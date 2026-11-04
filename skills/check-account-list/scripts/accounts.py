"""Load a company list, load each website, verify quotes and build the report for check-account-list.

Standard library only, so it runs wherever Python 3.10 or later does.

    python3 accounts.py load <list file> <out companies.md>
    python3 accounts.py web <companies.md> <out web.md>
    python3 accounts.py split <companies.md> <web.md> <out folder> [--size 10]
    python3 accounts.py verify <run folder> <record file> [<record file> ...]
    python3 accounts.py strip <run folder> <record file> <out to-check file>
    python3 accounts.py report <run folder> [--unchecked]
"""

from __future__ import annotations

import csv
import hashlib
import html
import http.client
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree

VERDICTS = ("keep", "drop", "check-by-hand")
PROBLEMS = (
    "wrong-website",
    "closed",
    "bought",
    "not-in-country",
    "wrong-size",
    "wrong-fit",
    "competitor",
    "customer",
    "duplicate",
)
CHECKS = ("website", "trading", "owner", "size", "fit", "conflict")
# A keep needs evidence for each of these. Size can be waived with "Size: not needed".
KEEP_NEEDS = ("website", "trading", "owner", "size", "fit")
# The evidence checks that can back each problem type. A customer named in the profile and a
# duplicate of another row rest on the profile and the list, which have no page to quote.
PROBLEM_EVIDENCE = {
    "wrong-website": ("website",),
    "closed": ("trading",),
    "bought": ("owner",),
    "not-in-country": ("trading", "owner", "website"),
    "wrong-size": ("size",),
    "wrong-fit": ("fit",),
    "competitor": ("fit", "conflict", "website"),
}
MAX_COMPANIES = 50

# Company websites often turn away anything that does not look like a browser. ADR 0004 allows this.
BROWSER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
# Seconds between two requests to the same site, so no site sees more than a person clicking through.
PAUSE = 2.0
# Official company registers get a longer pause. The script loads a register page only when a record
# cites it, once, to check the quote (ADR 0013), and stops using a register that refuses it.
REGISTER_PAUSE = 5.0
REGISTER_SITES = (
    "company-information.service.gov.uk",
    "brreg.no",
    "api.gouv.fr",
    "data.gouv.fr",
    "cro.ie",
    "sec.gov",
    "ised-isde.canada.ca",
    "registreentreprises.gouv.qc.ca",
    "asic.gov.au",
    "abr.business.gov.au",
    "companiesoffice.govt.nz",
    "bizfile.gov.sg",
    "mca.gov.in",
    "handelsregister.de",
    "unternehmensregister.de",
    "kvk.nl",
    "economie.fgov.be",
    "nbb.be",
    "boe.es",
    "registroimprese.it",
    "zefix.admin.ch",
    "virk.dk",
    "bolagsverket.se",
    "prh.fi",
    "ytj.fi",
    "rik.ee",
    "ms.gov.pl",
    "ares.gov.cz",
    "registeruz.sk",
    "e-justice.europa.eu",
)
TIMEOUT = 20


class FormatError(ValueError):
    """A file that does not follow the format the skill expects."""


# ---------------------------------------------------------------- fetching


@dataclass
class Page:
    url: str
    status: int = 0
    final: str = ""
    kind: str = ""
    text: str = ""
    error: str = ""


_last_request: dict[str, float] = {}


def is_register(host: str) -> bool:
    return any(host == site or host.endswith("." + site) for site in REGISTER_SITES)


def pace(host: str, now=time.monotonic, sleep=time.sleep) -> None:
    """Wait until the pause for this host has passed since the last request to it."""
    last = _last_request.get(host)
    if last is not None:
        wait = (REGISTER_PAUSE if is_register(host) else PAUSE) - (now() - last)
        if wait > 0:
            sleep(wait)
    _last_request[host] = now()


def fetch(url: str) -> Page:
    """Load one page. Never raises: a failure is recorded on the page."""
    pace(domain_of(url))
    request = urllib.request.Request(url, headers={"User-Agent": BROWSER_AGENT, "Accept-Language": "en-GB,en"})
    page = Page(url=url)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            page.status = response.status
            page.final = response.geturl()
            page.kind = response.headers.get_content_type()
            try:
                raw = response.read(5_000_000)
            except http.client.IncompleteRead as partial:
                raw = partial.partial
            charset = response.headers.get_content_charset() or "utf-8"
            if page.kind != "application/pdf":
                try:
                    page.text = raw.decode(charset, errors="replace")
                except LookupError:
                    # A charset Python does not know, such as "utf8mb4": read it as UTF-8.
                    page.text = raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        page.status = error.code
        page.final = error.geturl() or url
        page.error = f"HTTP {error.code}"
    except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as error:
        reason = getattr(error, "reason", error)
        page.error = str(reason)[:120] or type(error).__name__
    return page


# ---------------------------------------------------------------- the list


@dataclass
class Company:
    id: str
    name: str
    website: str = ""


NAME_HEADERS = ("company name", "company", "account name", "account", "organisation", "organization", "business", "name")
SITE_HEADERS = ("website", "domain", "company domain", "url", "site", "web")
# Words that mark a header as a website column when no header matches exactly, such as "Website URL".
SITE_WORDS = ("website", "domain", "url")
NAME_WORDS = ("company", "account", "organisation", "organization", "business", "name")
LIST_PREFIX = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s*")
# The first label has two or more characters, so "S.A." and "p.l.c." are not read as websites.
DOMAIN = re.compile(r"(?:https?://)?(?:www\.)?([a-z0-9][a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,})(/\S*)?", re.IGNORECASE)


def domain_of(value: str) -> str:
    """The bare host of a website, lower case, without www."""
    value = value.strip().strip("<>()[]").strip()
    if not value:
        return ""
    if "://" not in value:
        value = "https://" + value
    host = (urllib.parse.urlparse(value).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def pick(headers: list[str], wanted: tuple[str, ...], words: tuple[str, ...] = (), skip: int | None = None) -> int | None:
    """The column whose header is one of `wanted`, or failing that contains one of `words`."""
    clean = [h.strip().lower() for h in headers]
    for name in wanted:
        if name in clean and clean.index(name) != skip:
            return clean.index(name)
    for word in words:
        for i, header in enumerate(clean):
            if i != skip and word in header.split() + [header]:
                return i
    return None


def header_columns(row: list[str]) -> tuple[int | None, int | None]:
    """(name column, website column) if this row is a header row. Headers are matched exactly, and by a
    word in them ("Website URL") only when no cell in the row looks like a website, as a data row's would."""
    exact_only = any(DOMAIN.fullmatch(c.strip()) for c in row)
    site_col = pick(row, SITE_HEADERS, () if exact_only else SITE_WORDS)
    name_col = pick(row, NAME_HEADERS, () if exact_only else NAME_WORDS, skip=site_col)
    return name_col, site_col


def rows_to_companies(rows: list[list[str]]) -> list[tuple[str, str]]:
    rows = [r for r in rows if any(c.strip() for c in r)]
    if not rows:
        return []
    name_col, site_col = header_columns(rows[0])
    if name_col is None and site_col is not None:
        # A header row with a website column but no name header we know: the first other column holds the names.
        name_col = next(i for i in range(len(rows[0]) + 1) if i != site_col)
    if name_col is not None:
        body = rows[1:]
    else:
        name_col, body = 0, rows
        if site_col is None and len(rows[0]) > 1 and all(DOMAIN.fullmatch(r[1].strip()) for r in rows if len(r) > 1 and r[1].strip()):
            site_col = 1
    out = []
    for row in body:
        name = row[name_col].strip() if name_col < len(row) else ""
        site = row[site_col].strip() if site_col is not None and site_col < len(row) else ""
        if name:
            out.append((name, site))
    return out


def xlsx_rows(path: Path) -> list[list[str]]:
    """The first sheet of an Excel file, as rows of text."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(path) as book:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in book.namelist():
            root = ElementTree.fromstring(book.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", ns):
                shared.append("".join(t.text or "" for t in item.iter(f"{{{ns['m']}}}t")))
        sheets = sorted(n for n in book.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n))
        if not sheets:
            raise FormatError(f"{path.name}: no worksheet found")
        root = ElementTree.fromstring(book.read(sheets[0]))
    rows = []
    for row in root.iter(f"{{{ns['m']}}}row"):
        cells: dict[int, str] = {}
        for cell in row.findall("m:c", ns):
            ref = re.match(r"([A-Z]+)", cell.get("r", "A"))
            col = 0
            for letter in ref.group(1) if ref else "A":
                col = col * 26 + ord(letter) - 64
            kind = cell.get("t")
            value = cell.find("m:v", ns)
            if kind == "s" and value is not None:
                text = shared[int(value.text or 0)]
            elif kind == "inlineStr":
                text = "".join(t.text or "" for t in cell.iter(f"{{{ns['m']}}}t"))
            else:
                text = value.text if value is not None and value.text else ""
            cells[col - 1] = text
        if cells:
            rows.append([cells.get(i, "") for i in range(max(cells) + 1)])
    return rows


MD_DIVIDER = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?$")


def markdown_rows(text: str) -> list[list[str]] | None:
    lines = [l.strip() for l in text.splitlines() if l.strip().startswith("|")]
    if len(lines) < 2:
        # A table written without the outer pipes still has a divider row such as "--- | ---".
        all_lines = [l.strip() for l in text.splitlines()]
        if not any(MD_DIVIDER.match(l) for l in all_lines):
            return None
        lines = [l for l in all_lines if "|" in l]
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        rows.append([re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", c).strip("*` ") for c in cells])
    return rows


def plain_rows(text: str) -> list[list[str]]:
    """One company per line: "Name", "Name, site.com", "Name - site.com" or "1. Name (site.com)"."""
    rows = []
    for line in text.splitlines():
        line = LIST_PREFIX.sub("", line).strip()
        line = re.sub(r"\[([^\]]*)\]\(([^)]*)\)", r"\1 \2", line).replace("**", "").strip()
        if not line or line.startswith("#"):
            continue
        found = None
        for match in DOMAIN.finditer(line):
            found = match
        if found and found.start() > 0:
            name = line[: found.start()].rstrip(" ,;:-|(\t").strip()
            if name:
                rows.append([name, found.group(0).rstrip(").,")])
                continue
        rows.append([line, ""])
    return rows


def read_list(path: Path) -> list[tuple[str, str]]:
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return rows_to_companies(xlsx_rows(path))
    if suffix in (".xls", ".numbers", ".pdf", ".docx"):
        raise FormatError(f"{path.name}: save it as .csv or .xlsx, or paste the list")
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    if not text.strip():
        return []
    first = text.strip().splitlines()[0]
    delimiter = max(",;\t", key=first.count)
    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter)) if first.count(delimiter) else []
    has_header = bool(rows) and header_columns(rows[0]) != (None, None)
    # A .csv is read as columns. Other text only when its first line is a header we know,
    # so "Acme, Inc." on a line of its own stays one name.
    if rows and (suffix in (".csv", ".tsv") or (has_header and "|" not in first)):
        return rows_to_companies(rows)
    table = markdown_rows(text)
    if table:
        return rows_to_companies(table)
    return rows_to_companies(plain_rows(text))


def write_companies(companies: list[Company]) -> str:
    out = ["| ID | Company | Website given |", "|---|---|---|"]
    for c in companies:
        out.append(f"| {c.id} | {c.name.replace('|', '/')} | {c.website} |")
    return "\n".join(out) + "\n"


def read_companies(path: Path) -> list[Company]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and re.fullmatch(r"A\d{2,3}", cells[0]):
            out.append(Company(cells[0], cells[1], cells[2]))
    if not out:
        raise FormatError(f"{path.name}: no companies found")
    return out


def load(source: Path, out: Path) -> list[str]:
    pairs = read_list(source)
    if not pairs:
        raise FormatError(f"{source.name}: no company names found")
    width = 3 if len(pairs) > 99 else 2
    companies = [Company(f"A{n:0{width}d}", name, domain_of(site)) for n, (name, site) in enumerate(pairs, 1)]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(write_companies(companies), encoding="utf-8")
    notes = [f"{len(companies)} companies, {sum(1 for c in companies if c.website)} with a website"]
    if len(companies) > MAX_COMPANIES:
        notes.append(f"over {MAX_COMPANIES}: run it in parts")
    seen: dict[str, str] = {}
    pairs_noted: set[tuple[str, str]] = set()
    for c in companies:
        name_key = re.sub(r"\W+", "", re.sub(r"\b(ltd|limited|plc|inc|llc)\b", "", c.name.lower()))
        for key in filter(None, (c.website, name_key)):
            if key in seen and (seen[key], c.id) not in pairs_noted:
                pairs_noted.add((seen[key], c.id))
                notes.append(f"possible duplicate: {seen[key]} and {c.id} ({key})")
            seen.setdefault(key, c.id)
    return notes


# ---------------------------------------------------------------- websites


TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


@dataclass
class SiteResult:
    id: str
    name: str
    given: str
    status: str
    final: str
    moved: str
    title: str


def check_site(company: Company, get=fetch) -> SiteResult:
    if not company.website:
        return SiteResult(company.id, company.name, "", "no website given", "", "", "")
    tries = [f"https://{company.website}", f"https://www.{company.website}", f"http://{company.website}"]
    page = None
    for url in tries:
        page = get(url)
        if page.status and page.status < 400:
            break
    assert page is not None
    final_host = domain_of(page.final) if page.final else ""
    if page.status and page.status < 400:
        status = f"loads ({page.status})"
    elif page.status:
        status = f"error {page.status}"
    else:
        status = f"does not load: {page.error}"
    moved = ""
    same_site = final_host.endswith("." + company.website) or company.website.endswith("." + final_host)
    if final_host and final_host != company.website and not same_site:
        moved = f"redirects to another domain: {final_host}"
    title = ""
    match = TITLE.search(page.text or "")
    if match:
        title = " ".join(html.unescape(match.group(1)).split())[:100]
    return SiteResult(company.id, company.name, company.website, status, page.final, moved, title)


def write_sites(results: list[SiteResult]) -> str:
    out = ["| ID | Company | Website given | Result | Lands on | Note | Page title |", "|---|---|---|---|---|---|---|"]
    for r in results:
        cells = [r.id, r.name, r.given, r.status, r.final, r.moved, r.title]
        out.append("| " + " | ".join(c.replace("|", "/") for c in cells) + " |")
    return "\n".join(out) + "\n"


def read_sites(path: Path) -> dict[str, str]:
    """Each company's line from web.md, by ID."""
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\|\s*(A\d{2,3})\s*\|", line)
        if match:
            out[match.group(1)] = line
    return out


def web(companies_path: Path, out: Path, get=fetch) -> list[str]:
    results = [check_site(c, get) for c in read_companies(companies_path)]
    out.write_text(write_sites(results), encoding="utf-8")
    loads = sum(1 for r in results if r.status.startswith("loads"))
    moved = [r for r in results if r.moved]
    notes = [f"{len(results)} websites: {loads} load, {len(results) - loads} do not or none given, {len(moved)} redirect elsewhere"]
    notes += [f"{r.id} {r.name}: {r.moved}" for r in moved]
    return notes


def split(companies_path: Path, sites_path: Path, folder: Path, size: int = 10) -> list[str]:
    companies = read_companies(companies_path)
    sites = read_sites(sites_path)
    folder.mkdir(parents=True, exist_ok=True)
    header = "| ID | Company | Website given | Result | Lands on | Note | Page title |\n|---|---|---|---|---|---|---|"
    notes = []
    for start in range(0, len(companies), size):
        group = companies[start : start + size]
        n = start // size + 1
        lines = [header] + [sites.get(c.id, f"| {c.id} | {c.name} | {c.website} | not loaded | | | |") for c in group]
        path = folder / f"batch-{n}.md"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        notes.append(f"{path.name}: {group[0].id} to {group[-1].id}")
    return notes


# ---------------------------------------------------------------- page text


def page_text(raw: str) -> str:
    """Visible text of an HTML page, in reading order, with blocks on their own lines."""
    raw = re.sub(r"(?is)<(script|style|noscript|template)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?is)<!--.*?-->", " ", raw)
    raw = re.sub(r"(?i)<(br|/p|/div|/li|/tr|/h\d|/dd|/dt|/td|/th)[^>]*>", "\n", raw)
    raw = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    lines = (" ".join(l.split()) for l in raw.splitlines())
    return "\n".join(l for l in lines if l)


# ---------------------------------------------------------------- records


@dataclass
class Evidence:
    ref: str
    check: str
    url: str
    quote: str
    line: int


@dataclass
class Record:
    id: str
    name: str
    fields: dict[str, str] = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)
    line: int = 0
    source: str = ""

    @property
    def verdict(self) -> str:
        return self.fields.get("verdict", "").strip().lower()

    @property
    def problems(self) -> list[str]:
        value = self.fields.get("problems", "").strip().lower()
        if value in ("", "none", "-"):
            return []
        return [p.strip() for p in value.split(",") if p.strip()]


HEADING = re.compile(r"^##\s+(A\d{2,3})\s*\|\s*(.+?)\s*$")
FIELD = re.compile(r"^-\s+([A-Za-z][A-Za-z ]*?):\s*(.*)$")
EVIDENCE = re.compile(r'^\s+-\s+([EC]\d+)\s*\|\s*([a-z]+)\s*\|\s*(\S+)\s*\|\s*"(.*)"\s*$')


def parse_records(text: str, source: str = "") -> list[Record]:
    records: list[Record] = []
    current: Record | None = None
    in_evidence = False
    for number, raw in enumerate(text.splitlines(), 1):
        heading = HEADING.match(raw)
        if heading:
            current = Record(heading.group(1), heading.group(2), line=number, source=source)
            records.append(current)
            in_evidence = False
            continue
        if current is None:
            continue
        if raw.startswith("## "):
            raise FormatError(f"{source}:{number}: a heading must be '## A01 | Company name'")
        match = FIELD.match(raw)
        if match:
            key = match.group(1).strip().lower()
            in_evidence = key in ("evidence", "check evidence")
            if not in_evidence:
                current.fields[key] = match.group(2).strip()
            continue
        if in_evidence and raw.strip():
            item = EVIDENCE.match(raw)
            if not item:
                raise FormatError(f'{source}:{number}: evidence lines are "  - E1 | check | url | \\"quote\\""')
            current.evidence.append(Evidence(item.group(1), item.group(2), item.group(3), item.group(4), number))
    return records


def read_records(path: Path) -> list[Record]:
    return parse_records(path.read_text(encoding="utf-8"), path.name)


def check_record(record: Record, size_limit: bool = True) -> list[str]:
    """Problems with one record's shape. `size_limit` is False when the profile sets no staff range."""
    where = f"{record.source}:{record.line} {record.id}"
    problems = []
    if record.verdict not in VERDICTS:
        problems.append(f"{where}: verdict must be one of {', '.join(VERDICTS)}")
    unknown = [p for p in record.problems if p not in PROBLEMS]
    if unknown:
        problems.append(f"{where}: unknown problem types {', '.join(unknown)}")
    if record.verdict == "drop" and not record.problems:
        problems.append(f"{where}: a drop needs at least one problem type")
    if record.verdict == "keep" and record.problems:
        problems.append(f"{where}: a keep cannot carry problem types")
    if record.verdict == "check-by-hand" and record.problems:
        problems.append(f"{where}: check-by-hand means no problem is proven, so it cannot carry problem types")
    if not record.fields.get("reason"):
        problems.append(f"{where}: no reason line")
    for item in record.evidence:
        if item.check not in CHECKS:
            problems.append(f"{where} {item.ref}: check must be one of {', '.join(CHECKS)}")
        if not item.url.startswith(("http://", "https://")):
            problems.append(f"{where} {item.ref}: not a web address")
        if len(item.quote.split()) < 2:
            problems.append(f"{where} {item.ref}: quote at least two words")
    if record.verdict == "keep":
        have = {e.check for e in record.evidence}
        waived = record.fields.get("size", "").lower().startswith("not needed")
        if waived and size_limit:
            problems.append(f"{where}: size is 'not needed' only when the profile sets no staff range")
        needs = [c for c in KEEP_NEEDS if not (c == "size" and waived and not size_limit)]
        missing = [c for c in needs if c not in have]
        if missing:
            problems.append(f"{where}: a keep needs evidence for {', '.join(missing)}")
    if record.verdict == "drop":
        have = {e.check for e in record.evidence}
        dead_site = "not load" in record.fields.get("website", "").lower()
        for problem in record.problems:
            backing = PROBLEM_EVIDENCE.get(problem)
            if not backing or (problem == "wrong-website" and dead_site):
                continue
            if not have.intersection(backing):
                problems.append(f"{where}: {problem} needs evidence for {' or '.join(backing)}")
    return problems


# ---------------------------------------------------------------- quote check


# Curly quotes, dashes and non-breaking spaces fold to plain ones. Built from code points so this
# file never contains the characters the repo bans.
FOLD = str.maketrans({chr(0x2018): "'", chr(0x2019): "'", chr(0x201C): '"', chr(0x201D): '"', chr(0x2013): "-", chr(0x2014): "-", chr(0x00A0): " "})


def plain(text: str) -> str:
    text = text.translate(FOLD)
    return " ".join(text.lower().split())


def quote_on_page(quote: str, text: str) -> bool:
    """Whole words, in order, ignoring case, spacing and punctuation between words."""
    words = re.findall(r"[\w£$€%']+", plain(quote))
    if not words:
        return False
    pattern = r"(?<![\w'])" + r"[^\w£$€%']+".join(re.escape(w) for w in words) + r"(?![\w'])"
    return re.search(pattern, plain(text)) is not None


class PageCache:
    """Each page is loaded once per run and kept as text in working/pages/."""

    def __init__(self, folder: Path, get=fetch):
        self.folder = folder
        self.get = get
        self.refused: set[str] = set()
        folder.mkdir(parents=True, exist_ok=True)

    def text(self, url: str, fresh: bool = False) -> tuple[str, str]:
        """(state, text): state is "ok", "pdf" or "error: ...". A page that failed to load is not kept,
        so the next verify tries it again; `fresh` loads it again even when it is kept."""
        key = hashlib.sha1(url.encode()).hexdigest()[:16]
        path = self.folder / f"{key}.json"
        if path.is_file() and not fresh:
            saved = json.loads(path.read_text(encoding="utf-8"))
            return saved["state"], saved["text"]
        parts = urllib.parse.urlparse(url)
        if parts.path.lower().endswith(".pdf") or "format=pdf" in parts.query:
            # The script cannot read a PDF, so it does not download one just to say so.
            return "pdf", ""
        host = domain_of(url)
        if host in self.refused:
            return "error: the register refused an earlier request, so it was not asked again", ""
        page = self.get(url)
        if is_register(host) and page.status in (403, 429):
            self.refused.add(host)
        if page.error and not page.text:
            state, text = f"error: {page.error}", ""
        elif page.kind == "application/pdf" or url.split("?")[0].endswith(".pdf"):
            state, text = "pdf", ""
        else:
            state, text = "ok", page_text(page.text)
        if not state.startswith("error"):
            path.write_text(json.dumps({"url": url, "state": state, "text": text}), encoding="utf-8")
        return state, text


def sets_staff_range(profile: Path) -> bool:
    """True unless the profile says its staff range is "no limit". A run with no profile is held to a range."""
    if not profile.is_file():
        return True
    match = re.search(r"^- Staff range:\s*(.*)$", profile.read_text(encoding="utf-8"), re.MULTILINE)
    return not (match and match.group(1).strip().lower().startswith("no limit"))


def verify(run: Path, files: list[Path], get=fetch) -> tuple[list[str], dict[str, str]]:
    """Format problems, and each evidence item's state: verified, not-on-page, pdf or could-not-load."""
    problems: list[str] = []
    states: dict[str, str] = {}
    cache = PageCache(run / "working" / "pages", get)
    size_limit = sets_staff_range(run / "profile.md")
    for path in files:
        try:
            records = read_records(path)
        except FormatError as error:
            problems.append(str(error))
            continue
        if not records:
            problems.append(f"{path.name}: no records")
        for record in records:
            problems += check_record(record, size_limit)
            for item in record.evidence:
                state, text = cache.text(item.url)
                if state == "ok":
                    found = quote_on_page(item.quote, text)
                    if not found:
                        # Some pages change between loads (rotating banners, news), so look once more.
                        state, text = cache.text(item.url, fresh=True)
                        found = state == "ok" and quote_on_page(item.quote, text)
                    result = "verified" if found else "not-on-page"
                elif state == "pdf":
                    result = "pdf"
                else:
                    result = "could-not-load"
                states[f"{path.name}|{record.id}|{item.ref}"] = result
                if result == "not-on-page":
                    problems.append(f"{path.name}:{item.line} {record.id} {item.ref}: quote not found on {item.url}")
    store = run / "working" / "evidence.json"
    saved = json.loads(store.read_text(encoding="utf-8")) if store.is_file() else {}
    saved.update(states)
    store.write_text(json.dumps(saved, indent=1, sort_keys=True), encoding="utf-8")
    return problems, states


def evidence_states(run: Path) -> dict[str, str]:
    store = run / "working" / "evidence.json"
    return json.loads(store.read_text(encoding="utf-8")) if store.is_file() else {}


def needs_check(record: Record, source: str, states: dict[str, str]) -> bool:
    """Every keep, and every drop resting on evidence the script could not confirm."""
    if record.verdict == "keep":
        return True
    if record.verdict == "drop":
        return any(states.get(f"{source}|{record.id}|{e.ref}") != "verified" for e in record.evidence) or not record.evidence
    return False


CLAIM_FIELDS = ("website", "registered", "owner", "size", "fit", "conflicts", "verdict", "problems")


def strip(run: Path, source: Path, out: Path) -> int:
    """Write the records the checker must see: claims only, never the reasons or the evidence."""
    states = evidence_states(run)
    picked = [r for r in read_records(source) if needs_check(r, source.name, states)]
    lines = []
    for record in picked:
        lines.append(f"## {record.id} | {record.name}")
        given = record.fields.get("website given")
        if given:
            lines.append(f"- Website given: {given}")
        for key in CLAIM_FIELDS:
            if key in record.fields:
                lines.append(f"- {key.capitalize()}: {record.fields[key]}")
        lines.append("")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return len(picked)


# ---------------------------------------------------------------- report


def merged(run: Path) -> tuple[list[Record], dict[str, Record], dict[str, str]]:
    research: list[Record] = []
    for path in sorted((run / "working").glob("research-*.md"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0)):
        research += read_records(path)
    checks: dict[str, Record] = {}
    for path in sorted((run / "working").glob("check-*.md")):
        for record in read_records(path):
            checks[record.id] = record
    return research, checks, evidence_states(run)


def csv_text(rows: list[dict[str, str]], columns: list[str]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in columns})
    return buffer.getvalue()


# A company number as registers print it: 8 digits or two letters and 6 (UK), 9 digits (Norway, France's SIREN).
COMPANY_NUMBER = re.compile(r"\b(?:[A-Z]{2}\d{6}|\d{8,9})\b")
UNCHECKED = "Not checked: these verdicts are the first pass only, and no separate check tried to prove them wrong."


def sent_to_checker(run: Path) -> set[str]:
    ids: set[str] = set()
    for path in (run / "check-in").glob("to-check-*.md"):
        ids.update(m.group(1) for m in re.finditer(r"^##\s+(A\d{2,3})\s*\|", path.read_text(encoding="utf-8"), re.MULTILINE))
    return ids


def changed(first: Record | None, check: Record | None) -> str:
    """How the checker changed the first pass, in words, or "" if it did not."""
    if not first or not check:
        return ""
    if first.verdict != check.verdict:
        return f"changed it, was {first.verdict}" + (f" ({', '.join(first.problems)})" if first.problems else "")
    if sorted(first.problems) != sorted(check.problems):
        return f"kept it a {check.verdict}, changed the problems, were {', '.join(first.problems) or 'none'}"
    return ""


def report(run: Path, today: str | None = None, unchecked: bool = False) -> list[str]:
    today = today or time.strftime("%Y-%m-%d")
    companies = read_companies(run / "companies.md")
    research, checks, states = merged(run)
    by_id = {r.id: r for r in research}
    notes = []
    missing = [c.id for c in companies if c.id not in by_id]
    if missing:
        notes.append(f"no record for {', '.join(missing)}")
    final: list[tuple[Company, Record | None, Record | None]] = []
    for company in companies:
        first = by_id.get(company.id)
        check = checks.get(company.id)
        final.append((company, first, check))

    def outcome(first: Record | None, check: Record | None) -> Record | None:
        return check or first

    verdicts = Counter()
    problem_counts = Counter()
    overturned = 0
    for _, first, check in final:
        record = outcome(first, check)
        if record is None:
            verdicts["no record"] += 1
            continue
        verdicts[record.verdict] += 1
        problem_counts.update(record.problems)
        if changed(first, check):
            overturned += 1

    def state_of(record: Record, item: Evidence) -> str:
        for path_key in [k for k in states if k.endswith(f"|{record.id}|{item.ref}")]:
            if path_key.startswith(record.source + "|"):
                return states[path_key]
        return "not verified"

    lost = sorted(sent_to_checker(run) - set(checks))
    if lost:
        notes.append(f"sent to the checker but no record came back: {', '.join(lost)}")
    numbers: dict[str, list[str]] = {}
    for company, first, check in final:
        record = outcome(first, check)
        if record:
            for number in set(COMPANY_NUMBER.findall(record.fields.get("registered", ""))):
                numbers.setdefault(number, []).append(company.id)
    same_number = {n: ids for n, ids in numbers.items() if len(ids) > 1}
    for number, ids in sorted(same_number.items()):
        notes.append(f"possible duplicate: {' and '.join(ids)} give the same company number, {number}")

    lines = ["# Account list check", ""] + ([UNCHECKED, ""] if unchecked else [])
    lines += [f"Checked {today}. {len(companies)} companies.", "", "## Counts", ""]
    lines += ["| Verdict | Companies |", "|---|---|"]
    for verdict in (*VERDICTS, "no record"):
        if verdicts[verdict]:
            lines.append(f"| {verdict} | {verdicts[verdict]} |")
    lines += ["", "| Problem | Companies |", "|---|---|"]
    for problem in PROBLEMS:
        if problem_counts[problem]:
            lines.append(f"| {problem} | {problem_counts[problem]} |")
    checked = sum(1 for _, _, c in final if c)
    lines += ["", f"The checker re-checked {checked} companies and changed {overturned} verdicts or problem lists."]
    if lost:
        lines.append(f"Sent to the checker but no record came back, so these show the first pass only: {', '.join(lost)}.")
    for number, ids in sorted(same_number.items()):
        lines.append(f"Possible duplicate: {' and '.join(ids)} give the same company number, {number}. Check whether they are one company.")
    counts = Counter(states.values())
    unconfirmed = counts["pdf"] + counts["could-not-load"] + counts["not-on-page"]
    sizes = sum(1 for _, f, k in final if outcome(f, k) and outcome(f, k).fields.get("size", "").lower().startswith("unverified"))
    lines += ["", f"Quotes confirmed by the script: {counts['verified']}. Not confirmed by the script: {unconfirmed} ({counts['pdf']} in PDFs, {counts['could-not-load']} on pages that would not load, {counts['not-on-page']} not found). Companies with size unverified: {sizes}.", ""]
    by_hand = [(c, outcome(f, k)) for c, f, k in final if outcome(f, k) and outcome(f, k).verdict == "check-by-hand"]
    lines += ["## Check by hand", ""]
    lines += [f"- **{c.id} {c.name}**: {r.fields.get('reason', '')}" for c, r in by_hand] or ["Nothing."]
    lines += ["", "## Every company", ""]
    rows = []
    for company, first, check in final:
        record = outcome(first, check)
        if record is None:
            lines += [f"### {company.id} | {company.name}", "", "No record. Not checked.", ""]
            rows.append({"id": company.id, "company": company.name, "website_given": company.website, "verdict": "not checked"})
            continue
        lines.append(f"### {company.id} | {company.name}: {record.verdict}")
        lines.append("")
        if record.problems:
            lines.append(f"- Problems: {', '.join(record.problems)}")
        lines.append(f"- Reason: {record.fields.get('reason', '')}")
        for key in ("website", "registered", "owner", "size", "fit", "conflicts"):
            if record.fields.get(key):
                lines.append(f"- {key.capitalize()}: {record.fields[key]}")
        note = check.fields.get("check notes", "") if check else ""
        if check:
            what = changed(first, check) or "agreed"
            if note.lower().startswith("agreed"):
                note = note[len("agreed"):].lstrip(" :.,")
            lines.append(f"- Checker: {what}" + (f". {note}" if note else ""))
        evidence = (first.evidence if first else []) + (check.evidence if check else [])
        for holder, label in ((check, "the checker's"), (first, "the first pass's")):
            if holder and holder.evidence:
                lines.append(f"- Evidence, {label}:" if check else "- Evidence:")
                for item in holder.evidence:
                    lines.append(f'  - {item.ref} {item.check}: {item.url} "{item.quote}" ({state_of(holder, item)})')
        lines.append("")
        rows.append({
            "id": company.id,
            "company": company.name,
            "website_given": company.website,
            "verdict": record.verdict,
            "problems": "; ".join(record.problems),
            "reason": record.fields.get("reason", ""),
            "website": record.fields.get("website", ""),
            "registered": record.fields.get("registered", ""),
            "owner": record.fields.get("owner", ""),
            "size": record.fields.get("size", ""),
            "fit": record.fields.get("fit", ""),
            "conflicts": record.fields.get("conflicts", ""),
            "rechecked": "yes" if check else "no",
            "checker_note": changed(first, check) or (note if check else ""),
            "evidence": " ".join(dict.fromkeys(e.url for e in evidence)),
            "checked_on": today,
        })
    columns = ["id", "company", "website_given", "verdict", "problems", "reason", "website", "registered", "owner", "size", "fit", "conflicts", "rechecked", "checker_note", "evidence", "checked_on"]
    (run / "checks.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    (run / "checked.csv").write_text(csv_text(rows, columns), encoding="utf-8")
    (run / "keepers.csv").write_text(csv_text([r for r in rows if r.get("verdict") == "keep"], columns), encoding="utf-8")
    summary = ", ".join(f"{verdicts[v]} {v}" for v in (*VERDICTS, "no record") if verdicts[v])
    notes.insert(0, f"{len(companies)} companies: {summary}")
    if problem_counts:
        notes.append("problems: " + ", ".join(f"{problem_counts[p]} {p}" for p in PROBLEMS if problem_counts[p]))
    notes.append(f"checker re-checked {checked}, changed {overturned}")
    return notes


# ---------------------------------------------------------------- command line


def main(argv: list[str]) -> int:
    usage = __doc__.strip().split("\n\n")[2]
    if not argv:
        print(usage, file=sys.stderr)
        return 2
    command, args = argv[0], argv[1:]
    try:
        if command == "load" and len(args) == 2:
            print("\n".join(load(Path(args[0]), Path(args[1]))))
        elif command == "web" and len(args) == 2:
            print("\n".join(web(Path(args[0]), Path(args[1]))))
        elif command == "split" and (len(args) == 3 or (len(args) == 5 and args[3] == "--size" and args[4].isdigit() and int(args[4]) > 0)):
            size = int(args[4]) if len(args) == 5 else 10
            print("\n".join(split(Path(args[0]), Path(args[1]), Path(args[2]), size)))
        elif command == "verify" and len(args) >= 2:
            problems, states = verify(Path(args[0]), [Path(a) for a in args[1:]])
            counts = Counter(states.values())
            print("evidence: " + (", ".join(f"{n} {s}" for s, n in sorted(counts.items())) or "none"))
            if problems:
                print("\n".join(problems))
                return 1
            print("ok")
        elif command == "strip" and len(args) == 3:
            print(f"{strip(Path(args[0]), Path(args[1]), Path(args[2]))} records to check")
        elif command == "report" and len(args) in (1, 2) and args[1:] in ([], ["--unchecked"]):
            print("\n".join(report(Path(args[0]), unchecked=bool(args[1:]))))
        else:
            print(usage, file=sys.stderr)
            return 2
    except (FormatError, OSError, zipfile.BadZipFile, ElementTree.ParseError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
