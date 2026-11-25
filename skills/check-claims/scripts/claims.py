"""Number a draft, verify the claims and records, and build the report for check-claims.

Standard library only, so it runs wherever Python 3.10 or later does.

    python3 claims.py number <draft> <out draft-lines.md>
    python3 claims.py verify <run folder> --claims
    python3 claims.py verify <run folder> [<record file> ...]
    python3 claims.py report <run folder>
"""

from __future__ import annotations

import hashlib
import html
import http.client
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

VERDICTS = ("supported", "differs", "no-source", "could-not-open")
# The six problem types that say the draft departs from the first publisher's page.
DRAFT_SIDE = ("number-wrong", "base-dropped", "wrong-subject", "strength-changed", "source-mislabelled", "misquoted")
# The four that are about the source, and can sit on a supported claim.
SOURCE_SIDE = ("second-hand", "out-of-date", "publisher-disagrees", "page-gone")
# All ten, in the order the spec lists them.
PROBLEMS = (
    "second-hand",
    "number-wrong",
    "base-dropped",
    "wrong-subject",
    "strength-changed",
    "source-mislabelled",
    "misquoted",
    "out-of-date",
    "publisher-disagrees",
    "page-gone",
)
KINDS = ("statistic", "quotation", "company-fact", "event", "citation")
# What an evidence quote shows: the first publisher's words on the claim, or its newer figure or fact.
ROLES = ("page", "newer")
# Claims a run can trace, by route.
CAP_SUBAGENT = 40
CAP_CHAT = 15

# First publishers' sites often turn away anything that does not look like a browser. ADR 0004 allows this.
BROWSER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)
# Seconds between two requests to the same site, so no site sees more than a person clicking through.
PAUSE = 2.0
TIMEOUT = 20


class FormatError(ValueError):
    """A file that does not follow the format the skill expects."""


# ---------------------------------------------------------------- the draft

WORD_PARAGRAPH = re.compile(r"<w:p[ >].*?</w:p>|<w:p/>", re.DOTALL)
WORD_PIECE = re.compile(r"<w:t(?: [^>]*)?>([^<]*)</w:t>|<w:(tab|br|cr|noBreakHyphen)\b[^>]*/>")
# Text Word keeps twice (a moved passage's old place, a drawing's fallback) or outside the paragraph flow.
WORD_SKIP = re.compile(
    r"<w:moveFrom\b.*?</w:moveFrom>|<mc:Fallback\b.*?</mc:Fallback>|<w:txbxContent\b.*?</w:txbxContent>", re.DOTALL
)
TEXT_SUFFIXES = {".txt", ".md", ".markdown", ""}


def docx_text(path: Path) -> str:
    """The text of a Word file, read with the standard library. Each paragraph stands alone, so a
    heading or a list item is never joined to the paragraph after it."""
    try:
        with zipfile.ZipFile(path) as archive:
            raw = archive.read("word/document.xml")
        xml = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8")
    except (zipfile.BadZipFile, KeyError, UnicodeDecodeError) as error:
        raise FormatError(f"{path}: not a Word file this script can read ({error})") from error
    paragraphs = []
    for paragraph in WORD_PARAGRAPH.findall(WORD_SKIP.sub("", xml)):
        pieces = []
        for words, mark in WORD_PIECE.findall(paragraph):
            pieces.append(words if not mark else {"tab": "\t", "noBreakHyphen": "-"}.get(mark, "\n"))
        paragraphs.append(html.unescape("".join(pieces)))
    return "\n\n".join(paragraphs)


def read_draft(path: Path) -> str:
    """A draft file as text. Word files are unpacked; a PDF is refused with a way round it."""
    head = path.read_bytes()[:5]
    suffix = path.suffix.lower()
    if suffix == ".pdf" or head.startswith(b"%PDF"):
        raise FormatError(f"{path}: a PDF can't be read reliably. Save the draft as .docx, .txt or .md, or paste the text.")
    if suffix == ".docx":
        return docx_text(path)
    if suffix not in TEXT_SUFFIXES:
        raise FormatError(f"{path}: this skill reads .txt, .md and .docx. Save the draft as one of those, or paste the text.")
    return path.read_text(encoding="utf-8-sig", errors="replace")


HEADING_LINE = re.compile(r"^\s{0,3}#{1,6}\s+\S")
LIST_ITEM = re.compile(r"^\s*((?:[-*+\u2022]|\d+[.)]))\s+(\S.*)$")
RULE = re.compile(r"^\s*(?:[-*_=]\s*){3,}$")
TABLE_DIVIDER = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?$")
# Marks that can close a sentence after its full stop, and open the next one. The curly quotes are
# built from code points so this file never contains the characters the repo bans.
CLOSERS = "\"')]*_" + chr(0x2019) + chr(0x201D)
OPENERS = "\"'([*_" + chr(0x2018) + chr(0x201C)
BOUNDARY = re.compile(r"[.!?]+[" + re.escape(CLOSERS) + r"]*\s+")
# A full stop after one of these does not end a sentence.
ABBREVIATIONS = {
    "mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc", "inc", "ltd", "co", "corp",
    "fig", "approx", "est", "e.g", "i.e", "a.m", "p.m", "u.s", "u.k",
}


def squash(text: str) -> str:
    return " ".join(text.split())


def split_sentences(text: str) -> list[str]:
    """The sentences of one paragraph, each kept exactly as written."""
    out: list[str] = []
    start = 0
    for match in BOUNDARY.finditer(text):
        rest = text[match.end():].lstrip(OPENERS)
        if not rest or not (rest[0].isupper() or rest[0].isdigit() or rest[0] in "$\u00a3\u20ac["):
            continue
        stops = match.group().rstrip().rstrip(CLOSERS)
        if stops == ".":
            word = re.search(r"([A-Za-z][A-Za-z.]*)$", text[start:match.start()])
            if word and (word.group(1).lower() in ABBREVIATIONS or (len(word.group(1)) == 1 and word.group(1).isupper())):
                continue
        out.append(text[start:match.end()].strip())
        start = match.end()
    tail = text[start:].strip()
    if tail:
        out.append(tail)
    return out


def number(text: str) -> list[str]:
    """Every sentence of the draft, in order. A heading or a table row is one sentence. A list item
    keeps its marker and is split like a paragraph. Lines with no blank line between them are one
    paragraph, as in Markdown, so hard-wrapped text is not cut mid-sentence."""
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    sentences: list[str] = []
    marker = ""
    paragraph: list[str] = []

    def flush() -> None:
        nonlocal marker, paragraph
        parts = split_sentences(squash(" ".join(paragraph)))
        if parts:
            parts[0] = marker + parts[0]
            sentences.extend(parts)
        marker, paragraph = "", []

    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip() or RULE.match(line) or line.strip().startswith("```"):
            flush()
            continue
        if HEADING_LINE.match(line):
            flush()
            sentences.append(squash(line))
            continue
        if line.lstrip().startswith("|"):
            flush()
            if not TABLE_DIVIDER.match(line.strip()):
                sentences.append(squash(line))
            continue
        item = LIST_ITEM.match(line)
        if item:
            flush()
            marker, paragraph = item.group(1) + " ", [item.group(2)]
            continue
        paragraph.append(line.strip())
    flush()
    return sentences


def write_lines(sentences: list[str]) -> str:
    return "".join(f"[S{n}] {text}\n" for n, text in enumerate(sentences, 1))


NUMBERED = re.compile(r"^\[S(\d+)\] (.*)$")


def read_lines(path: Path) -> dict[int, str]:
    """The numbered draft, by sentence number."""
    out: dict[int, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = NUMBERED.match(line)
        if match:
            out[int(match.group(1))] = match.group(2)
    if not out:
        raise FormatError(f"{path.name}: no numbered sentences found")
    return out


# ---------------------------------------------------------------- claims


@dataclass
class Claim:
    id: str
    sentence: int
    kind: str
    fields: dict[str, str] = field(default_factory=dict)
    line: int = 0

    @property
    def text(self) -> str:
        return self.fields.get("claim", "").strip()

    @property
    def words(self) -> str:
        return unquote(self.fields.get("draft words", ""))

    @property
    def source(self) -> str:
        return self.fields.get("source given", "").strip() or "none"

    @property
    def trace(self) -> str:
        """"yes", "own-company", "named-person", or "" when the Trace line is missing or unreadable."""
        value = self.fields.get("trace", "").strip().lower()
        if value.startswith("yes"):
            return "yes"
        if value.startswith("no") and "own company" in value:
            return "own-company"
        if value.startswith("no") and "named person" in value:
            return "named-person"
        return ""


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1]
    return value


CLAIM_HEADING = re.compile(r"^##\s+(C\d+)\s*\|\s*S(\d+)\s*\|\s*([A-Za-z-]+)\s*$")
NO_CLAIM = re.compile(r"^(?:[-*]\s+)?no claim\s*:\s*(.*)$", re.IGNORECASE)
SENTENCE_REF = re.compile(r"^S(\d+)(?:\s*-\s*S?(\d+))?$")
FIELD = re.compile(r"^-\s+([A-Za-z][A-Za-z ]*?):\s*(.*)$")


def parse_claims(text: str, source: str = "claims.md") -> tuple[list[Claim], dict[int, int]]:
    """(claims, sentences marked no claim with the line each mark is on)."""
    claims: list[Claim] = []
    no_claim: dict[int, int] = {}
    current: Claim | None = None
    for number_, raw in enumerate(text.splitlines(), 1):
        mark = NO_CLAIM.match(raw.strip())
        if mark:
            current = None
            for token in filter(None, (t.strip() for t in mark.group(1).split(","))):
                ref = SENTENCE_REF.match(token)
                if not ref or (ref.group(2) and int(ref.group(2)) < int(ref.group(1))):
                    raise FormatError(f"{source}:{number_}: '{token}' is not a sentence or a range, such as S3 or S3-S6")
                for n in range(int(ref.group(1)), int(ref.group(2) or ref.group(1)) + 1):
                    no_claim.setdefault(n, number_)
            continue
        if raw.startswith("## "):
            heading = CLAIM_HEADING.match(raw)
            if not heading:
                raise FormatError(f"{source}:{number_}: a claim heading must be '## C01 | S12 | statistic'")
            current = Claim(heading.group(1), int(heading.group(2)), heading.group(3).lower(), line=number_)
            claims.append(current)
            continue
        match = FIELD.match(raw)
        if match and current is not None:
            current.fields[match.group(1).strip().lower()] = match.group(2).strip()
    return claims, no_claim


def read_claims(path: Path) -> tuple[list[Claim], dict[int, int]]:
    return parse_claims(path.read_text(encoding="utf-8"), path.name)


def check_claims(sentences: dict[int, str], claims: list[Claim], no_claim: dict[int, int], source: str = "claims.md") -> list[str]:
    """Stage 4's coverage rule for the reader's file: every sentence has a claim or a no claim mark."""
    problems = []
    with_claim: dict[int, str] = {}
    seen: set[str] = set()
    for claim in claims:
        where = f"{source}:{claim.line} {claim.id}"
        if claim.id in seen:
            problems.append(f"{where}: this claim number is used twice")
        seen.add(claim.id)
        if claim.sentence not in sentences:
            problems.append(f"{where}: S{claim.sentence} is not a sentence in the numbered draft")
        else:
            with_claim.setdefault(claim.sentence, claim.id)
        if claim.kind not in KINDS:
            problems.append(f"{where}: kind must be one of {', '.join(KINDS)}")
        if not claim.text:
            problems.append(f"{where}: no Claim line")
        if not claim.trace:
            problems.append(f"{where}: the Trace line must be 'yes', 'no, own company' or 'no, named person'")
    for n in sorted(no_claim):
        if n not in sentences:
            problems.append(f"{source}:{no_claim[n]}: S{n} is marked no claim but is not a sentence in the numbered draft")
        elif n in with_claim:
            problems.append(f"{source}:{no_claim[n]}: S{n} is marked no claim and also carries {with_claim[n]}")
    for n in sorted(sentences):
        if n not in with_claim and n not in no_claim:
            problems.append(f"{source}: S{n} has neither a claim nor a no claim mark")
    return problems


def added_claim_problems(sentences: dict[int, str], claims: list[Claim], source: str = "claims.md") -> list[str]:
    """The spec's second stage 4 list, for the reader's file. Stage 6 hands a person 'the draft's
    exact words', so the script confirms those words are in the sentence the claim cites, as ADR
    0008 does for quotes."""
    problems = []
    for claim in claims:
        where = f"{source}:{claim.line} {claim.id}"
        if not claim.words:
            problems.append(f"{where}: no Draft words line")
        elif claim.sentence in sentences and not quote_on_page(claim.words, sentences[claim.sentence]):
            problems.append(f"{where}: the draft words are not in S{claim.sentence}")
    return problems


# ---------------------------------------------------------------- records


@dataclass
class Evidence:
    ref: str
    role: str
    url: str
    quote: str
    line: int


@dataclass
class Record:
    id: str
    fields: dict[str, str] = field(default_factory=dict)
    evidence: list[Evidence] = field(default_factory=list)
    searches: list[str] = field(default_factory=list)
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

    def quotes(self, role: str) -> list[Evidence]:
        return [e for e in self.evidence if e.role == role]

    def has(self, key: str) -> bool:
        return self.fields.get(key, "").strip().lower() not in ("", "none", "-")


RECORD_HEADING = re.compile(r"^##\s+(C\d+)\s*(?:\|.*)?$")
EVIDENCE = re.compile(r'^\s+-\s+(E\d+)\s*\|\s*([A-Za-z-]+)\s*\|\s*(\S+)\s*\|\s*"(.*)"\s*$')
LIST_LINE = re.compile(r"^\s+-\s+(.+?)\s*$")
WEB_ADDRESS = re.compile(r"https?://\S+|\b[a-z0-9][a-z0-9-]*(?:\.[a-z0-9-]+)*\.[a-z]{2,}(?:/\S*)?", re.IGNORECASE)


def parse_records(text: str, source: str = "") -> list[Record]:
    records: list[Record] = []
    current: Record | None = None
    section = ""
    for number_, raw in enumerate(text.splitlines(), 1):
        if raw.startswith("## "):
            heading = RECORD_HEADING.match(raw)
            if not heading:
                raise FormatError(f"{source}:{number_}: a record heading must be '## C01'")
            current = Record(heading.group(1), line=number_, source=source)
            records.append(current)
            section = ""
            continue
        if current is None:
            continue
        match = FIELD.match(raw)
        if match:
            key, value = match.group(1).strip().lower(), match.group(2).strip()
            section = key if key in ("evidence", "searches") else ""
            if key == "searches":
                if value.lower() not in ("", "none", "-"):
                    current.searches.append(value)
            elif key != "evidence":
                current.fields[key] = value
            continue
        if section == "evidence" and raw.strip():
            item = EVIDENCE.match(raw)
            if not item:
                raise FormatError(f'{source}:{number_}: evidence lines are "  - E1 | page | web address | \\"quote\\""')
            current.evidence.append(Evidence(item.group(1), item.group(2).lower(), item.group(3), item.group(4), number_))
        elif section == "searches" and raw.strip():
            item = LIST_LINE.match(raw)
            if not item:
                raise FormatError(f"{source}:{number_}: each search goes on its own line, as '  - the words searched'")
            current.searches.append(item.group(1))
    return records


def read_records(path: Path) -> list[Record]:
    return parse_records(path.read_text(encoding="utf-8"), path.name)


def format_problems(record: Record) -> list[str]:
    """Whether the record can be read at all: a known verdict, and evidence lines that hold a role,
    a web address and a quote long enough to look for."""
    where = f"{record.source}:{record.line} {record.id}"
    problems = []
    if record.verdict not in VERDICTS:
        problems.append(f"{where}: verdict must be one of {', '.join(VERDICTS)}")
    for item in record.evidence:
        if item.role not in ROLES:
            problems.append(f"{where} {item.ref}: an evidence line is marked {' or '.join(ROLES)}")
        if not item.url.startswith(("http://", "https://")):
            problems.append(f"{where} {item.ref}: not a web address")
        if len(item.quote.split()) < 2:
            problems.append(f"{where} {item.ref}: quote at least two words")
    return problems


def stage4_problems(record: Record) -> list[str]:
    """The spec's first stage 4 list: the shape rules for verdicts and problem types."""
    where = f"{record.source}:{record.line} {record.id}"
    verdict, types = record.verdict, record.problems
    problems = []
    unknown = [p for p in types if p not in PROBLEMS]
    if unknown:
        problems.append(f"{where}: not one of the ten problem types: {', '.join(unknown)}")
    if verdict == "differs" and not types:
        problems.append(f"{where}: a differs needs at least one problem type")
    if verdict == "supported" and not record.quotes("page"):
        problems.append(f"{where}: a supported needs evidence, a quote marked page from the first publisher's page")
    if verdict == "no-source" and not record.searches:
        problems.append(f"{where}: a no-source lists the searches tried")
    if "out-of-date" in types and not record.quotes("newer"):
        problems.append(f"{where}: out-of-date needs a quote marked newer, for the newer figure or fact")
    if "publisher-disagrees" in types and len({(e.url, plain(e.quote)) for e in record.quotes("page")}) < 2:
        problems.append(f"{where}: publisher-disagrees needs two quotes marked page, one for each figure")
    if "page-gone" in types and not WEB_ADDRESS.search(record.fields.get("page gone", "")):
        problems.append(f"{where}: page-gone needs a Page gone line naming the address that has gone")
    departs = [p for p in types if p in DRAFT_SIDE]
    if verdict == "supported" and departs and not record.has("still supported"):
        problems.append(f"{where}: a supported carrying {', '.join(departs)} needs a Still supported line saying why")
    if verdict in ("could-not-open", "no-source"):
        barred = [p for p in types if p in PROBLEMS and p != "page-gone"]
        if barred:
            problems.append(f"{where}: a {verdict} can carry page-gone or nothing, not {', '.join(barred)}")
    if verdict == "could-not-open" and not record.has("in the way"):
        problems.append(f"{where}: a could-not-open needs an In the way line saying what stood in the way")
    return problems


def added_problems(record: Record) -> list[str]:
    """The spec's second stage 4 list: a record the report in stage 6 could not be written from."""
    where = f"{record.source}:{record.line} {record.id}"
    verdict = record.verdict
    problems = []
    if not record.has("finding"):
        problems.append(f"{where}: no Finding line")
    if verdict in ("supported", "differs", "could-not-open") and not record.has("first publisher"):
        problems.append(f"{where}: a {verdict} names the first publisher")
    if verdict in ("supported", "differs") and not record.has("published"):
        problems.append(f"{where}: a {verdict} needs a Published line, the date or 'not shown'")
    if verdict == "differs" and not record.evidence:
        problems.append(f"{where}: a differs needs evidence")
    if verdict == "differs" and not record.has("use instead"):
        problems.append(f"{where}: a differs needs a Use instead line")
    if verdict == "could-not-open":
        if not record.fields.get("address", "").strip().startswith(("http://", "https://")):
            problems.append(f"{where}: a could-not-open needs an Address line, the web address a person should open")
        if not record.has("look for"):
            problems.append(f"{where}: a could-not-open needs a Look for line")
    return problems


def check_record(record: Record) -> list[str]:
    problems = format_problems(record)
    if record.verdict not in VERDICTS:
        return problems
    return problems + stage4_problems(record) + added_problems(record)


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


def domain_of(value: str) -> str:
    """The bare host of a web address, lower case, without www."""
    value = value.strip().strip("<>()[]").strip()
    if not value:
        return ""
    if "://" not in value:
        value = "https://" + value
    host = (urllib.parse.urlparse(value).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def pace(host: str, now=time.monotonic, sleep=time.sleep) -> None:
    """Wait until the pause for this site has passed since the last request to it."""
    last = _last_request.get(host)
    if last is not None:
        wait = PAUSE - (now() - last)
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
            if page.kind == "application/pdf":
                return page
            try:
                raw = response.read(5_000_000)
            except http.client.IncompleteRead as partial:
                raw = partial.partial
            charset = response.headers.get_content_charset() or "utf-8"
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


def page_text(raw: str) -> str:
    """Visible text of an HTML page, in reading order, with blocks on their own lines."""
    raw = re.sub(r"(?is)<(script|style|noscript|template)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?is)<!--.*?-->", " ", raw)
    raw = re.sub(r"(?i)<(br|/p|/div|/li|/tr|/h\d|/dd|/dt|/td|/th)[^>]*>", "\n", raw)
    raw = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    lines = (" ".join(l.split()) for l in raw.splitlines())
    return "\n".join(l for l in lines if l)


# ---------------------------------------------------------------- quote check

# Curly quotes, dashes and non-breaking spaces fold to plain ones. Built from code points so this
# file never contains the characters the repo bans.
FOLD = str.maketrans({chr(0x2018): "'", chr(0x2019): "'", chr(0x201C): '"', chr(0x201D): '"', chr(0x2013): "-", chr(0x2014): "-", chr(0x00A0): " "})
WORD_CHARS = "\\w\u00a3$\u20ac%'"


def plain(text: str) -> str:
    text = text.translate(FOLD)
    # A page can hold a figure and its percent sign in two tags, which reads as "86 %". That gap is
    # spacing, so it is closed on both the quote and the page.
    text = re.sub(r"(?<=\d)\s+(?=%)", "", text)
    return " ".join(text.lower().split())


def quote_on_page(quote: str, text: str) -> bool:
    """Whole words, in order, ignoring case, spacing, quote marks and punctuation, and nothing else."""
    words = [w for w in (w.strip("'") for w in re.findall(rf"[{WORD_CHARS}]+", plain(quote))) if w]
    if not words:
        return False
    pattern = r"(?<![\w'])" + rf"[^{WORD_CHARS}]+".join(re.escape(w) for w in words) + r"(?![\w'])"
    # An apostrophe inside a word is part of it. One at a word's edge is a quote mark, so it goes.
    folded = re.sub(r"(?<![\w])'+|'+(?![\w])", " ", plain(text))
    return re.search(pattern, folded) is not None


class PageCache:
    """Each page is loaded once per run. A page that loaded is kept as text in working/pages/, so a
    later verify in the same run folder reads the copy. A page that failed is tried again by the next
    verify, never twice by this one."""

    def __init__(self, folder: Path, get=fetch):
        self.folder = folder
        self.get = get
        self.seen: dict[str, tuple[str, str]] = {}
        folder.mkdir(parents=True, exist_ok=True)

    def text(self, url: str) -> tuple[str, str]:
        """(state, text): state is "ok", "pdf" or "error: ..."."""
        if url not in self.seen:
            self.seen[url] = self.load(url)
        return self.seen[url]

    def load(self, url: str) -> tuple[str, str]:
        path = self.folder / f"{hashlib.sha1(url.encode()).hexdigest()[:16]}.json"
        if path.is_file():
            saved = json.loads(path.read_text(encoding="utf-8"))
            return saved["state"], saved["text"]
        parts = urllib.parse.urlparse(url)
        if parts.path.lower().endswith(".pdf") or "format=pdf" in parts.query:
            # The script cannot read a PDF, so it does not download one just to say so.
            return "pdf", ""
        page = self.get(url)
        if page.kind == "application/pdf":
            state, text = "pdf", ""
        elif page.error and not page.text:
            return f"error: {page.error}", ""
        else:
            state, text = "ok", page_text(page.text)
        path.write_text(json.dumps({"url": url, "state": state, "text": text}), encoding="utf-8")
        return state, text


# ---------------------------------------------------------------- verify


def record_files(run: Path) -> list[Path]:
    def order(path: Path) -> int:
        return int(re.sub(r"\D", "", path.stem) or 0)

    working = run / "working"
    return sorted(working.glob("research-*.md"), key=order) + sorted(working.glob("check-*.md"), key=order)


def is_check(path_name: str) -> bool:
    return path_name.startswith("check-")


def evidence_states(run: Path) -> dict[str, str]:
    store = run / "working" / "evidence.json"
    return json.loads(store.read_text(encoding="utf-8")) if store.is_file() else {}


def verify(
    run: Path, files: list[Path] | None = None, claims_only: bool = False, get=fetch
) -> tuple[list[str], list[str], dict[str, str]]:
    """(problems, notes, states). Problems fail the run. Notes do not: they are counts, and quotes
    the script looked for and did not find, which stage 5 sends to the checker. `files` checks only
    those record files. With none given, the whole run is checked, and every traced claim needs a record."""
    sentences = read_lines(run / "draft-lines.md")
    claims, no_claim = read_claims(run / "claims.md")
    problems = check_claims(sentences, claims, no_claim) + added_claim_problems(sentences, claims)
    by_id = {c.id: c for c in claims}
    traced = [c for c in claims if c.trace == "yes"]
    notes = [f"{len(sentences)} sentences, {len(claims)} claims: {len(traced)} to trace, {len(claims) - len(traced)} to confirm with a person"]
    if len(traced) > CAP_SUBAGENT:
        notes.append(f"over {CAP_SUBAGENT} claims to trace: run the draft in parts")
    elif len(traced) > CAP_CHAT:
        notes.append(f"over {CAP_CHAT} claims to trace: too many for the chat route in one run")
    states: dict[str, str] = {}
    if claims_only:
        return problems, notes, states
    whole_run = files is None
    paths = record_files(run) if files is None else files
    cache = PageCache(run / "working" / "pages", get)
    first_pass: dict[str, str] = {}
    for path in paths:
        try:
            records = read_records(path)
        except FormatError as error:
            problems.append(str(error))
            continue
        if not records:
            problems.append(f"{path.name}: no records")
        seen_here: set[str] = set()
        for record in records:
            where = f"{path.name}:{record.line} {record.id}"
            claim = by_id.get(record.id)
            if claim is None:
                problems.append(f"{where}: no such claim in claims.md")
            elif claim.trace != "yes":
                problems.append(f"{where}: this claim is on the confirm list and is not traced")
            if record.id in seen_here or (not is_check(path.name) and record.id in first_pass):
                problems.append(f"{where}: a second record for this claim")
            seen_here.add(record.id)
            if not is_check(path.name):
                first_pass.setdefault(record.id, path.name)
            problems += check_record(record)
            for item in record.evidence:
                if not item.url.startswith(("http://", "https://")):
                    continue
                state, text = cache.text(item.url)
                if state == "ok":
                    result = "verified" if quote_on_page(item.quote, text) else "not-on-page"
                elif state == "pdf":
                    result = "pdf"
                else:
                    result = "could-not-load"
                states[f"{path.name}|{record.id}|{item.ref}"] = result
                if result == "not-on-page":
                    notes.append(f"{path.name}:{item.line} {record.id} {item.ref}: quote not found on {item.url}")
    if whole_run:
        for claim in traced:
            if claim.id not in first_pass:
                problems.append(f"claims.md:{claim.line} {claim.id}: no record")
    store = run / "working" / "evidence.json"
    store.parent.mkdir(parents=True, exist_ok=True)
    saved = evidence_states(run)
    saved.update(states)
    store.write_text(json.dumps(saved, indent=1, sort_keys=True), encoding="utf-8")
    return problems, notes, states


# ---------------------------------------------------------------- re-check


def state_of(record: Record, item: Evidence, states: dict[str, str]) -> str:
    return states.get(f"{record.source}|{record.id}|{item.ref}", "not-checked")


def needs_check(record: Record, states: dict[str, str]) -> bool:
    """Stage 5: every supported claim, and every claim resting on evidence the script could not
    confirm. A differs whose every quote was found on its page goes straight to the report."""
    if record.verdict == "supported":
        return True
    return any(state_of(record, item, states) != "verified" for item in record.evidence)


def stripped(claim: Claim, record: Record) -> list[str]:
    """What a checker reads about one claim: the claim and the verdict. Never the first publisher,
    the evidence, the reasons or the problem types."""
    return [
        f"## {claim.id} | S{claim.sentence} | {claim.kind}",
        f"- Claim: {claim.text}",
        f'- Draft words: "{claim.words}"',
        f"- Source given: {claim.source}",
        f"- Verdict: {record.verdict}",
        "",
    ]


def write_check_in(run: Path, claims: dict[str, Claim], research: list[Record], states: dict[str, str]) -> list[str]:
    """Write check-in/to-check-<n>.md for each research file with claims to re-check. Returns their IDs."""
    folder = run / "check-in"
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("to-check-*.md"):
        old.unlink()
    sent: list[str] = []
    by_file: dict[str, list[str]] = {}
    for record in research:
        claim = claims.get(record.id)
        if claim is None or not needs_check(record, states):
            continue
        sent.append(record.id)
        by_file.setdefault(record.source, []).extend(stripped(claim, record))
    for source, lines in by_file.items():
        name = "to-check-" + (re.sub(r"\D", "", Path(source).stem) or "1") + ".md"
        (folder / name).write_text("\n".join(lines), encoding="utf-8")
    return sent


# ---------------------------------------------------------------- report

UNCHECKED = "No verdict was re-checked: these are the first pass only, and no separate checker tried to prove them wrong."
COMPARISONS = (
    "Comparisons between claims were not checked. Each claim has its own verdict, and whether two "
    "figures can fairly be set side by side is for you to judge."
)
STATE_WORDS = {
    "verified": "found on the page by the script",
    "not-on-page": "not found on the page by the script",
    "pdf": "in a PDF, which the script cannot read",
    "could-not-load": "the page would not load for the script",
    "not-checked": "not checked by the script",
}


def count(n: int, word: str) -> str:
    return f"{n} {word}" + ("" if n == 1 else "s")


def changed(first: Record | None, check: Record | None) -> str:
    """How the checker changed the first pass, in words, or "" if it did not."""
    if not first or not check:
        return ""
    if first.verdict != check.verdict:
        return f"changed it, was {first.verdict}" + (f" ({', '.join(first.problems)})" if first.problems else "")
    if sorted(first.problems) != sorted(check.problems):
        return f"kept it {check.verdict}, changed the problem types, were {', '.join(first.problems) or 'none'}"
    return ""


def merged(run: Path) -> tuple[list[Record], dict[str, Record]]:
    research: list[Record] = []
    checks: dict[str, Record] = {}
    for path in record_files(run):
        if is_check(path.name):
            checks.update({r.id: r for r in read_records(path)})
        else:
            research += read_records(path)
    return research, checks


def report(run: Path, today: str | None = None) -> list[str]:
    today = today or time.strftime("%Y-%m-%d")
    sentences = read_lines(run / "draft-lines.md")
    claims, _ = read_claims(run / "claims.md")
    research, checks = merged(run)
    states = evidence_states(run)
    by_id = {c.id: c for c in claims}
    first_of = {r.id: r for r in reversed(research)}
    sent = write_check_in(run, by_id, research, states)
    traced = [c for c in claims if c.trace == "yes"]
    final = {c.id: checks.get(c.id) or first_of.get(c.id) for c in traced}
    missing = [c.id for c in traced if final[c.id] is None]
    lost = [i for i in sent if i not in checks]
    nothing_rechecked = bool(sent) and not checks

    verdicts: Counter = Counter()
    types: Counter = Counter()
    for claim in traced:
        record = final[claim.id]
        if record is None:
            continue
        verdicts[record.verdict] += 1
        types.update(record.problems)
    rechecked = [c for c in traced if c.id in checks]
    overturned = sum(1 for c in rechecked if changed(first_of.get(c.id), checks[c.id]))
    quote_states = Counter(state_of(r, e, states) for r in final.values() if r for e in r.evidence)

    def label(claim: Claim) -> str:
        return f"{claim.id} | S{claim.sentence}"

    def checker_line(claim: Claim) -> list[str]:
        check = checks.get(claim.id)
        if not check:
            return []
        note = check.fields.get("check notes", "")
        if note.lower().startswith("agreed"):
            note = note[len("agreed"):].lstrip(" :.,")
        what = changed(first_of.get(claim.id), check) or "agreed"
        return [f"- Checker: {what}" + (f". {note}" if note else "")]

    def evidence_lines(record: Record) -> list[str]:
        if not record.evidence:
            return []
        out = ["- Evidence:"]
        for item in record.evidence:
            out.append(f'  - {item.ref} {item.role}: {item.url} "{item.quote}" ({STATE_WORDS[state_of(record, item, states)]})')
        return out

    def publisher(record: Record) -> list[str]:
        out = []
        if record.has("first publisher"):
            out.append(f"- First publisher: {record.fields['first publisher']}")
        if record.has("published"):
            out.append(f"- Published: {record.fields['published']}")
        return out

    def full(claim: Claim, record: Record) -> list[str]:
        """One claim with everything a person needs to fix or cite it. What to do comes first."""
        head = f"### {label(claim)}: {record.verdict}" + (f", {', '.join(record.problems)}" if record.problems else "")
        out = [head, "", f'- The draft says: "{claim.words}"']
        if record.has("use instead"):
            out.append(f"- Use instead: {record.fields['use instead']}")
        out.append(f"- What was found: {record.fields.get('finding', '')}")
        out.append(f"- Claim: {claim.text}")
        if not claim.source.lower().startswith("none"):
            out.append(f"- Source the draft gives: {claim.source}")
        out += publisher(record)
        for key, words in (("still supported", "Still supported because"), ("page gone", "Page gone")):
            if record.has(key):
                out.append(f"- {words}: {record.fields[key]}")
        if record.verdict == "no-source":
            out.append("- Searches tried:")
            out += [f"  - {search}" for search in record.searches]
        return out + checker_line(claim) + evidence_lines(record) + [""]

    def having(verdict: str, with_types: bool | None = None) -> list[Claim]:
        found = [c for c in traced if final[c.id] and final[c.id].verdict == verdict]
        return found if with_types is None else [c for c in found if bool(final[c.id].problems) == with_types]

    # The order is the user's, least work first (ADR 0021): what to fix, what to update, what is
    # their call, what needs a person, what needs nothing, and last how the check was done.
    def unfound(claim: Claim) -> list[Evidence]:
        """The quotes that leave a supported claim unconfirmed: the script loaded the page, looked
        for each quote marked page, and found none of them. A PDF or a page that would not load is
        not this: the script could not look, and the quote's state is shown beside it."""
        record = final[claim.id]
        found = [state_of(record, item, states) for item in record.quotes("page")]
        if "verified" in found or "not-on-page" not in found:
            return []
        return [item for item in record.quotes("page") if state_of(record, item, states) == "not-on-page"]

    unconfirmed_claims = [c for c in having("supported") if unfound(c)]
    fix, your_call, unopened = having("differs"), having("no-source"), having("could-not-open")
    update = [c for c in having("supported", True) if c not in unconfirmed_claims]
    clean = [c for c in having("supported", False) if c not in unconfirmed_claims]
    own = [c for c in claims if c.trace == "own-company"]
    person = [c for c in claims if c.trace == "named-person"]

    lines = ["# Claims check", ""] + ([UNCHECKED, ""] if nothing_rechecked else [])
    lines += [f"Checked {today}. {count(len(sentences), 'sentence')}, {count(len(claims), 'claim')}.", ""]
    lines += [
        f"**{len(clean)} of the {count(len(claims), 'claim')} {'needs' if len(clean) == 1 else 'need'} nothing from you.** What the rest need, least work first:",
        "",
        "| What to do | Claims |",
        "|---|---|",
        f"| Fix: the first publisher says something else, and the words to use are given | {len(fix)} |",
        f"| Update or re-credit: supported, with a newer figure or a better source to give | {len(update)} |",
        f"| Your call: no source was found | {len(your_call)} |",
        f"| Confirm with a person: one visit or one question each | {len(unopened) + len(unconfirmed_claims) + len(own) + len(person)} |",
    ]
    if missing:
        lines.append(f"| Not checked: no record | {len(missing)} |")
    lines.append("")

    def section(title: str, intro: str, group: list[Claim]) -> list[str]:
        out = [f"## {title}", "", intro, ""]
        for claim in group:
            out += full(claim, final[claim.id])
        return out + ([] if group else ["None.", ""])

    lines += section("Fix these", "The first publisher says something else. The words to use come first, then what was found.", fix)
    lines += section(
        "Update or re-credit these",
        "Supported, with something to add: a newer figure, the first publisher in place of a page that repeats it, or a page that has gone.",
        update,
    )
    lines += section(
        "Your call: no source found",
        "No first publisher was found. That is not proof there is none. Cut the claim, soften it, or cite it yourself.",
        your_call,
    )

    lines += ["## Confirm with a person", ""]
    for heading, group in (("About your own company", own), ("About a named person", person)):
        lines += [f"### {heading}", ""]
        lines += [f'- **{label(c)}**: "{c.words}". {c.text}' for c in group] or ["None."]
        lines.append("")
    lines += ["### Pages that could not be opened", ""]
    for claim in unopened:
        record = final[claim.id]
        lines += [
            f"- **{label(claim)}**",
            f"  - Open: {record.fields.get('address', '')}",
            f'  - The draft says: "{claim.words}"',
            f"  - What stood in the way: {record.fields.get('in the way', '')}",
            f"  - Look for: {record.fields.get('look for', '')}",
        ]
        lines += ["  " + line for line in publisher(record)]
        if record.has("page gone"):
            lines.append(f"  - Page gone: {record.fields['page gone']}")
        lines += ["  " + line for line in checker_line(claim)]
    lines += ([] if unopened else ["None."]) + [""]
    lines += ["### Supported, but the script did not find the quote", ""]
    for claim in unconfirmed_claims:
        record = final[claim.id]
        lines += [f"- **{label(claim)}**", f'  - The draft says: "{claim.words}"']
        for item in unfound(claim):
            lines += [f"  - Open: {item.url}", f'  - Look for: "{item.quote}"']
        lines += ["  " + line for line in publisher(record) + checker_line(claim)]
    lines += ([] if unconfirmed_claims else ["None."]) + [""]

    lines += ["## Nothing to do", "", "Supported, with nothing against it.", ""]
    for claim in clean:
        record = final[claim.id]
        lines.append(f'- **{label(claim)}**: "{claim.words}"')
        lines += ["  " + line for line in publisher(record) + checker_line(claim) + evidence_lines(record)]
    lines += ([] if clean else ["None."]) + [""]

    lines += ["## How this was checked", "", "| Verdict | Claims |", "|---|---|"]
    lines += [f"| {verdict} | {verdicts[verdict]} |" for verdict in VERDICTS]
    if missing:
        lines.append(f"| no record | {len(missing)} |")
    lines.append("")
    if types:
        lines += ["| Problem type | Claims |", "|---|---|"]
        lines += [f"| {p} | {types[p]} |" for p in PROBLEMS if types[p]]
        lines += [f"| {p} | {types[p]} |" for p in sorted(types) if p not in PROBLEMS]
    else:
        lines.append("No claim carries a problem type.")
    lines += ["", f"The checker re-checked {count(len(rechecked), 'claim')} and changed the verdict or the problem types of {overturned}."]
    if lost and not nothing_rechecked:
        lines.append(f"Sent to the checker but no record came back, so these show the first pass only: {', '.join(lost)}.")
    if missing:
        lines.append(f"No record, so not checked: {', '.join(missing)}.")
    unconfirmed = sum(n for state, n in quote_states.items() if state != "verified")
    lines += [
        f"Quotes found on their pages by the script: {quote_states['verified']}. Not confirmed by the script: {unconfirmed} "
        f"({quote_states['pdf']} in PDFs, {quote_states['could-not-load'] + quote_states['not-checked']} on pages it did not load, "
        f"{quote_states['not-on-page']} not found).",
        "",
        COMPARISONS,
        "",
    ]

    (run / "check.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    notes = [f"{len(traced)} claims traced: " + ", ".join(f"{verdicts[v]} {v}" for v in VERDICTS)]
    if types:
        notes.append("problem types: " + ", ".join(f"{types[p]} {p}" for p in PROBLEMS if types[p]))
    notes.append(f"to re-check: {count(len(sent), 'claim')}, written to check-in/" if sent else "to re-check: none")
    notes.append(f"checker re-checked {len(rechecked)}, changed {overturned}")
    if nothing_rechecked:
        notes.append("no verdict was re-checked, and the report says so at the top")
    elif lost:
        notes.append(f"sent to the checker but no record came back: {', '.join(lost)}")
    if missing:
        notes.append(f"no record for {', '.join(missing)}")
    notes.append(f"report written to {run / 'check.md'}")
    return notes


# ---------------------------------------------------------------- command line


def main(argv: list[str]) -> int:
    usage = __doc__.strip().split("\n\n")[2]
    if not argv:
        print(usage, file=sys.stderr)
        return 2
    command, args = argv[0], argv[1:]
    try:
        if command == "number" and len(args) == 2:
            source, out = Path(args[0]), Path(args[1])
            sentences = number(read_draft(source))
            if not sentences:
                print(f"error: no sentences found in {source}", file=sys.stderr)
                return 1
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(write_lines(sentences), encoding="utf-8")
            print(f"{len(sentences)} sentences written to {out}")
        elif command == "verify" and args and not args[0].startswith("--"):
            claims_only = args[1:] == ["--claims"]
            if not claims_only and any(a.startswith("--") for a in args[1:]):
                print(usage, file=sys.stderr)
                return 2
            files = None if claims_only or len(args) == 1 else [Path(a) for a in args[1:]]
            problems, notes, states = verify(Path(args[0]), files, claims_only)
            print("\n".join(notes))
            if not claims_only:
                counts = Counter(states.values())
                print("evidence: " + (", ".join(f"{n} {s}" for s, n in sorted(counts.items())) or "none"))
            if problems:
                print("\n".join(problems))
                print(f"\n{len(problems)} problems")
                return 1
            print("ok")
        elif command == "report" and len(args) == 1:
            print("\n".join(report(Path(args[0]))))
        else:
            print(usage, file=sys.stderr)
            return 2
    except (FormatError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
