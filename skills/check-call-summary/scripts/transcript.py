"""Number a transcript, verify a checker's quotes, and build the report for check-call-summary.

Standard library only, so it runs wherever Python 3.10 or later does.

    python3 transcript.py number <transcript> <out transcript-lines.md>
    python3 transcript.py verify <transcript-lines.md> <key-facts.md> [<summary> <check file> [--by-hand]]
    python3 transcript.py report <out check.md> <key-facts.md> <check file> [<check file> ...]
"""

from __future__ import annotations

import html
import json
import re
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

VERDICTS = ("said", "inferred", "not-in-transcript", "contradicted")
FAILURES = (
    "wrong-speaker",
    "tone-read-as-sincere",
    "intention-as-done",
    "owner-or-date-wrong",
    "made-up-detail",
    "overstated",
)
LEFT_OUT = "left-out"
KINDS = ("next-step", "commitment", "date", "number", "who-decides", "objection", "competitor")
STATUSES = ("carried", "carried wrongly", "missing")
CONFIRM_KINDS = ("next-step", "commitment")
UNLABELLED = "unlabelled"


class FormatError(ValueError):
    """A file that does not follow the format the skill expects."""


# ---------------------------------------------------------------- numbering

TIMING = re.compile(r"^\s*(\d{1,2}:)?\d{1,2}:\d{2}[.,]\d{1,3}\s*-->\s*(\d{1,2}:)?\d{1,2}:\d{2}[.,]\d{1,3}")
STAMP = r"(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?"
# A speaker label: one to four words, each starting with a capital or a digit ("Speaker 1"), plus the
# small words in names such as "van der Berg". So "So the thing is: we..." is never read as a speaker.
PARTICLES = r"(?:van|von|der|den|de|da|di|du|del|la|le|bin|al|el|ter)"
WORD = r"(?:[^\W\d_a-z][\w.'\-]*|\d+)"
NAME = rf"{WORD}(?: (?:{WORD}|{PARTICLES})){{0,3}}"
ORG = r"(?:\s*\((?![\d:.,]+\))[^)]{1,40}\))?"  # "Priya Shah (Acme):", but not a timestamp
VOICE = re.compile(r"<v(?:\.[\w.]+)?\s+([^>]+)>")
TAG = re.compile(r"</?[^>]+>")
# Bracketed sound tags, kept in the words and never read as a speaker.
SOUNDS = {
    "laughs", "laughter", "laughing", "chuckles", "music", "inaudible", "crosstalk", "silence",
    "applause", "coughs", "pause", "noise", "background noise", "indistinct", "sighs",
}
# Lines at the top of an export that describe the call rather than record it.
EXPORT_HEADERS = {
    "date", "time", "title", "meeting", "attendees", "participants", "duration", "location",
    "recording", "transcript", "subject", "agenda", "speakers", "created", "host",
    "organizer", "organiser", "owner", "id", "meeting id", "url", "link", "language",
}
# Plain-text turns, tried in order.
# "[00:01:23]", "(00:01:23)", or a range such as "[00:05 - 00:08]" as the Fireflies connector gives it.
# A range only counts inside brackets, so an agenda line such as "09:00 - 09:30 Intro: ..." is not a turn.
STAMP_FIRST = re.compile(
    rf"^(?:[\[(]({STAMP})(?:\s*[-\u2013]\s*{STAMP})?[\])]|({STAMP}))\s+({NAME}){ORG}\s*:\s+(.+)$"
)
NAME_STAMP = re.compile(rf"^({NAME}){ORG}\s*[\[(]({STAMP})[\])]\s*:\s*(.*)$")
NAME_ONLY = re.compile(rf"^({NAME}){ORG}\s*:\s+(.+)$")
# Exports that put the speaker and time on a line of their own, with the words below.
HEADING = re.compile(rf"^\[?({NAME})\]?{ORG}\s+(?:-\s+)?[\[(]?({STAMP})[\])]?\s*$")
BRACKETED = re.compile(rf"^\[({NAME})\]\s*(.+)$")
EMPHASIS = re.compile(r"^(\*\*|__)(.+?)\1")


def unemphasise(line: str) -> str:
    """"**Priya:** Hello" and "**Priya**: Hello" as "Priya: Hello"."""
    return EMPHASIS.sub(lambda m: m.group(2), line, count=1)


@dataclass
class Line:
    number: int
    time: str
    speaker: str
    text: str

    def render(self) -> str:
        stamp = f" {self.time}" if self.time else ""
        return f"[L{self.number}]{stamp} {self.speaker}: {self.text}"


def clock(stamp: str) -> str:
    """Any timestamp as HH:MM:SS."""
    parts = re.split(r"[.,]", stamp)[0].split(":")
    while len(parts) < 3:
        parts.insert(0, "0")
    return ":".join(f"{int(part):02d}" for part in parts)


def is_sound(name: str) -> bool:
    return name.strip().lower() in SOUNDS


def speaker_and_text(text: str) -> tuple[str, str]:
    """One caption's speaker and words, from a voice tag, "Name:" or "[Name]"."""
    voice = VOICE.search(text)
    if voice:
        return voice.group(1).strip(), TAG.sub("", text).strip()
    text = unemphasise(TAG.sub("", text).strip())
    match = NAME_ONLY.match(text)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    bracketed = BRACKETED.match(text)
    if bracketed and not is_sound(bracketed.group(1)):
        return bracketed.group(1).strip(), bracketed.group(2).strip()
    return "", text


def split_cue(words: list[str]) -> list[str]:
    """A caption can hold several turns: two voice tags, or lines starting "- Name:"."""
    joined = " ".join(words)
    voices = VOICE.findall(joined)
    if len(voices) > 1:
        return [part for part in re.split(r"(?=<v[\s.])", joined) if TAG.sub("", part).strip()]
    if len(words) > 1 and all(w.startswith("- ") for w in words):
        return [w[2:] for w in words]
    return [joined]


def parse_cues(text: str) -> list[tuple[str, str, str]]:
    """WebVTT and SRT: one entry per turn in each caption."""
    entries: list[tuple[str, str, str]] = []
    for block in re.split(r"\n\s*\n", text):
        lines = [line.strip() for line in block.strip().splitlines() if line.strip()]
        timing_at = next((i for i, line in enumerate(lines) if TIMING.match(line)), None)
        if timing_at is None:
            continue  # WEBVTT header, NOTE and STYLE blocks
        time = clock(lines[timing_at].split("-->")[0].strip())
        for part in split_cue(lines[timing_at + 1 :]):
            speaker, spoken = speaker_and_text(part)
            if spoken:
                entries.append((time, speaker, spoken))
    return entries


def parse_plain(text: str) -> list[tuple[str, str, str]]:
    entries: list[tuple[str, str, str]] = []
    speaker, time = "", ""
    heading_time = ""  # a heading's time goes on the first paragraph under it
    under_heading = False  # only words under a speaker heading take that speaker
    for raw in text.splitlines():
        line = unemphasise(raw.strip())
        if not line:
            continue
        if not entries and not speaker:
            label = line.split(":", 1)[0].strip().lower()
            if ":" in line and label in EXPORT_HEADERS:
                continue  # "Date: 4 March 2026" above the first turn
        first = STAMP_FIRST.match(line)
        named = NAME_STAMP.match(line)
        if first or named:
            if first:
                stamp, speaker, words = first.group(1) or first.group(2), first.group(3), first.group(4)
            else:
                speaker, stamp, words = named.group(1), named.group(2), named.group(3)
            speaker, time, under_heading = speaker.strip(), clock(stamp), False
            if words.strip():
                entries.append((time, speaker, words.strip()))
            else:
                heading_time, under_heading = time, True  # "Speaker 1 (00:00:05):" on a line of its own
            continue
        heading = HEADING.match(line)
        if heading:
            speaker, time = heading.group(1).strip(), clock(heading.group(2))
            heading_time, under_heading = time, True
            continue
        match = NAME_ONLY.match(line)
        if match:
            speaker, under_heading = match.group(1).strip(), False
            entries.append(("", speaker, match.group(2).strip()))
            continue
        bracketed = BRACKETED.match(line)
        if bracketed and not is_sound(bracketed.group(1)):
            speaker, under_heading = bracketed.group(1).strip(), False
            entries.append(("", speaker, bracketed.group(2).strip()))
            continue
        # Words under a speaker heading belong to that speaker. Anywhere else, a line the script
        # cannot attribute stays unlabelled: guessing the last speaker is how mislabels are made.
        entries.append((heading_time, speaker if under_heading else "", line))
        heading_time = ""
    return entries


# JSON exports and connector responses name the same three things in different ways.
JSON_TEXT = ("text", "sentence", "raw_text", "content", "transcript_text")
JSON_SPEAKER = ("speaker_name", "speakerName", "speaker", "display_name", "name", "participant")
JSON_TIME = ("start_time", "startTime", "timestamp", "start", "time", "start_ms", "offset")


GROUPS = ("sentences", "utterances", "segments")


def expand_groups(items: list[dict]) -> list[dict]:
    """Paragraphs that hold their sentences in a list: one turn per sentence, keeping the speaker."""
    turns = []
    for item in items:
        inner = next((item[key] for key in GROUPS if isinstance(item.get(key), list)), None)
        if inner and not any(isinstance(item.get(key), str) for key in JSON_TEXT):
            for sentence in inner:
                if isinstance(sentence, dict):
                    turns.append({**{k: v for k, v in item.items() if k not in GROUPS}, **sentence})
        else:
            turns.append(item)
    return turns


def candidate_lists(data: object) -> list[list[dict]]:
    found = []
    if isinstance(data, list) and data and all(isinstance(item, dict) for item in data):
        found.append(expand_groups(data))
    children = data.values() if isinstance(data, dict) else data if isinstance(data, list) else []
    for child in children:
        found.extend(candidate_lists(child))
    return found


def json_turns(data: object) -> list[dict] | None:
    """The list of turns in a JSON document: the list whose items carry text with a speaker or a
    time, and are more than single words. A summary's list of bullets or action items carries text
    but neither speakers nor times, so it never wins over the conversation."""

    def score(items: list[dict]) -> tuple[int, int]:
        texts = [next((i[k] for k in JSON_TEXT if isinstance(i.get(k), str)), "") for i in items]
        with_text = [t for t in texts if t.strip()]
        if not with_text:
            return (-1, 0)
        attributed = sum(
            1 for i, t in zip(items, texts) if t.strip() and (json_speaker(i) or any(k in i for k in JSON_TIME))
        )
        single_words = sum(1 for t in with_text if len(t.split()) <= 1) > len(with_text) / 2
        return (attributed * (0 if single_words else 1), len(with_text))

    lists = [items for items in candidate_lists(data) if score(items)[1]]
    return max(lists, key=score) if lists else None


def json_speaker(item: dict) -> str:
    for key in JSON_SPEAKER:
        value = item.get(key)
        if isinstance(value, dict):
            value = value.get("display_name") or value.get("name")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def json_clock(item: dict, in_ms: bool, origin: float = 0) -> str:
    for key in JSON_TIME:
        value = item.get(key)
        if isinstance(value, str) and re.fullmatch(STAMP, value.strip()):
            return clock(value.strip())
        if is_number(value):
            value -= origin
            seconds = int(value / 1000 if in_ms or key.endswith("_ms") else value)
            return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"
    return ""


def parse_json(data: object) -> list[tuple[str, str, str]]:
    """JSON exports and API responses: a list of turns, each with text and usually a speaker and a time."""
    turns = json_turns(data)
    if turns is None:
        # A connector may return the whole transcript as one string: read the longest one as text.
        strings = [s for s in all_strings(data) if "\n" in s or ":" in s]
        text = max(strings, key=len, default="")
        return parse_text(text) if text.strip() else []
    times = [
        next(item[key] for key in JSON_TIME if is_number(item.get(key)))
        for item in turns
        if any(is_number(item.get(key)) for key in JSON_TIME)
    ]
    origin = min(times) if times and min(times) > 1e9 else 0  # clock time since 1970: count from the start
    relative = [t - origin for t in times]
    gaps = sorted(b - a for a, b in zip(relative, relative[1:]) if b > a)
    # Milliseconds give away no unit. No call runs past a day of seconds, and turns a second or more
    # apart in milliseconds are a thousand or more apart.
    in_ms = bool(relative) and (
        max(relative) > 86400 or (all(float(t).is_integer() for t in relative) and bool(gaps) and gaps[len(gaps) // 2] >= 1000)
    )
    entries = []
    for item in turns:
        text = next((item[key] for key in JSON_TEXT if isinstance(item.get(key), str)), "")
        if text.strip():
            entries.append((json_clock(item, in_ms, origin), json_speaker(item), text.strip()))
    return entries


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def all_strings(data: object) -> list[str]:
    if isinstance(data, str):
        return [data]
    children = data.values() if isinstance(data, dict) else data if isinstance(data, list) else []
    return [s for child in children for s in all_strings(child)]


WORD_PARAGRAPH = re.compile(r"<w:p[ >].*?</w:p>|<w:p/>", re.DOTALL)
WORD_PIECE = re.compile(r"<w:t(?: [^>]*)?>([^<]*)</w:t>|<w:(tab|br|cr|noBreakHyphen)\b[^>]*/>")
# Text Word keeps twice (a moved passage's old place, a drawing's fallback) or outside the paragraph flow.
WORD_SKIP = re.compile(
    r"<w:moveFrom\b.*?</w:moveFrom>|<mc:Fallback\b.*?</mc:Fallback>|<w:txbxContent\b.*?</w:txbxContent>", re.DOTALL
)


def docx_text(path: Path) -> str:
    """The text of a Word file, one paragraph per line, read with the standard library."""
    try:
        with zipfile.ZipFile(path) as archive:
            raw = archive.read("word/document.xml")
        xml = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8")
    except (zipfile.BadZipFile, KeyError, UnicodeDecodeError) as error:
        raise FormatError(f"{path}: not a Word file this script can read ({error})") from error
    lines = []
    for paragraph in WORD_PARAGRAPH.findall(WORD_SKIP.sub("", xml)):
        pieces = []
        for words, mark in WORD_PIECE.findall(paragraph):
            pieces.append(words if not mark else {"tab": "\t", "noBreakHyphen": "-"}.get(mark, "\n"))
        lines.append(html.unescape("".join(pieces)))
    return "\n".join(lines)


TEXT_SUFFIXES = {".txt", ".md", ".vtt", ".srt", ".json", ".csv"}


def read_transcript(path: Path) -> str:
    """Any transcript file as text. Word files are unpacked; PDF is refused with a way round it."""
    head = path.read_bytes()[:5]
    if path.suffix.lower() == ".pdf" or head.startswith(b"%PDF"):
        raise FormatError(f"{path}: PDF can't be read reliably. Export the transcript as .txt, .docx, .vtt or .srt, or paste it.")
    if path.suffix.lower() == ".docx" or (head.startswith(b"PK\x03\x04") and path.suffix.lower() not in TEXT_SUFFIXES):
        return docx_text(path)
    return path.read_text(encoding="utf-8-sig", errors="replace")


def parse_text(text: str) -> list[tuple[str, str, str]]:
    looks_like_cues = text.lstrip().startswith("WEBVTT") or any(TIMING.match(line) for line in text.splitlines()[:20])
    return parse_cues(text) if looks_like_cues else parse_plain(text)


def number(text: str) -> list[Line]:
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    entries: list[tuple[str, str, str]] | None = None
    if text.lstrip()[:1] in ("{", "["):
        try:
            entries = parse_json(json.loads(text))
        except json.JSONDecodeError:
            entries = None  # "[00:05 - 00:08] Name:" lines also start with "["
    if entries is None:
        entries = parse_text(text)
    return [
        Line(index, time, speaker or UNLABELLED, re.sub(r"\s+", " ", spoken))
        for index, (time, speaker, spoken) in enumerate(entries, start=1)
    ]


NUMBERED = re.compile(r"^\[L(\d+)\](?: (\d{2}:\d{2}:\d{2}))? (.+?): (.*)$")


def read_lines(path: Path) -> dict[int, Line]:
    lines: dict[int, Line] = {}
    for raw in read_text(path).splitlines():
        match = NUMBERED.match(raw)
        if match:
            n = int(match.group(1))
            lines[n] = Line(n, match.group(2) or "", match.group(3), match.group(4))
    if not lines:
        raise FormatError(f"{path}: no numbered lines. Run the number command first.")
    return lines


# ---------------------------------------------------------------- blocks

QUOTE = re.compile(r'^- Quote: \[L(\d+)(?:-L(\d+))?\] (.+?): "(.*)"\s*$')
NO_QUOTE = re.compile(r"^- Quote: none\s*$", re.IGNORECASE)
FIELD = re.compile(r"^- ([^:]+):\s*(.*)$")
FACT_HEADER = re.compile(r"^## K(\d+)\. (.+?)\s+\(kind: ([a-z-]+)\)\s*$")
DOUBT_HEADER = re.compile(r"^## D(\d+)\. \[L(\d+)\] labelled (.+?), more likely (.+?)\s*$")
CLAIM_HEADER = re.compile(r"^## C(\d+)\. (.+?)\s+\[([a-z-]+)\]\s*$")
SUMMARY_TITLE = re.compile(r"^# Summary: (.+?)\s*$")
FACT_STATUS = re.compile(r"^- K(\d+): (carried wrongly|carried|missing)(?: \(C(\d+)\))?\s*$")
LOOKS_LIKE_BLOCK = re.compile(r"^#{2,6}\s*(?:[A-Za-z]+\s*)?\d")
LOOKS_LIKE_QUOTE = re.compile(r"^-\s*quote\b(?!\s*check)", re.IGNORECASE)


@dataclass
class Quote:
    start: int
    end: int
    speaker: str
    words: str

    def cite(self) -> str:
        span = f"L{self.start}" if self.start == self.end else f"L{self.start}-L{self.end}"
        return f'[{span}] {self.speaker}: "{self.words}"'


@dataclass
class Block:
    kind: str  # K, D or C
    number: int
    title: str
    tag: str  # fact kind, claim verdict, or the doubtful line number
    lines: list[str] = field(default_factory=list)
    quotes: list[Quote] = field(default_factory=list)
    extra: str = ""  # for D: who it more likely was
    bad: list[str] = field(default_factory=list)  # Quote lines out of shape

    @property
    def ident(self) -> str:
        return f"{self.kind}{self.number}"

    def get(self, key: str) -> list[str]:
        values = []
        for line in self.lines:
            match = FIELD.match(line)
            if match and match.group(1).strip().lower() == key.lower():
                values.append(match.group(2).strip())
        return values

    def header(self) -> str:
        if self.kind == "K":
            return f"## {self.ident}. {self.title}  (kind: {self.tag})"
        if self.kind == "D":
            return f"## {self.ident}. [L{self.tag}] labelled {self.title}, more likely {self.extra}"
        return f"## {self.ident}. {self.title}  [{self.tag}]"

    def render(self) -> str:
        return "\n".join([self.header(), *self.lines]).rstrip()


def parse_blocks(text: str, source: str) -> list[Block]:
    blocks: list[Block] = []
    current: Block | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        fact, doubt, claim = FACT_HEADER.match(line), DOUBT_HEADER.match(line), CLAIM_HEADER.match(line)
        if fact:
            current = Block("K", int(fact.group(1)), fact.group(2), fact.group(3))
        elif doubt:
            current = Block("D", int(doubt.group(1)), doubt.group(3), doubt.group(2), extra=doubt.group(4))
        elif claim:
            current = Block("C", int(claim.group(1)), claim.group(2), claim.group(3))
        elif LOOKS_LIKE_BLOCK.match(line):
            raise FormatError(f"{source}: this header is not in the format, so its block would be lost: {line!r}")
        elif line.startswith("#"):
            current = None
            continue
        elif current is not None and line.startswith("- "):
            line = line.replace("\u201c", '"').replace("\u201d", '"')
            current.lines.append(line)
            quote = QUOTE.match(line)
            if quote:
                start = int(quote.group(1))
                current.quotes.append(Quote(start, int(quote.group(2) or start), quote.group(3), quote.group(4)))
            elif LOOKS_LIKE_QUOTE.match(line) and not NO_QUOTE.match(line):
                current.bad.append(line)
            continue
        else:
            continue
        blocks.append(current)
    return blocks


@dataclass
class CheckFile:
    path: Path
    name: str
    claims: list[Block]
    statuses: dict[int, tuple[str, int | None]]
    marked_twice: list[int] = field(default_factory=list)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise FormatError(f"{path}: not UTF-8 text ({error.reason}). Save it as UTF-8 and run again.") from error


def read_check(path: Path) -> CheckFile:
    text = read_text(path)
    title = next((m.group(1) for m in map(SUMMARY_TITLE.match, text.splitlines()) if m), path.stem)
    claims = [b for b in parse_blocks(text, str(path)) if b.kind == "C"]
    statuses: dict[int, tuple[str, int | None]] = {}
    twice: list[int] = []
    for line in text.splitlines():
        match = FACT_STATUS.match(line.rstrip())
        if match:
            ref = int(match.group(3)) if match.group(3) else None
            if int(match.group(1)) in statuses:
                twice.append(int(match.group(1)))
            statuses[int(match.group(1))] = (match.group(2), ref)
    return CheckFile(path, title, claims, statuses, twice)


def read_facts(path: Path) -> tuple[list[Block], list[Block]]:
    blocks = parse_blocks(read_text(path), str(path))
    return [b for b in blocks if b.kind == "K"], [b for b in blocks if b.kind == "D"]


# ---------------------------------------------------------------- verifying

def plain(text: str) -> str:
    """Lower case, letters and digits only, single spaces: the word-for-word comparison."""
    text = text.lower().replace("\u2019", "'").replace("\u2018", "'")
    text = re.sub(r"(?<=\w)'(?=\w)", "", text)
    return " ".join(re.sub(r"[^\w]+", " ", text).split())


def check_quote(quote: Quote, lines: dict[int, Line]) -> str | None:
    """None if the quote is on its lines, word for word and from that speaker, else why not."""
    span = range(quote.start, quote.end + 1)
    if quote.end < quote.start or quote.end - quote.start > 5:
        return "the line range must run forwards and cover at most 6 lines"
    missing = [n for n in span if n not in lines]
    if missing:
        return f"L{missing[0]} is not in the transcript"
    speakers = {lines[n].speaker.lower() for n in span}
    if speakers != {quote.speaker.lower()}:
        on_line = ", ".join(sorted({lines[n].speaker for n in span}))
        return f"credited to {quote.speaker}, but the line says {on_line}"
    words = plain(quote.words)
    if not words:
        return "the quote is empty"
    # Whole words only, so "we can" is never found inside "we cannot".
    if f" {words} " not in f" {plain(' '.join(lines[n].text for n in span))} ":
        return "these words are not on the cited line"
    return None


LABEL_ONLY = re.compile(r"^(\*\*|__)[^*_]+\1:?$")


def summary_lines(text: str) -> list[str]:
    """Every line of a summary that carries a claim. Only headings and bare labels are left out:
    a line starting "#", a label ending in a colon ("Next steps:"), or a label that is all bold."""
    kept = []
    for raw in text.splitlines():
        line = re.sub(r"^(?:[-*+\u2022]|\d+[.)])\s+", "", raw.strip())
        if not plain(line) or line.startswith("#") or line.rstrip("*_ ").endswith(":") or LABEL_ONLY.match(line):
            continue
        kept.append(line)
    return kept


def covered(line: str, fragments: list[str]) -> float:
    words = plain(line).split()
    hit = [False] * len(words)
    for fragment in fragments:
        piece = plain(fragment).split()
        if not piece:
            continue
        for i in range(len(words) - len(piece) + 1):
            if words[i : i + len(piece)] == piece:
                for j in range(i, i + len(piece)):
                    hit[j] = True
    return sum(hit) / len(words) if words else 1.0


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def verify_facts(lines: dict[int, Line], facts: list[Block], doubts: list[Block]) -> list[str]:
    problems = []
    for block in facts:
        if block.tag not in KINDS:
            problems.append(f"{block.ident}: kind '{block.tag}' is not one of {', '.join(KINDS)}")
        if not block.quotes:
            problems.append(f"{block.ident}: no quote")
    for block in doubts:
        if int(block.tag) not in lines:
            problems.append(f"{block.ident}: L{block.tag} is not in the transcript")
        elif lines[int(block.tag)].speaker.lower() != block.title.lower():
            problems.append(f"{block.ident}: L{block.tag} is labelled {lines[int(block.tag)].speaker}, not {block.title}")
    for block in facts + doubts:
        for quote in block.quotes:
            why = check_quote(quote, lines)
            if why:
                problems.append(f"{block.ident}: quote {quote.cite()}: {why}")
    for kind, blocks in (("K", facts), ("D", doubts)):
        numbers = [b.number for b in blocks]
        if numbers != list(range(1, len(numbers) + 1)):
            problems.append(f"{kind} numbers must run 1, 2, 3 with no gaps or repeats")
    return problems


def verify_check(
    lines: dict[int, Line],
    facts: list[Block],
    doubts: list[Block],
    summary: str,
    check: CheckFile,
    by_hand_allowed: bool = False,
) -> tuple[list[str], list[str]]:
    """Problems that fail the check, and quotes marked to check by hand.

    A claim may carry "Quote check: failed" only after the checker has had its one send-back: the
    skill adds it, and only on a verify run with by_hand_allowed. Anywhere else it is a problem.
    """
    claims_by_number = {c.number: c for c in check.claims}
    problems: list[str] = []
    hand: list[str] = []
    doubt_lines = {int(d.tag): d.ident for d in doubts}
    doubt_ids = set(doubt_lines.values())
    claim_ids = {c.number for c in check.claims}
    summary_plain = [plain(line) for line in summary_lines(summary)]
    fragments: list[str] = []
    if not check.claims:
        problems.append("no claims")
    numbers = [c.number for c in check.claims]
    if numbers != list(range(1, len(numbers) + 1)):
        problems.append("C numbers must run 1, 2, 3 with no gaps or repeats")
    for claim in check.claims:
        where = claim.ident
        if claim.tag not in VERDICTS:
            problems.append(f"{where}: verdict '{claim.tag}' is not one of {', '.join(VERDICTS)}")
        froms = [unquote(v) for v in claim.get("From")]
        if not froms:
            problems.append(f"{where}: no From line")
        for value in froms:
            fragments.append(value)
            if not any(plain(value) and plain(value) in line for line in summary_plain):
                problems.append(f'{where}: From "{value}" is not in the summary')
        failures = claim.get("Failures")
        if len(failures) != 1:
            problems.append(f"{where}: needs exactly one Failures line")
        else:
            for kind in failures_of(claim):
                if kind not in FAILURES:
                    problems.append(f"{where}: failure type '{kind}' is not one of {', '.join(FAILURES)}")
        labels = claim.get("Label")
        label_ref = None
        if len(labels) != 1:
            problems.append(f"{where}: needs exactly one Label line")
        else:
            match = re.fullmatch(r"ok|doubtful \((D\d+)\)", labels[0])
            if not match:
                problems.append(f"{where}: Label must be 'ok' or 'doubtful (D1)'")
            elif match.group(1):
                label_ref = match.group(1)
                if label_ref not in doubt_ids:
                    problems.append(f"{where}: {label_ref} is not in the doubtful labels")
        if failures_of(claim) and not claim.get("Note"):
            problems.append(f"{where}: a claim with failures needs a Note saying what the transcript says instead")
        for line in claim.bad:
            problems.append(f"{where}: this Quote line is not in the format, so it was not checked: {line}")
        cited = {n for q in claim.quotes for n in range(q.start, q.end + 1)}
        if label_ref and label_ref not in {doubt_lines[n] for n in cited if n in doubt_lines}:
            problems.append(f"{where}: Label says {label_ref}, but no quote cites that line")
        if claim.tag in ("said", "inferred", "contradicted") and not claim.quotes:
            problems.append(f"{where}: a '{claim.tag}' claim needs a quote")
        if any(NO_QUOTE.match(l) for l in claim.lines) and claim.quotes:
            problems.append(f"{where}: has both quotes and 'Quote: none'")
        by_hand = any(v.lower() == "failed" for v in claim.get("Quote check"))
        if by_hand and not by_hand_allowed:
            problems.append(f"{where}: 'Quote check: failed' is added by the skill after the send-back, never by a checker")
        for quote in claim.quotes:
            why = check_quote(quote, lines)
            if why and by_hand and by_hand_allowed:
                hand.append(f"{check.name} {where}: {quote.cite()}: {why}")
            elif why:
                problems.append(f"{where}: quote {quote.cite()}: {why}")
            for n in range(quote.start, quote.end + 1):
                if n in doubt_lines and label_ref is None and not why:
                    problems.append(f"{where}: quotes L{n}, a doubtful label ({doubt_lines[n]}), so its Label must say so")
    for line in summary_lines(summary):
        if covered(line, fragments) < 1.0:
            problems.append(f'summary line not checked: "{line}"')
    for fact in facts:
        status = check.statuses.get(fact.number)
        if status is None:
            problems.append(f"{fact.ident}: not marked carried, carried wrongly or missing")
            continue
        state, ref = status
        if state == "missing" and ref is not None:
            problems.append(f"{fact.ident}: a missing fact names no claim")
        if state != "missing" and (ref is None or ref not in claim_ids):
            problems.append(f"{fact.ident}: '{state}' must name a claim in this file, as (C3)")
        elif state == "carried wrongly" and not failures_of(claims_by_number[ref]):
            problems.append(f"{fact.ident}: carried wrongly by C{ref}, so C{ref} must carry the failure type that says how")
        elif state == "carried" and (failures_of(claims_by_number[ref]) or claims_by_number[ref].tag not in ("said", "inferred")):
            problems.append(f"{fact.ident}: C{ref} has failures or is not supported, so the fact is carried wrongly, not carried")
    for twice in sorted(set(check.marked_twice)):
        problems.append(f"K{twice}: marked more than once")
    for extra in sorted(set(check.statuses) - {f.number for f in facts}):
        problems.append(f"K{extra}: marked, but not in the key facts")
    return problems, hand


def failures_of(claim: Block) -> list[str]:
    values = claim.get("Failures")
    if not values or values[0].strip().lower() in ("none", ""):
        return []
    return [part.strip().lower() for part in values[0].split(",") if part.strip()]


# ---------------------------------------------------------------- report

def tally(check: CheckFile) -> Counter:
    counts: Counter = Counter()
    for claim in check.claims:
        counts[claim.tag] += 1
        for kind in failures_of(claim):
            counts[kind] += 1
    counts[LEFT_OUT] = sum(1 for state, _ in check.statuses.values() if state == "missing")
    return counts


def report(facts: list[Block], doubts: list[Block], checks: list[CheckFile]) -> str:
    names = [c.name for c in checks]
    counts = [tally(c) for c in checks]
    out = ["# Call summary check", ""]

    hand = [
        f"- {c.name} {claim.ident}: {claim.title}"
        for c in checks
        for claim in c.claims
        if any(v.lower() == "failed" for v in claim.get("Quote check"))
    ]
    if hand:
        out += ["## Quote could not be verified, check by hand", "", *hand, ""]

    out += ["## Counts", "", "| | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    out.append("| claims | " + " | ".join(str(len(c.claims)) for c in checks) + " |")
    for row in (*VERDICTS, *FAILURES, LEFT_OUT):
        out.append(f"| {row} | " + " | ".join(str(n[row]) for n in counts) + " |")
    out.append("")

    out += ["## Confirm with a person before saving", ""]
    doubt_lines = {int(d.tag): d.ident for d in doubts}
    for fact in facts:
        on_doubt = sorted({doubt_lines[n] for q in fact.quotes for n in range(q.start, q.end + 1) if n in doubt_lines})
        if fact.tag not in CONFIRM_KINDS and not on_doubt:
            continue
        where = "; ".join(f"{c.name}: {status_text(c, fact.number)}" for c in checks)
        label = f"; rests on a doubtful label ({', '.join(on_doubt)})" if on_doubt else ""
        out.append(f"- **{fact.ident}** {fact.title} ({where}{label})")
    for check in checks:
        for claim in check.claims:
            reasons = []
            label = (claim.get("Label") or ["ok"])[0]
            if label.startswith("doubtful"):
                reasons.append(f"rests on a {label.replace('(', 'label (')}")
            failures = failures_of(claim)
            if "tone-read-as-sincere" in failures:
                reasons.append("may have been said for effect")
            if "intention-as-done" in failures or "owner-or-date-wrong" in failures:
                reasons.append("a next step the summary got wrong")
            if reasons:
                out.append(f"- **{check.name} {claim.ident}** {claim.title} ({'; '.join(reasons)})")
    if out[-1] == "":
        out.append("Nothing to confirm.")
    out.append("")

    out += ["## Doubtful labels", ""]
    out += [d.render().replace("## D", "### D", 1) + "\n" for d in doubts] or ["None found.", ""]

    for check in checks:
        out += [f"## Summary: {check.name}", ""]
        out += [claim.render().replace("## C", "### C", 1) + "\n" for claim in check.claims]

    out += ["## Key facts", "", "| | Kind | Fact | " + " | ".join(names) + " |", "|---|---|---|" + "---|" * len(names)]
    for fact in facts:
        cells = " | ".join(status_text(c, fact.number) for c in checks)
        out.append(f"| {fact.ident} | {fact.tag} | {fact.title} | {cells} |")
    out.append("")
    return "\n".join(out)


def status_text(check: CheckFile, number: int) -> str:
    state, ref = check.statuses.get(number, ("not marked", None))
    return f"{state} ({'C' + str(ref)})" if ref else state


# ---------------------------------------------------------------- commands

def main(argv: list[str]) -> int:
    usage = "\n".join(line.strip() for line in __doc__.strip().splitlines()[3:6])
    if not argv or argv[0] not in ("number", "verify", "report"):
        print(usage, file=sys.stderr)
        return 2
    command, args = argv[0], argv[1:]
    try:
        if command == "number" and len(args) == 2:
            source, out = Path(args[0]), Path(args[1])
            lines = number(read_transcript(source))
            if not lines:
                print(f"error: no transcript lines found in {source}", file=sys.stderr)
                return 1
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text("\n".join(line.render() for line in lines) + "\n", encoding="utf-8")
            speakers = Counter(line.speaker for line in lines)
            print(f"{len(lines)} lines written to {out}")
            for speaker, count in speakers.most_common():
                print(f"  {speaker}: {count} lines")
            if UNLABELLED in speakers:
                print(f"warning: {speakers[UNLABELLED]} lines have no speaker label")
            return 0
        by_hand_allowed = "--by-hand" in args
        args = [a for a in args if a != "--by-hand"]
        if command == "verify" and (len(args) == 2 and not by_hand_allowed or len(args) == 4):
            lines = read_lines(Path(args[0]))
            facts, doubts = read_facts(Path(args[1]))
            problems = verify_facts(lines, facts, doubts)
            hand: list[str] = []
            if len(args) == 4:
                summary = read_text(Path(args[2]))
                more, hand = verify_check(lines, facts, doubts, summary, read_check(Path(args[3])), by_hand_allowed)
                problems += more
            for item in hand:
                print(f"check by hand: {item}")
            if problems:
                print("\n".join(problems))
                print(f"\n{len(problems)} problems")
                return 1
            print("ok")
            return 0
        if command == "report" and len(args) >= 3:
            facts, doubts = read_facts(Path(args[1]))
            checks = [read_check(Path(p)) for p in args[2:]]
            out = Path(args[0])
            out.write_text(report(facts, doubts, checks), encoding="utf-8")
            for check, counts in zip(checks, map(tally, checks)):
                failures = sum(counts[k] for k in FAILURES)
                print(f"{check.name}: {len(check.claims)} claims, {failures} failures on claims, {counts[LEFT_OUT]} key facts left out")
            print(f"report written to {out}")
            return 0
    except (OSError, FormatError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(usage, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
