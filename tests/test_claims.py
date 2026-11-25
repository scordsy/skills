"""Tests for check-claims' claims.py: sentence numbering, the claims file, the record format, each
shape rule in stage 4 of the spec, the quote check, what goes to the checker, and the report. No network.

Every expected value here is written by hand from docs/specs/check-claims.md, never copied from the
script's output or imported from its constants.

The script is the skill's own, at skills/check-claims/scripts/claims.py."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "check-claims" / "scripts" / "claims.py"
SAMPLE = ROOT / "tests" / "check-claims" / "sample-a4"
spec = importlib.util.spec_from_file_location("claims", SCRIPT)
assert spec and spec.loader
claims = importlib.util.module_from_spec(spec)
# Dataclasses look their module up in sys.modules, so register it before running it.
sys.modules[spec.name] = claims
spec.loader.exec_module(claims)

Page = claims.Page

# From the spec, "Problem types": the ten, and how "Which verdict a problem type sits on" splits them.
THE_TEN = [
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
]
DEPART_FROM_THE_PAGE = ["number-wrong", "base-dropped", "wrong-subject", "strength-changed", "source-mislabelled", "misquoted"]
ABOUT_THE_SOURCE = ["second-hand", "out-of-date", "publisher-disagrees", "page-gone"]
# What a record must also carry for each type, so a test of one rule does not trip another.
NEEDS = {
    "out-of-date": '  - E8 | newer | https://acme.example/survey-2026 | "69% of buyers read reviews"\n',
    "publisher-disagrees": '  - E9 | page | https://acme.example/summary | "71% of buyers read reviews"\n',
    "page-gone": "- Page gone: https://acme.example/old-survey now loads the home page\n",
}


def fake(pages: dict[str, Page], calls: list[str] | None = None):
    """A fetch that serves pages from a dict, fails for anything else, and notes every request."""

    def get(url: str) -> Page:
        if calls is not None:
            calls.append(url)
        if url in pages:
            return pages[url]
        return Page(url=url, error="no such host")

    return get


def html_page(url: str, body: str) -> Page:
    return Page(url=url, status=200, final=url, kind="text/html", text=body)


def run_main(args: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = claims.main(args)
    return code, out.getvalue(), err.getvalue()


# ---------------------------------------------------------------- stage 1: number


class NumberTests(unittest.TestCase):
    def number_file(self, name: str, content: str | bytes) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            if isinstance(content, bytes):
                path.write_bytes(content)
            else:
                path.write_text(content, encoding="utf-8")
            return claims.number(claims.read_draft(path))

    def test_markdown_headings_and_list_items_are_numbered_as_sentences(self):
        draft = (
            "# Is it worth it? A look at the cost\n"
            "\n"
            "ABM costs money. It also takes time!\n"
            "\n"
            "1. **Your deals are large enough.** Above $50,000, it gets easier.\n"
            "- A single buyer does not need it.\n"
            "\n"
            "---\n"
            "\n"
            "*A note on sources: check them.*\n"
        )
        self.assertEqual(
            self.number_file("draft.md", draft),
            [
                "# Is it worth it? A look at the cost",
                "ABM costs money.",
                "It also takes time!",
                "1. **Your deals are large enough.**",
                "Above $50,000, it gets easier.",
                "- A single buyer does not need it.",
                "*A note on sources: check them.*",
            ],
        )

    def test_text_file_with_hard_wrapped_lines(self):
        draft = "Sales rose 3.5% in 2025, said Dr. Shah of Acme Inc. in March.\nThe firm, e.g. its UK arm, grew\nfaster. Why?\n\nNobody knows.\n"
        self.assertEqual(
            self.number_file("draft.txt", draft),
            [
                "Sales rose 3.5% in 2025, said Dr. Shah of Acme Inc. in March.",
                "The firm, e.g. its UK arm, grew faster.",
                "Why?",
                "Nobody knows.",
            ],
        )

    def test_a_quotation_keeps_its_closing_mark(self):
        self.assertEqual(
            claims.number('She said "we will refund it." Then she left.'),
            ['She said "we will refund it."', "Then she left."],
        )

    def test_docx_paragraphs_stand_alone(self):
        xml = (
            '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="x"><w:body>'
            "<w:p><w:r><w:t>Why onboarding matters</w:t></w:r></w:p>"
            '<w:p><w:r><w:t xml:space="preserve">Acme found 74% of buyers read reviews. </w:t></w:r><w:r><w:t>That is a lot.</w:t></w:r></w:p>'
            "<w:p><w:r><w:t>Tom &amp; Co agree</w:t></w:r></w:p>"
            "</w:body></w:document>"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "draft.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", xml)
            sentences = claims.number(claims.read_draft(path))
        self.assertEqual(
            sentences,
            ["Why onboarding matters", "Acme found 74% of buyers read reviews.", "That is a lot.", "Tom & Co agree"],
        )

    def test_a_pdf_is_refused_with_a_way_round(self):
        for name, content in (("draft.pdf", b"anything"), ("draft.txt", b"%PDF-1.7 rest")):
            with self.subTest(name=name), self.assertRaises(claims.FormatError) as caught:
                self.number_file(name, content)
            self.assertIn("Save the draft as .docx, .txt or .md, or paste the text", str(caught.exception))

    def test_other_formats_are_refused(self):
        with self.assertRaises(claims.FormatError) as caught:
            self.number_file("deck.pptx", b"PK\x03\x04 slides")
        self.assertIn("or paste the text", str(caught.exception))

    def test_the_numbered_draft_is_one_sentence_per_line(self):
        self.assertEqual(claims.write_lines(["# A heading", "A sentence."]), "[S1] # A heading\n[S2] A sentence.\n")

    def test_the_command_writes_the_file_and_prints_the_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, out = Path(tmp) / "draft.md", Path(tmp) / "run" / "draft-lines.md"
            source.write_text("# Title\n\nOne. Two. Three.\n", encoding="utf-8")
            code, printed, _ = run_main(["number", str(source), str(out)])
            self.assertEqual(code, 0)
            self.assertIn("4 sentences", printed)
            self.assertEqual(out.read_text(encoding="utf-8"), "[S1] # Title\n[S2] One.\n[S3] Two.\n[S4] Three.\n")
            self.assertEqual(claims.read_lines(out), {1: "# Title", 2: "One.", 3: "Two.", 4: "Three."})

    def test_no_arguments_prints_how_to_use_it(self):
        code, _, err = run_main([])
        self.assertEqual(code, 2)
        for command in ("number", "verify", "report"):
            self.assertIn(f"claims.py {command}", err)

    def test_an_unknown_command_prints_how_to_use_it(self):
        self.assertEqual(run_main(["publish", "x"])[0], 2)


# ---------------------------------------------------------------- stage 2: the claims file

LINES = (
    "[S1] # Why reviews matter\n"
    "[S2] Acme's 2025 survey found that 74% of buyers read reviews.\n"
    "[S3] That is a lot.\n"
    "[S4] Our product cuts onboarding time by half.\n"
    '[S5] Jo Bloggs, a buyer at Initech, said she "never reads vendor email".\n'
    "[S6] Bigfirm says 9 in 10 deals involve a committee.\n"
    "[S7] Acme was founded in 2010, and Acme is now part of Globex.\n"
    "[S8] Nobody has counted how many buyers skim.\n"
    "[S9] Its newest report says most buyers will switch.\n"
)

CLAIMS = """# Claims

No claim: S1, S3

## C01 | S2 | statistic
- Claim: Acme's 2025 survey found that 74% of buyers read reviews.
- Draft words: "74% of buyers read reviews"
- Source given: Acme's 2025 survey
- Trace: yes

## C02 | S7 | event
- Claim: Acme was founded in 2010.
- Draft words: "Acme was founded in 2010"
- Source given: none
- Trace: yes

## C03 | S8 | statistic
- Claim: Nobody has counted how many buyers skim.
- Draft words: "Nobody has counted how many buyers skim"
- Source given: none
- Trace: yes

## C04 | S6 | statistic
- Claim: Bigfirm says 9 in 10 deals involve a buying committee.
- Draft words: "9 in 10 deals involve a committee"
- Source given: Bigfirm
- Trace: yes

## C05 | S4 | company-fact
- Claim: The user's product cuts onboarding time by half.
- Draft words: "Our product cuts onboarding time by half"
- Source given: none
- Trace: no, own company

## C06 | S5 | quotation
- Claim: Jo Bloggs of Initech said she never reads vendor email.
- Draft words: "never reads vendor email"
- Source given: none
- Trace: no, named person

## C07 | S7 | company-fact
- Claim: Acme is now part of Globex.
- Draft words: "Acme is now part of Globex"
- Source given: none
- Trace: yes

## C08 | S9 | citation
- Claim: Acme's newest report says most buyers will switch.
- Draft words: "most buyers will switch"
- Source given: Acme's newest report
- Trace: yes
"""


def sentences() -> dict[int, str]:
    return {int(line[2:line.index("]")]): line[line.index("]") + 2:] for line in LINES.splitlines()}


def claim_problems(text: str) -> list[str]:
    listed, no_claim = claims.parse_claims(text)
    return claims.check_claims(sentences(), listed, no_claim) + claims.added_claim_problems(sentences(), listed)


class ClaimsFileTests(unittest.TestCase):
    def test_a_file_that_covers_every_sentence_passes(self):
        self.assertEqual(claim_problems(CLAIMS), [])

    def test_what_the_reader_wrote_is_read_back(self):
        listed, no_claim = claims.parse_claims(CLAIMS)
        self.assertEqual([c.id for c in listed], ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08"])
        self.assertEqual(sorted(no_claim), [1, 3])
        first = listed[0]
        self.assertEqual((first.sentence, first.kind, first.words, first.source), (2, "statistic", "74% of buyers read reviews", "Acme's 2025 survey"))
        self.assertEqual([c.trace for c in listed[3:6]], ["yes", "own-company", "named-person"])

    def test_a_sentence_with_neither_a_claim_nor_a_no_claim_mark_fails(self):
        problems = claim_problems(CLAIMS.replace("No claim: S1, S3", "No claim: S1"))
        self.assertEqual(len(problems), 1)
        self.assertIn("S3 has neither a claim nor a no claim mark", problems[0])

    def test_no_claim_marks_can_be_ranges(self):
        _, no_claim = claims.parse_claims("No claim: S1-S3, S5, S8-9\n")
        self.assertEqual(sorted(no_claim), [1, 2, 3, 5, 8, 9])

    def test_a_mark_the_script_cannot_read_is_refused(self):
        for bad in ("No claim: 3", "No claim: S6-S2", "No claim: the rest"):
            with self.subTest(bad=bad), self.assertRaises(claims.FormatError):
                claims.parse_claims(bad + "\n")

    def test_a_sentence_cannot_be_both(self):
        problems = claim_problems(CLAIMS.replace("No claim: S1, S3", "No claim: S1-S3"))
        self.assertTrue(any("S2 is marked no claim and also carries C01" in p for p in problems), problems)

    def test_a_claim_must_cite_a_real_sentence(self):
        problems = claim_problems(CLAIMS.replace("## C03 | S8 |", "## C03 | S80 |"))
        self.assertTrue(any("C03" in p and "S80 is not a sentence" in p for p in problems), problems)

    def test_kind_is_one_of_the_five(self):
        for kind in ("statistic", "quotation", "company-fact", "event", "citation"):
            with self.subTest(kind=kind):
                self.assertEqual(claim_problems(CLAIMS.replace("## C01 | S2 | statistic", f"## C01 | S2 | {kind}")), [])
        problems = claim_problems(CLAIMS.replace("## C01 | S2 | statistic", "## C01 | S2 | opinion"))
        self.assertTrue(any("C01" in p and "kind must be one of" in p for p in problems), problems)

    def test_trace_must_be_stated(self):
        problems = claim_problems(CLAIMS.replace("- Trace: no, own company", "- Trace: maybe"))
        self.assertTrue(any("C05" in p and "Trace" in p for p in problems), problems)

    def test_a_claim_number_cannot_be_used_twice(self):
        problems = claim_problems(CLAIMS.replace("## C02 | S7 | event", "## C01 | S7 | event"))
        self.assertTrue(any("used twice" in p for p in problems), problems)

    def test_a_bad_heading_is_refused(self):
        with self.assertRaises(claims.FormatError):
            claims.parse_claims("## Claim 1: statistic\n")

    def test_added_rule_draft_words_must_be_in_the_sentence(self):
        problems = claim_problems(CLAIMS.replace('"74% of buyers read reviews"', '"47% of buyers read reviews"'))
        self.assertEqual(len(problems), 1)
        self.assertIn("C01", problems[0])
        self.assertIn("draft words are not in S2", problems[0])


# ---------------------------------------------------------------- stage 3: records

SUPPORTED = """## C01
- Verdict: supported
- Problems: none
- First publisher: Acme Research
- Published: 3 March 2025
- Finding: Acme's 2025 survey report says 74% of buyers read reviews.
- Evidence:
  - E1 | page | https://acme.example/survey-2025 | "74% of buyers read reviews"
"""

DIFFERS = """## C02
- Verdict: differs
- Problems: number-wrong
- First publisher: Acme
- Published: not shown
- Finding: Acme's own history page says it was founded in 2012, not 2010.
- Use instead: Acme was founded in 2012
- Evidence:
  - E1 | page | https://acme.example/about | "Founded in 2012 by two engineers"
"""

NO_SOURCE = """## C03
- Verdict: no-source
- Problems: none
- Finding: No first publisher's page was found. The line appears only on pages that repeat it.
- Searches:
  - "how many buyers skim" survey
  - buyers skim vendor content study
"""

COULD_NOT_OPEN = """## C04
- Verdict: could-not-open
- Problems: none
- First publisher: Bigfirm
- Finding: Bigfirm's report page asks for a sign-up before it shows the figure.
- Address: https://bigfirm.example/report
- In the way: a sign-up form
- Look for: the 9 in 10 figure, whether it counts all deals or only large ones, and the report's date
"""

OUT_OF_DATE_NOW = """## C07
- Verdict: differs
- Problems: out-of-date
- First publisher: Globex
- Published: 4 September 2025
- Finding: Globex sold Acme in 2025, so Acme is no longer part of it.
- Use instead: Acme, which Globex sold to Initrode in September 2025
- Evidence:
  - E1 | newer | https://globex.example/news/sale | "Globex has completed the sale of Acme to Initrode"
"""

SUPPORTED_FIRST_PASS = """## C08
- Verdict: supported
- Problems: none
- First publisher: Acme Research
- Published: 1 May 2026
- Finding: Acme's 2026 report says most buyers will switch.
- Evidence:
  - E1 | page | https://acme.example/report-2026 | "most buyers will switch"
"""

CHECK_C08 = """## C08
- Verdict: differs
- Problems: strength-changed
- First publisher: Acme Research
- Published: 1 May 2026
- Finding: The report says most buyers say they may switch, which is a hedge the draft makes firm.
- Use instead: most buyers say they may switch (Acme, 2026)
- Check notes: The first pass quoted a pull-out heading, not the finding.
- Evidence:
  - E1 | page | https://acme.example/report-2026 | "most buyers say they may switch"
"""


def problems_of(text: str) -> list[str]:
    (record,) = claims.parse_records(text, "research-1.md")
    return claims.check_record(record)


def stage4_of(text: str) -> list[str]:
    (record,) = claims.parse_records(text, "research-1.md")
    return claims.stage4_problems(record)


def with_type(record: str, name: str, extra: str = "") -> str:
    """The record carrying one problem type, with whatever that type must bring along."""
    head, evidence = record.split("- Evidence:\n") if "- Evidence:\n" in record else (record, "")
    head = head.replace("- Problems: none", f"- Problems: {name}")
    need = NEEDS.get(name, "")
    if need.startswith("- "):
        head += need
    elif need:
        evidence += need
    return head + extra + ("- Evidence:\n" + evidence if evidence else "")


class RecordFormatTests(unittest.TestCase):
    def test_the_four_example_records_pass(self):
        for text in (SUPPORTED, DIFFERS, NO_SOURCE, COULD_NOT_OPEN, OUT_OF_DATE_NOW, CHECK_C08):
            with self.subTest(record=text.splitlines()[0]):
                self.assertEqual(problems_of(text), [])

    def test_a_record_is_read_back(self):
        (record,) = claims.parse_records(SUPPORTED, "research-1.md")
        self.assertEqual((record.id, record.verdict, record.problems), ("C01", "supported", []))
        (item,) = record.evidence
        self.assertEqual((item.ref, item.role, item.url, item.quote), ("E1", "page", "https://acme.example/survey-2025", "74% of buyers read reviews"))
        (searched,) = claims.parse_records(NO_SOURCE, "research-1.md")
        self.assertEqual(searched.searches, ['"how many buyers skim" survey', "buyers skim vendor content study"])

    def test_the_verdict_is_one_of_the_four(self):
        for verdict in ("supported", "differs", "no-source", "could-not-open"):
            self.assertFalse(any("verdict must be" in p for p in problems_of(SUPPORTED.replace("Verdict: supported", f"Verdict: {verdict}"))))
        for verdict in ("confirmed", "unverifiable", "wrong", ""):
            with self.subTest(verdict=verdict):
                problems = problems_of(SUPPORTED.replace("Verdict: supported", f"Verdict: {verdict}"))
                self.assertEqual(len(problems), 1)
                self.assertIn("verdict must be one of supported, differs, no-source, could-not-open", problems[0])

    def test_a_bad_evidence_line_is_refused(self):
        with self.assertRaises(claims.FormatError):
            claims.parse_records(SUPPORTED.replace('| "74% of buyers read reviews"', "| 74% of buyers read reviews"), "research-1.md")

    def test_an_evidence_line_needs_a_role_a_web_address_and_two_words(self):
        for change, message in (
            (("| page |", "| proof |"), "page or newer"),
            (("https://acme.example/survey-2025", "acme.example/survey-2025"), "not a web address"),
            (('"74% of buyers read reviews"', '"74%"'), "at least two words"),
        ):
            with self.subTest(message=message):
                self.assertTrue(any(message in p for p in problems_of(SUPPORTED.replace(*change))))


class Stage4RuleTests(unittest.TestCase):
    """One passing and one failing record for each rule the spec lists under 'Stage 4: Verify'."""

    def failing(self, text: str, message: str) -> None:
        problems = stage4_of(text)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(message, problems[0])

    def test_a_differs_needs_a_problem_type(self):
        self.assertEqual(stage4_of(DIFFERS), [])
        self.failing(DIFFERS.replace("Problems: number-wrong", "Problems: none"), "a differs needs at least one problem type")

    def test_a_supported_needs_evidence(self):
        self.assertEqual(stage4_of(SUPPORTED), [])
        self.failing(SUPPORTED.split("- Evidence:")[0], "a supported needs evidence")

    def test_a_newer_quote_alone_does_not_support_a_claim(self):
        self.failing(SUPPORTED.replace("| page |", "| newer |"), "a supported needs evidence")

    def test_a_no_source_lists_its_searches(self):
        self.assertEqual(stage4_of(NO_SOURCE), [])
        self.failing(NO_SOURCE.split("- Searches:")[0], "lists the searches tried")
        self.failing(NO_SOURCE.split("- Searches:")[0] + "- Searches: none\n", "lists the searches tried")

    def test_each_of_the_ten_types_is_known(self):
        for name in DEPART_FROM_THE_PAGE:
            with self.subTest(name=name):
                self.assertEqual(stage4_of(DIFFERS.replace("number-wrong", name)), [])
        for name in ABOUT_THE_SOURCE:
            with self.subTest(name=name):
                self.assertEqual(stage4_of(with_type(SUPPORTED, name)), [])
        self.assertEqual(sorted(DEPART_FROM_THE_PAGE + ABOUT_THE_SOURCE), sorted(THE_TEN))

    def test_a_type_that_is_not_one_of_the_ten_fails(self):
        # The two names ADR 0020 retired, a check-account-list type, and a made-up one.
        for name in ("overstated", "dead-link", "wrong-fit", "made-up"):
            with self.subTest(name=name):
                self.failing(DIFFERS.replace("number-wrong", f"number-wrong, {name}"), f"not one of the ten problem types: {name}")

    def test_out_of_date_needs_a_quote_for_the_newer_figure(self):
        self.assertEqual(stage4_of(with_type(SUPPORTED, "out-of-date")), [])
        self.assertEqual(stage4_of(OUT_OF_DATE_NOW), [])
        self.failing(SUPPORTED.replace("Problems: none", "Problems: out-of-date"), "out-of-date needs a quote marked newer")
        self.failing(OUT_OF_DATE_NOW.replace("| newer |", "| page |"), "out-of-date needs a quote marked newer")

    def test_publisher_disagrees_needs_two_quotes(self):
        self.assertEqual(stage4_of(with_type(SUPPORTED, "publisher-disagrees")), [])
        self.failing(SUPPORTED.replace("Problems: none", "Problems: publisher-disagrees"), "publisher-disagrees needs two quotes")
        same_twice = SUPPORTED.replace("Problems: none", "Problems: publisher-disagrees") + '  - E2 | page | https://acme.example/survey-2025 | "74% of buyers read reviews"\n'
        self.failing(same_twice, "publisher-disagrees needs two quotes")

    def test_page_gone_names_the_address(self):
        self.assertEqual(stage4_of(with_type(SUPPORTED, "page-gone")), [])
        self.failing(SUPPORTED.replace("Problems: none", "Problems: page-gone"), "page-gone needs a Page gone line naming the address")
        no_address = SUPPORTED.replace("Problems: none", "Problems: page-gone\n- Page gone: the old survey page now loads the home page")
        self.failing(no_address, "page-gone needs a Page gone line naming the address")

    def test_a_supported_that_departs_from_the_page_says_why_it_is_still_supported(self):
        why = "- Still supported: the draft drops 'B2B', and every buyer the survey asked was a B2B buyer\n"
        for name in DEPART_FROM_THE_PAGE:
            with self.subTest(name=name):
                self.assertEqual(stage4_of(with_type(SUPPORTED, name, why)), [])
                self.failing(with_type(SUPPORTED, name), f"a supported carrying {name} needs a Still supported line")

    def test_a_type_about_the_source_needs_no_reason_on_a_supported(self):
        for name in ABOUT_THE_SOURCE:
            with self.subTest(name=name):
                self.assertFalse(any("Still supported" in p for p in stage4_of(with_type(SUPPORTED, name))))

    def test_a_could_not_open_carries_page_gone_or_nothing(self):
        self.assertEqual(stage4_of(COULD_NOT_OPEN), [])
        self.assertEqual(stage4_of(with_type(COULD_NOT_OPEN, "page-gone")), [])
        for name in THE_TEN:
            if name == "page-gone":
                continue
            with self.subTest(name=name):
                problems = stage4_of(with_type(COULD_NOT_OPEN, name))
                self.assertTrue(any(f"a could-not-open can carry page-gone or nothing, not {name}" in p for p in problems), problems)

    def test_a_no_source_carries_page_gone_or_nothing(self):
        self.assertEqual(stage4_of(with_type(NO_SOURCE, "page-gone")), [])
        for name in THE_TEN:
            if name == "page-gone":
                continue
            with self.subTest(name=name):
                problems = stage4_of(with_type(NO_SOURCE, name))
                self.assertTrue(any(f"a no-source can carry page-gone or nothing, not {name}" in p for p in problems), problems)

    def test_a_could_not_open_says_what_stood_in_the_way(self):
        self.failing(COULD_NOT_OPEN.replace("- In the way: a sign-up form\n", ""), "what stood in the way")
        self.failing(COULD_NOT_OPEN.replace("- In the way: a sign-up form", "- In the way:"), "what stood in the way")


class AddedRuleTests(unittest.TestCase):
    """The spec's second stage 4 list: a record the report could not be written from."""

    def added(self, text: str) -> list[str]:
        (record,) = claims.parse_records(text, "research-1.md")
        return claims.added_problems(record)

    def test_the_example_records_pass(self):
        for text in (SUPPORTED, DIFFERS, NO_SOURCE, COULD_NOT_OPEN):
            self.assertEqual(self.added(text), [])

    def test_every_record_has_a_finding(self):
        problems = self.added(NO_SOURCE.replace("- Finding: No first publisher's page was found. The line appears only on pages that repeat it.\n", ""))
        self.assertEqual(len(problems), 1)
        self.assertIn("no Finding line", problems[0])

    def test_a_first_publisher_is_named_unless_none_was_found(self):
        for text in (SUPPORTED, DIFFERS, COULD_NOT_OPEN):
            with self.subTest(record=text.splitlines()[1]):
                cut = "\n".join(l for l in text.splitlines() if not l.startswith("- First publisher:")) + "\n"
                self.assertTrue(any("names the first publisher" in p for p in self.added(cut)))

    def test_a_published_line_is_needed_and_can_say_not_shown(self):
        self.assertEqual(self.added(DIFFERS), [])
        self.assertTrue(any("needs a Published line" in p for p in self.added(SUPPORTED.replace("- Published: 3 March 2025\n", ""))))

    def test_a_differs_needs_evidence_and_words_to_use_instead(self):
        self.assertTrue(any("a differs needs evidence" in p for p in self.added(DIFFERS.split("- Evidence:")[0])))
        self.assertTrue(any("Use instead" in p for p in self.added(DIFFERS.replace("- Use instead: Acme was founded in 2012\n", ""))))

    def test_a_could_not_open_gives_the_address_and_what_to_look_for(self):
        self.assertTrue(any("Address" in p for p in self.added(COULD_NOT_OPEN.replace("- Address: https://bigfirm.example/report\n", ""))))
        look = "- Look for: the 9 in 10 figure, whether it counts all deals or only large ones, and the report's date\n"
        self.assertTrue(any("Look for" in p for p in self.added(COULD_NOT_OPEN.replace(look, ""))))


# ---------------------------------------------------------------- stage 4: the quote check


class QuoteTests(unittest.TestCase):
    # A page as a site serves it: curly quotes and a non-breaking space, built from code points so
    # this file never contains the characters the repo bans.
    PAGE = "Our survey found that 74% of B2B buyers " + chr(0x201C) + "read reviews" + chr(0x201D) + " before they" + chr(0x00A0) + "buy. PayScale" + chr(0x2019) + "s team agreed: it's true."

    def test_a_figure_split_from_its_percent_sign_is_still_found(self):
        # Forrester's press release of 4 December 2024 holds "86" and "%" in two tags, so the page's
        # text reads "86 %". Found in the check set's second run, 25 November 2026.
        html = "<p>Currently, <span>86</span><span>%</span> of B2B purchases stall during the buying process.</p>"
        text = claims.page_text(html)
        self.assertTrue(claims.quote_on_page("86% of B2B purchases stall during the buying process", text))
        self.assertTrue(claims.quote_on_page("86 % of B2B purchases stall", text))
        self.assertFalse(claims.quote_on_page("68% of B2B purchases stall", text))

    def test_case_spacing_quote_marks_and_punctuation_are_ignored(self):
        for quote in (
            "74% of b2b buyers read reviews",
            "74%   of B2B buyers,  read reviews",
            '"read reviews" before they buy',
            "'read reviews' before they buy.",
            "PayScale's team agreed; it's true",
        ):
            with self.subTest(quote=quote):
                self.assertTrue(claims.quote_on_page(quote, self.PAGE))

    def test_nothing_else_is_ignored(self):
        for quote in (
            "47% of B2B buyers read reviews",  # another figure
            "74 of B2B buyers read reviews",  # the per cent sign dropped
            "74% of buyers read reviews",  # a word left out
            "buyers B2B read reviews",  # words out of order
            "74% of B2B buyer read reviews",  # part of a word
            "PayScales team agreed",  # an apostrophe inside a word dropped
        ):
            with self.subTest(quote=quote):
                self.assertFalse(claims.quote_on_page(quote, self.PAGE))

    def test_whole_words_only(self):
        self.assertFalse(claims.quote_on_page("part of Sage", "Now part of Sagemaker"))
        self.assertTrue(claims.quote_on_page("part of Sage", "Now part of Sage."))

    def test_an_empty_quote_is_never_found(self):
        self.assertFalse(claims.quote_on_page("...", self.PAGE))

    def test_page_text_leaves_out_scripts_and_tags(self):
        text = claims.page_text("<p>Founded in <b>2012</b> by two engineers</p><script>var founded = 2010;</script>")
        self.assertTrue(claims.quote_on_page("Founded in 2012 by two engineers", text))
        self.assertFalse(claims.quote_on_page("founded 2010", text))


class PacingTests(unittest.TestCase):
    def setUp(self):
        claims._last_request.clear()
        self.clock = 100.0
        self.slept: list[float] = []

    def now(self):
        return self.clock

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.clock += seconds

    def test_a_second_request_to_the_same_site_waits_two_seconds(self):
        claims.pace("acme.example", self.now, self.sleep)
        claims.pace("acme.example", self.now, self.sleep)
        self.assertEqual(self.slept, [2.0])

    def test_other_sites_do_not_wait(self):
        claims.pace("acme.example", self.now, self.sleep)
        claims.pace("globex.example", self.now, self.sleep)
        self.assertEqual(self.slept, [])

    def test_no_wait_once_two_seconds_have_passed(self):
        claims.pace("acme.example", self.now, self.sleep)
        self.clock += 2.5
        claims.pace("acme.example", self.now, self.sleep)
        self.assertEqual(self.slept, [])


PAGES = {
    "https://acme.example/survey-2025": html_page("https://acme.example/survey-2025", "<h1>Survey 2025</h1><p>74% of buyers read reviews.</p>"),
    "https://acme.example/about": html_page("https://acme.example/about", "<p>Founded in 2012 by two engineers.</p>"),
    "https://globex.example/news/sale": html_page("https://globex.example/news/sale", "<p>Globex has completed the sale of Acme to Initrode.</p>"),
    "https://acme.example/report-2026": html_page("https://acme.example/report-2026", "<h2>Most buyers will switch</h2><p>In fact most buyers say they may switch.</p>"),
}


class RunFolder(unittest.TestCase):
    """A run folder with a numbered draft, a claims file and one research file."""

    RESEARCH = "\n".join((SUPPORTED, DIFFERS, NO_SOURCE, COULD_NOT_OPEN, OUT_OF_DATE_NOW, SUPPORTED_FIRST_PASS))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name)
        (self.run / "working").mkdir()
        (self.run / "draft-lines.md").write_text(LINES, encoding="utf-8")
        (self.run / "claims.md").write_text(CLAIMS, encoding="utf-8")
        self.research = self.run / "working" / "research-1.md"
        self.research.write_text(self.RESEARCH, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def write_check(self, text: str) -> Path:
        path = self.run / "working" / "check-1.md"
        path.write_text(text, encoding="utf-8")
        return path


class VerifyTests(RunFolder):
    def test_a_good_run_passes_and_records_each_quote(self):
        problems, notes, states = claims.verify(self.run, get=fake(PAGES))
        self.assertEqual(problems, [])
        self.assertEqual(
            states,
            {
                "research-1.md|C01|E1": "verified",
                "research-1.md|C02|E1": "verified",
                "research-1.md|C07|E1": "verified",
                "research-1.md|C08|E1": "verified",
            },
        )
        saved = json.loads((self.run / "working" / "evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["research-1.md|C02|E1"], "verified")
        self.assertIn("9 sentences, 8 claims: 6 to trace, 2 to confirm with a person", notes[0])

    def test_the_four_states_a_quote_can_be_in(self):
        self.research.write_text(
            self.RESEARCH.replace('"Founded in 2012 by two engineers"', '"Founded in 2010 by two engineers"')
            .replace("https://globex.example/news/sale", "https://globex.example/annual-report.pdf")
            .replace("https://acme.example/report-2026", "https://acme.example/blocked"),
            encoding="utf-8",
        )
        problems, notes, states = claims.verify(self.run, get=fake(PAGES))
        self.assertEqual(states["research-1.md|C01|E1"], "verified")
        self.assertEqual(states["research-1.md|C02|E1"], "not-on-page")
        self.assertEqual(states["research-1.md|C07|E1"], "pdf")
        self.assertEqual(states["research-1.md|C08|E1"], "could-not-load")
        # The spec's list of what verify fails on does not hold a quote that was not found. Stage 5
        # sends it to the checker, so the script says so and carries on.
        self.assertEqual(problems, [])
        self.assertTrue(any("C02 E1: quote not found on https://acme.example/about" in n for n in notes), notes)

    def test_a_page_served_as_a_pdf_is_a_pdf(self):
        pages = dict(PAGES)
        pages["https://acme.example/about"] = Page(url="https://acme.example/about", status=200, kind="application/pdf")
        _, _, states = claims.verify(self.run, get=fake(pages))
        self.assertEqual(states["research-1.md|C02|E1"], "pdf")

    def test_every_page_is_loaded_once(self):
        self.research.write_text(
            self.RESEARCH.replace("https://acme.example/about", "https://acme.example/survey-2025").replace(
                "https://acme.example/report-2026", "https://acme.example/blocked"
            )
            + '  - E2 | page | https://acme.example/blocked | "buyers will switch soon"\n',
            encoding="utf-8",
        )
        calls: list[str] = []
        claims.verify(self.run, get=fake(PAGES, calls))
        self.assertEqual(sorted(calls), ["https://acme.example/blocked", "https://acme.example/survey-2025", "https://globex.example/news/sale"])
        # The checker's file cites pages the first pass loaded: they are read from the saved copy.
        again: list[str] = []
        claims.verify(self.run, [self.write_check(CHECK_C08.replace("report-2026", "survey-2025"))], get=fake(PAGES, again))
        self.assertEqual(again, [])

    def test_a_pdf_is_not_downloaded(self):
        self.research.write_text(self.RESEARCH.replace("https://globex.example/news/sale", "https://globex.example/annual-report.pdf"), encoding="utf-8")
        calls: list[str] = []
        claims.verify(self.run, get=fake(PAGES, calls))
        self.assertNotIn("https://globex.example/annual-report.pdf", calls)

    def test_a_claim_with_no_record_fails(self):
        self.research.write_text("\n".join((SUPPORTED, DIFFERS, NO_SOURCE, COULD_NOT_OPEN, OUT_OF_DATE_NOW)), encoding="utf-8")
        problems, _, _ = claims.verify(self.run, get=fake(PAGES))
        self.assertEqual(len(problems), 1)
        self.assertIn("C08: no record", problems[0])

    def test_one_researcher_can_verify_its_own_file(self):
        self.research.write_text(SUPPORTED, encoding="utf-8")
        problems, _, _ = claims.verify(self.run, [self.research], get=fake(PAGES))
        self.assertEqual(problems, [])

    def test_a_shape_problem_fails_the_run(self):
        self.research.write_text(self.RESEARCH.replace("Problems: number-wrong", "Problems: none"), encoding="utf-8")
        problems, _, _ = claims.verify(self.run, get=fake(PAGES))
        self.assertEqual(len(problems), 1)
        self.assertIn("research-1.md", problems[0])
        self.assertIn("C02: a differs needs at least one problem type", problems[0])

    def test_a_claim_on_the_confirm_list_is_never_traced(self):
        self.research.write_text(self.RESEARCH + "\n" + SUPPORTED.replace("## C01", "## C05"), encoding="utf-8")
        problems, _, _ = claims.verify(self.run, get=fake(PAGES))
        self.assertTrue(any("C05" in p and "confirm list" in p for p in problems), problems)

    def test_a_record_for_no_claim_and_a_second_record_fail(self):
        self.research.write_text(self.RESEARCH + "\n" + SUPPORTED.replace("## C01", "## C40") + "\n" + SUPPORTED, encoding="utf-8")
        problems, _, _ = claims.verify(self.run, get=fake(PAGES))
        self.assertTrue(any("C40: no such claim" in p for p in problems), problems)
        self.assertTrue(any("C01: a second record" in p for p in problems), problems)

    def test_the_readers_file_can_be_checked_before_any_research(self):
        self.research.unlink()
        calls: list[str] = []
        problems, notes, states = claims.verify(self.run, claims_only=True, get=fake(PAGES, calls))
        self.assertEqual((problems, states, calls), ([], {}, []))
        (self.run / "claims.md").write_text(CLAIMS.replace("No claim: S1, S3", "No claim: S1"), encoding="utf-8")
        code, printed, _ = run_main(["verify", str(self.run), "--claims"])
        self.assertEqual(code, 1)
        self.assertIn("S3 has neither a claim nor a no claim mark", printed)

    def test_over_the_caps_is_said_and_does_not_fail(self):
        lines = "".join(f"[S{n}] Fact number {n} is true.\n" for n in range(1, 42))
        blocks = "".join(
            f'## C{n:02d} | S{n} | statistic\n- Claim: Fact {n}.\n- Draft words: "Fact number {n} is true"\n- Source given: none\n- Trace: yes\n\n' for n in range(1, 42)
        )
        (self.run / "draft-lines.md").write_text(lines, encoding="utf-8")
        (self.run / "claims.md").write_text(blocks, encoding="utf-8")
        problems, notes, _ = claims.verify(self.run, claims_only=True)
        self.assertEqual(problems, [])
        self.assertTrue(any("over 40 claims to trace: run the draft in parts" in n for n in notes), notes)
        # 16 claims: fine for the subagent route, over the chat route's 15.
        (self.run / "draft-lines.md").write_text("".join(lines.splitlines(True)[:16]), encoding="utf-8")
        (self.run / "claims.md").write_text("\n\n".join(blocks.split("\n\n")[:16]) + "\n", encoding="utf-8")
        problems, notes, _ = claims.verify(self.run, claims_only=True)
        self.assertEqual(problems, [])
        self.assertTrue(any("over 15 claims to trace" in n for n in notes), notes)


# ---------------------------------------------------------------- stage 5: what goes to the checker


class CheckerTests(RunFolder):
    def record(self, text: str) -> "claims.Record":
        (record,) = claims.parse_records(text, "research-1.md")
        return record

    def test_every_supported_goes_to_the_checker(self):
        self.assertTrue(claims.needs_check(self.record(SUPPORTED), {"research-1.md|C01|E1": "verified"}))

    def test_a_differs_with_every_quote_found_goes_straight_to_the_report(self):
        self.assertFalse(claims.needs_check(self.record(DIFFERS), {"research-1.md|C02|E1": "verified"}))

    def test_a_differs_goes_to_the_checker_for_each_state_the_script_could_not_confirm(self):
        for state in ("not-on-page", "pdf", "could-not-load"):
            with self.subTest(state=state):
                self.assertTrue(claims.needs_check(self.record(DIFFERS), {"research-1.md|C02|E1": state}))
        # A quote verify never looked at is not confirmed either.
        self.assertTrue(claims.needs_check(self.record(DIFFERS), {}))

    def test_one_unconfirmed_quote_among_several_is_enough(self):
        two = DIFFERS + '  - E2 | page | https://acme.example/history.pdf | "established in 2012"\n'
        states = {"research-1.md|C02|E1": "verified", "research-1.md|C02|E2": "pdf"}
        self.assertTrue(claims.needs_check(self.record(two), states))

    def test_a_claim_with_no_evidence_to_confirm_is_not_sent(self):
        self.assertFalse(claims.needs_check(self.record(NO_SOURCE), {}))
        self.assertFalse(claims.needs_check(self.record(COULD_NOT_OPEN), {}))

    def test_a_no_source_resting_on_an_unconfirmed_quote_is_sent(self):
        lead = NO_SOURCE + '- Evidence:\n  - E1 | page | https://acme.example/comic.pdf | "published by Acme"\n'
        self.assertTrue(claims.needs_check(self.record(lead), {"research-1.md|C03|E1": "pdf"}))

    def test_the_checker_reads_claims_and_verdicts_and_nothing_else(self):
        claims.verify(self.run, get=fake(PAGES))
        claims.report(self.run, today="2026-11-25")
        files = sorted(p.name for p in (self.run / "check-in").iterdir())
        self.assertEqual(files, ["to-check-1.md"])
        text = (self.run / "check-in" / "to-check-1.md").read_text(encoding="utf-8")
        # The two supported claims go. The differs with a verified quote, the no-source and the
        # could-not-open do not.
        self.assertEqual([l for l in text.splitlines() if l.startswith("## ")], ["## C01 | S2 | statistic", "## C08 | S9 | citation"])
        self.assertIn("- Claim: Acme's 2025 survey found that 74% of buyers read reviews.", text)
        self.assertIn('- Draft words: "74% of buyers read reviews"', text)
        self.assertIn("- Source given: Acme's 2025 survey", text)
        self.assertIn("- Verdict: supported", text)
        for hidden in ("Acme Research", "acme.example", "http", "E1", "Finding", "Published", "3 March 2025", "Problems", "Evidence", "Searches"):
            with self.subTest(hidden=hidden):
                self.assertNotIn(hidden, text)

    def test_the_checker_is_not_told_the_problem_types(self):
        self.research.write_text(self.RESEARCH.replace(SUPPORTED, with_type(SUPPORTED, "out-of-date")), encoding="utf-8")
        claims.verify(self.run, get=fake(PAGES))
        claims.report(self.run, today="2026-11-25")
        text = (self.run / "check-in" / "to-check-1.md").read_text(encoding="utf-8")
        self.assertIn("## C01 | S2 | statistic", text)
        self.assertNotIn("out-of-date", text)
        self.assertNotIn("69%", text)


# ---------------------------------------------------------------- stage 6: the report

AGREED = """## C01
- Verdict: supported
- Problems: none
- First publisher: Acme Research
- Published: 3 March 2025
- Finding: The 2025 survey report gives 74% of buyers.
- Check notes: Agreed. Found the same report from Acme's own research page.
- Evidence:
  - E1 | page | https://acme.example/survey-2025 | "74% of buyers read reviews"
"""


class ReportTests(RunFolder):
    """The order and contents under 'Stage 6: Hand-back' in the spec, as ADR 0021 sets them."""

    FIX = "Fix these"
    UPDATE = "Update or re-credit these"
    YOUR_CALL = "Your call: no source found"
    CONFIRM = "Confirm with a person"
    NOTHING = "Nothing to do"
    HOW = "How this was checked"

    def build(self, check: str | None = AGREED + "\n" + CHECK_C08) -> str:
        if check is not None:
            self.write_check(check)
        claims.verify(self.run, get=fake(PAGES))
        self.notes = claims.report(self.run, today="2026-11-25")
        return (self.run / "check.md").read_text(encoding="utf-8")

    def sections(self, text: str) -> dict[str, str]:
        """The report cut at its second-level headings, in the order they come."""
        parts = text.split("\n## ")
        return {part.splitlines()[0]: part for part in parts[1:]}

    def heads(self, section: str) -> list[str]:
        return [line for line in section.splitlines() if line.startswith("### ")]

    def test_the_parts_come_in_the_spec_order(self):
        self.assertEqual(
            list(self.sections(self.build())),
            [self.FIX, self.UPDATE, self.YOUR_CALL, self.CONFIRM, self.NOTHING, self.HOW],
        )

    def test_it_opens_with_how_many_claims_need_nothing_and_a_count_for_each_kind_of_work(self):
        top = self.build().split("\n## ")[0]
        self.assertIn("Checked 2026-11-25. 9 sentences, 8 claims.", top)
        # By hand: of the 8 claims only C01 is supported with nothing against it. C02, C07 and C08
        # differ. C03 has no source. C04 could not be opened, and C05 and C06 are for a person.
        self.assertIn("**1 of the 8 claims needs nothing from you.**", top)
        rows = [line for line in top.splitlines() if line.startswith("| ") and line[2:5] not in ("Wha", "---")]
        self.assertEqual([row.split("|")[1].split(":")[0].strip() for row in rows], ["Fix", "Update or re-credit", "Your call", "Confirm with a person"])
        self.assertEqual([row.split("|")[2].strip() for row in rows], ["3", "0", "1", "3"])
        # The counts by verdict are not what the report opens with.
        self.assertNotIn("| Verdict |", top)

    def test_counts_by_verdict_and_by_problem_type_come_last(self):
        how = self.sections(self.build())[self.HOW]
        # By hand: C01 supported, C02 differs, C03 no-source, C04 could-not-open, C07 differs, and
        # C08 differs once the checker's record replaces the first pass's supported.
        for row in ("| supported | 1 |", "| differs | 3 |", "| no-source | 1 |", "| could-not-open | 1 |"):
            self.assertIn(row, how)
        # C02 number-wrong, C07 out-of-date, C08 strength-changed.
        for row in ("| number-wrong | 1 |", "| out-of-date | 1 |", "| strength-changed | 1 |"):
            self.assertIn(row, how)
        for absent in ("second-hand", "base-dropped", "page-gone"):
            self.assertNotIn(absent, how)
        self.assertIn("The checker re-checked 2 claims and changed the verdict or the problem types of 1.", how)
        self.assertIn("Quotes found on their pages by the script: 4.", how)

    def test_it_says_comparisons_between_claims_were_not_checked(self):
        self.assertIn("Comparisons between claims were not checked.", self.sections(self.build())[self.HOW])

    def test_every_differs_is_under_fix_with_the_words_to_use_first(self):
        fix = self.sections(self.build())[self.FIX]
        self.assertEqual(
            self.heads(fix),
            ["### C02 | S7: differs, number-wrong", "### C07 | S7: differs, out-of-date", "### C08 | S9: differs, strength-changed"],
        )
        entry = fix.split("### C02")[1].split("### ")[0]
        self.assertIn("- Use instead: Acme was founded in 2012", entry)
        self.assertIn("- What was found: Acme's own history page says it was founded in 2012, not 2010.", entry)
        self.assertLess(entry.index("Use instead"), entry.index("What was found"))
        self.assertIn("- First publisher: Acme\n- Published: not shown", entry)
        self.assertIn('E1 page: https://acme.example/about "Founded in 2012 by two engineers" (found on the page by the script)', entry)

    def test_a_no_source_is_the_users_call_and_lists_the_searches(self):
        call = self.sections(self.build())[self.YOUR_CALL]
        self.assertEqual(self.heads(call), ["### C03 | S8: no-source"])
        self.assertIn("That is not proof there is none.", call)
        self.assertIn("Searches tried:", call)
        self.assertIn('  - "how many buyers skim" survey', call)

    def test_the_confirm_list_holds_own_company_named_person_and_could_not_open(self):
        confirm = self.sections(self.build())[self.CONFIRM]
        own, person, unopened, unfound = confirm.split("### ")[1:]
        self.assertEqual(unfound.strip().splitlines(), ["Supported, but the script did not find the quote", "", "None."])
        self.assertTrue(own.startswith("About your own company"))
        self.assertIn('**C05 | S4**: "Our product cuts onboarding time by half"', own)
        self.assertTrue(person.startswith("About a named person"))
        self.assertIn('**C06 | S5**: "never reads vendor email"', person)
        self.assertTrue(unopened.startswith("Pages that could not be opened"))
        # Everything a person needs to settle it in one visit.
        self.assertIn("**C04 | S6**", unopened)
        self.assertIn("Open: https://bigfirm.example/report", unopened)
        self.assertIn('The draft says: "9 in 10 deals involve a committee"', unopened)
        self.assertIn("What stood in the way: a sign-up form", unopened)
        self.assertIn("Look for: the 9 in 10 figure, whether it counts all deals or only large ones, and the report's date", unopened)
        for elsewhere in ("C01", "C02", "C03", "C07", "C08"):
            self.assertNotIn(elsewhere, confirm)

    def test_a_supported_claim_with_a_problem_type_is_under_update(self):
        self.research.write_text(self.RESEARCH.replace(SUPPORTED, with_type(SUPPORTED, "out-of-date")), encoding="utf-8")
        text = self.build(check=None)
        parts = self.sections(text)
        self.assertEqual(self.heads(parts[self.UPDATE]), ["### C01 | S2: supported, out-of-date"])
        self.assertIn('E8 newer: https://acme.example/survey-2026 "69% of buyers read reviews" (the page would not load for the script)', parts[self.UPDATE])
        self.assertNotIn("C01", parts[self.NOTHING])
        self.assertIn("C08", parts[self.NOTHING])
        self.assertIn("| out-of-date | 2 |", parts[self.HOW])
        # C08 is now the only clean claim, and C01 has moved to the second row.
        self.assertIn("**1 of the 8 claims needs nothing from you.**", text)
        self.assertIn("| Update or re-credit: supported, with a newer figure or a better source to give | 1 |", text)

    def test_a_gone_page_and_the_reason_a_claim_is_still_supported_reach_the_report(self):
        why = "- Still supported: the draft drops 'B2B', and every buyer the survey asked was a B2B buyer\n"
        both = with_type(SUPPORTED, "page-gone", why).replace("Problems: page-gone", "Problems: page-gone, base-dropped")
        self.research.write_text(self.RESEARCH.replace(SUPPORTED, both), encoding="utf-8")
        parts = self.sections(self.build(check=None))
        entry = parts[self.UPDATE].split("### C01")[1].split("### ")[0]
        self.assertTrue(entry.startswith(" | S2: supported, page-gone, base-dropped"), entry)
        self.assertIn("- Still supported because: the draft drops 'B2B', and every buyer the survey asked was a B2B buyer", entry)
        self.assertIn("- Page gone: https://acme.example/old-survey now loads the home page", entry)
        self.assertNotIn("C01", parts[self.NOTHING])

    def test_clean_supported_claims_need_nothing_and_show_publisher_and_date(self):
        clean = self.sections(self.build())[self.NOTHING]
        self.assertIn('- **C01 | S2**: "74% of buyers read reviews"\n  - First publisher: Acme Research\n  - Published: 3 March 2025', clean)
        self.assertIn("Checker: agreed. Found the same report from Acme's own research page.", clean)
        for elsewhere in ("C02", "C03", "C04", "C07", "C08"):
            self.assertNotIn(elsewhere, clean)

    def test_the_checkers_record_replaces_the_first_pass_and_the_report_says_what_changed(self):
        entry = self.sections(self.build())[self.FIX].split("### C08")[1].split("### ")[0]
        self.assertIn("Checker: changed it, was supported. The first pass quoted a pull-out heading, not the finding.", entry)
        self.assertIn('"most buyers say they may switch"', entry)
        self.assertNotIn('"most buyers will switch" (', entry)

    def test_it_says_above_everything_else_when_no_verdict_was_re_checked(self):
        text = self.build(check=None)
        self.assertEqual(text.splitlines()[2][:26], "No verdict was re-checked:")
        self.assertIn("The checker re-checked 0 claims and changed the verdict or the problem types of 0.", text)
        self.assertNotIn("No verdict was re-checked", self.build())

    def test_it_names_a_claim_the_checker_never_returned(self):
        how = self.sections(self.build(check=CHECK_C08))[self.HOW]
        self.assertIn("Sent to the checker but no record came back, so these show the first pass only: C01.", how)

    def test_a_supported_claim_whose_quote_the_script_did_not_find_goes_on_the_confirm_list(self):
        self.research.write_text(self.RESEARCH.replace('"74% of buyers read reviews"', '"74% of all buyers read reviews"'), encoding="utf-8")
        text = self.build(check=None)
        parts = self.sections(text)
        entry = parts[self.CONFIRM].split("### Supported, but the script did not find the quote")[1]
        self.assertIn("**C01 | S2**", entry)
        self.assertIn('The draft says: "74% of buyers read reviews"', entry)
        self.assertIn("Open: https://acme.example/survey-2025", entry)
        self.assertIn('Look for: "74% of all buyers read reviews"', entry)
        # It is still supported in the counts, and it is no longer under nothing to do.
        self.assertNotIn("C01", parts[self.NOTHING])
        self.assertIn("| supported | 2 |", parts[self.HOW])
        self.assertIn("Not confirmed by the script: 1 (0 in PDFs, 0 on pages it did not load, 1 not found).", parts[self.HOW])
        # By hand: C08 is the one clean claim left. To confirm: C04, C05, C06 and now C01.
        self.assertIn("**1 of the 8 claims needs nothing from you.**", text)
        self.assertIn("| Confirm with a person: one visit or one question each | 4 |", text)

    def test_a_supported_claim_on_a_page_the_script_could_not_read_stays_where_it_was(self):
        for address in ("https://acme.example/survey-2025.pdf", "https://acme.example/blocked"):
            with self.subTest(address=address):
                self.research.write_text(self.RESEARCH.replace("https://acme.example/survey-2025", address), encoding="utf-8")
                parts = self.sections(self.build(check=None))
                self.assertIn("**C01 | S2**", parts[self.NOTHING])
                self.assertNotIn("C01", parts[self.CONFIRM])

    def test_one_quote_found_is_enough_to_stay_supported_without_a_visit(self):
        two = SUPPORTED + '  - E2 | page | https://acme.example/survey-2025 | "74% of all buyers read reviews"\n'
        self.research.write_text(self.RESEARCH.replace(SUPPORTED, two), encoding="utf-8")
        parts = self.sections(self.build(check=None))
        self.assertIn("**C01 | S2**", parts[self.NOTHING])
        self.assertNotIn("C01", parts[self.CONFIRM])

    def test_a_claim_with_no_record_is_counted_and_named(self):
        self.research.write_text("\n".join((SUPPORTED, DIFFERS, NO_SOURCE, COULD_NOT_OPEN, OUT_OF_DATE_NOW)), encoding="utf-8")
        claims.report(self.run, today="2026-11-25")
        text = (self.run / "check.md").read_text(encoding="utf-8")
        self.assertIn("| Not checked: no record | 1 |", text.split("\n## ")[0])
        how = self.sections(text)[self.HOW]
        self.assertIn("| no record | 1 |", how)
        self.assertIn("No record, so not checked: C08.", how)

    def test_the_command_writes_check_md(self):
        claims.verify(self.run, get=fake(PAGES))
        code, printed, _ = run_main(["report", str(self.run)])
        self.assertEqual(code, 0)
        self.assertTrue((self.run / "check.md").is_file())
        self.assertIn("6 claims traced: 2 supported, 2 differs, 1 no-source, 1 could-not-open", printed)


# ---------------------------------------------------------------- the saved sample


class SampleTests(unittest.TestCase):
    """The sample built from the test of the problem's records for draft A4 still fits the format.
    This checks its shape only. Its verdicts are the test's, and nothing here re-scores them."""

    def test_the_sample_records_pass_every_shape_rule(self):
        self.assertTrue((SAMPLE / "check.md").is_file(), "the sample report is missing")
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp)
            (run / "working").mkdir()
            for name in ("draft-lines.md", "claims.md", "working/research-1.md", "working/check-1.md"):
                (run / name).write_text((SAMPLE / name).read_text(encoding="utf-8"), encoding="utf-8")
            problems, _, states = claims.verify(run, get=fake({}))
        self.assertEqual(problems, [])
        # Built with the network off, so no quote was looked for on a live page.
        self.assertNotIn("verified", states.values())


if __name__ == "__main__":
    unittest.main()
