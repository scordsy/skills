"""Tests for check-account-list's accounts.py: loading lists, websites,
pacing, the record format, the quote check, what goes to the checker, and the report. No network."""

from __future__ import annotations

import csv
import importlib.util
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "check-account-list" / "scripts" / "accounts.py"
spec = importlib.util.spec_from_file_location("accounts", SCRIPT)
assert spec and spec.loader
accounts = importlib.util.module_from_spec(spec)
# Dataclasses look their module up in sys.modules, so register it before running it.
sys.modules[spec.name] = accounts
spec.loader.exec_module(accounts)

Page = accounts.Page


def fake(pages: dict[str, Page]):
    """A fetch that serves pages from a dict, and fails for anything else."""

    def get(url: str) -> Page:
        if url in pages:
            return pages[url]
        return Page(url=url, error="no such host")

    return get


def html_page(url: str, body: str, final: str | None = None, status: int = 200) -> Page:
    return Page(url=url, status=status, final=final or url, kind="text/html", text=body)


KEEP = """## A01 | RotaCloud
- Website given: rotacloud.com
- Website: https://rotacloud.com/ loads, rota software for small businesses
- Registered: UK, 08012345, active
- Owner: independent, founders
- Size: 65 staff (UK company, accounts to 31 March 2025)
- Fit: sells rota software to small UK employers
- Conflicts: none
- Verdict: keep
- Problems: none
- Reason: UK SaaS company, 65 staff, sells to small businesses.
- Evidence:
  - E1 | website | https://rotacloud.com/ | "Staff rota software"
  - E2 | trading | https://example.gov/co | "Company status Active"
  - E3 | owner | https://example.gov/owners | "Jane Founder"
  - E4 | size | https://example.gov/accounts.pdf | "average number of employees was 65"
  - E5 | fit | https://rotacloud.com/ | "for small businesses"
"""

DROP = """## A02 | Rotageek
- Website given: rotageek.com
- Website: https://www.rotageek.com/ loads
- Registered: UK, 06783810, active
- Owner: Elmo Software Uk Holdings Limited since 30 May 2025
- Size: 39 staff
- Fit: sells to large chains
- Conflicts: same group as your best customer, Breathe
- Verdict: drop
- Problems: bought, customer
- Reason: Owned by ELMO since May 2025, the group that owns your best customer.
- Evidence:
  - E1 | owner | https://example.gov/owners | "Elmo Software Uk Holdings Limited"
"""

PAGES = {
    "https://rotacloud.com/": html_page("https://rotacloud.com/", "<h1>Staff rota software</h1><p>Built for small businesses.</p>"),
    "https://example.gov/co": html_page("https://example.gov/co", "<dt>Company status</dt><dd>Active</dd>"),
    "https://example.gov/owners": html_page("https://example.gov/owners", "<b>Jane Founder</b> <b>Elmo Software Uk Holdings Limited</b>"),
    "https://example.gov/accounts.pdf": Page(url="https://example.gov/accounts.pdf", status=200, final="https://example.gov/accounts.pdf", kind="application/pdf"),
}


class LoadTests(unittest.TestCase):
    def load(self, name: str, content: str | bytes) -> tuple[list, list[str]]:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / name
            if isinstance(content, bytes):
                source.write_bytes(content)
            else:
                source.write_text(content, encoding="utf-8")
            out = Path(tmp) / "companies.md"
            notes = accounts.load(source, out)
            return accounts.read_companies(out), notes

    def test_markdown_table_with_links(self):
        companies, notes = self.load("list.md", (
            "| # | Company | Website | Why |\n| --- | --- | --- | --- |\n"
            "| 1 | Ciphr | [ciphr.com](https://www.ciphr.com/?utm_source=chatgpt.com) | HR |\n"
            "| 2 | Cezanne HR | cezannehr.com | HR |\n"
        ))
        self.assertEqual([(c.id, c.name, c.website) for c in companies], [("A01", "Ciphr", "ciphr.com"), ("A02", "Cezanne HR", "cezannehr.com")])
        self.assertIn("2 companies, 2 with a website", notes[0])

    def test_csv_with_headers_in_any_order(self):
        companies, _ = self.load("list.csv", "Domain,Company Name,Industry\nhttps://www.rotacloud.com,RotaCloud,HR\n,No Site Ltd,HR\n")
        self.assertEqual([(c.name, c.website) for c in companies], [("RotaCloud", "rotacloud.com"), ("No Site Ltd", "")])

    def test_plain_numbered_lines(self):
        companies, _ = self.load("list.txt", "1. CharlieHR, charliehr.com\n2. Natural HR - naturalhr.com\n- Timetastic (timetastic.co.uk)\nJust A Name\n")
        self.assertEqual(
            [(c.name, c.website) for c in companies],
            [("CharlieHR", "charliehr.com"), ("Natural HR", "naturalhr.com"), ("Timetastic", "timetastic.co.uk"), ("Just A Name", "")],
        )

    def test_xlsx_first_sheet(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as book:
            book.writestr("xl/sharedStrings.xml", (
                '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                "<si><t>Company</t></si><si><t>Website</t></si><si><t>Feefo</t></si><si><t>feefo.com</t></si></sst>"
            ))
            book.writestr("xl/worksheets/sheet1.xml", (
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>'
                '<row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2" t="s"><v>3</v></c></row>'
                '<row r="3"><c r="A3" t="inlineStr"><is><t>Reviews.io</t></is></c><c r="B3" t="inlineStr"><is><t>reviews.io</t></is></c></row>'
                "</sheetData></worksheet>"
            ))
        companies, _ = self.load("list.xlsx", buffer.getvalue())
        self.assertEqual([(c.name, c.website) for c in companies], [("Feefo", "feefo.com"), ("Reviews.io", "reviews.io")])

    def test_headers_matched_by_a_word_in_them(self):
        companies, _ = self.load("list.csv", "Company Domain Name,Organization Name\nciphr.com,Ciphr\n")
        self.assertEqual([(c.name, c.website) for c in companies], [("Ciphr", "ciphr.com")])
        companies, _ = self.load("list.csv", "Business,Website URL\nCiphr,https://www.ciphr.com\n")
        self.assertEqual([(c.name, c.website) for c in companies], [("Ciphr", "ciphr.com")])

    def test_a_website_header_alone_does_not_become_a_company(self):
        companies, _ = self.load("list.csv", "Account,Website\nCiphr,ciphr.com\n")
        self.assertEqual([c.name for c in companies], ["Ciphr"])
        companies, _ = self.load("list.csv", "Who,Website\nCiphr,ciphr.com\n")
        self.assertEqual([c.name for c in companies], ["Ciphr"])

    def test_a_first_row_of_data_is_not_read_as_a_header(self):
        companies, _ = self.load("list.csv", "Acme Business Solutions,acme.com\nCiphr,ciphr.com\n")
        self.assertEqual([c.name for c in companies], ["Acme Business Solutions", "Ciphr"])

    def test_semicolon_csv(self):
        companies, _ = self.load("list.csv", "Company;Website\nCiphr;ciphr.com\n")
        self.assertEqual([(c.name, c.website) for c in companies], [("Ciphr", "ciphr.com")])

    def test_markdown_table_without_outer_pipes(self):
        companies, _ = self.load("list.md", "Company | Website\n--- | ---\nCiphr | ciphr.com\n")
        self.assertEqual([(c.name, c.website) for c in companies], [("Ciphr", "ciphr.com")])

    def test_names_with_dotted_abbreviations_or_commas_stay_whole(self):
        companies, _ = self.load("list.txt", "Carrefour S.A.\nMarks & Spencer p.l.c.\nAcme, Inc.\nKoninklijke Philips N.V.\n")
        self.assertEqual([(c.name, c.website) for c in companies], [
            ("Carrefour S.A.", ""), ("Marks & Spencer p.l.c.", ""), ("Acme, Inc.", ""), ("Koninklijke Philips N.V.", "")])

    def test_an_empty_list_is_refused(self):
        with self.assertRaises(accounts.FormatError):
            self.load("list.csv", "")

    def test_duplicates_flagged_once_per_pair(self):
        _, notes = self.load("list.txt", "Ciphr, ciphr.com\nCiphr Ltd, www.ciphr.com\n")
        self.assertEqual([n for n in notes if "duplicate" in n], ["possible duplicate: A01 and A02 (ciphr.com)"])

    def test_over_fifty_says_run_in_parts(self):
        _, notes = self.load("list.txt", "\n".join(f"Company {n}" for n in range(1, 53)))
        self.assertIn("over 50: run it in parts", notes)

    def test_refuses_formats_it_cannot_read(self):
        with self.assertRaises(accounts.FormatError):
            self.load("list.pdf", b"%PDF-1.4")

    def test_domain_of(self):
        self.assertEqual(accounts.domain_of("https://www.Ciphr.com/?utm_source=x"), "ciphr.com")
        self.assertEqual(accounts.domain_of("getapron.com/"), "getapron.com")
        self.assertEqual(accounts.domain_of(""), "")


class WebsiteTests(unittest.TestCase):
    def test_redirect_to_another_domain_is_noted(self):
        get = fake({"https://weekly10.com": html_page("https://weekly10.com", "<title>Zensai</title>", final="https://zensai.com/")})
        result = accounts.check_site(accounts.Company("A01", "Weekly10", "weekly10.com"), get)
        self.assertEqual(result.moved, "redirects to another domain: zensai.com")
        self.assertEqual(result.title, "Zensai")

    def test_same_domain_with_www_is_not_a_redirect(self):
        get = fake({"https://ciphr.com": html_page("https://ciphr.com", "", final="https://www.ciphr.com/")})
        self.assertEqual(accounts.check_site(accounts.Company("A01", "Ciphr", "ciphr.com"), get).moved, "")

    def test_a_subdomain_of_the_same_site_is_not_another_domain(self):
        get = fake({"https://feefo.com": html_page("https://feefo.com", "", final="https://business.feefo.com/")})
        self.assertEqual(accounts.check_site(accounts.Company("A01", "Feefo", "feefo.com"), get).moved, "")

    def test_falls_back_to_www(self):
        get = fake({"https://www.example.co.uk": html_page("https://www.example.co.uk", "")})
        result = accounts.check_site(accounts.Company("A01", "Example", "example.co.uk"), get)
        self.assertEqual(result.status, "loads (200)")

    def test_site_that_never_loads(self):
        result = accounts.check_site(accounts.Company("A01", "Titania", "titaniasecurity.com"), fake({}))
        self.assertTrue(result.status.startswith("does not load"))

    def test_no_website_given(self):
        self.assertEqual(accounts.check_site(accounts.Company("A01", "X", ""), fake({})).status, "no website given")


class PacingTests(unittest.TestCase):
    def setUp(self):
        accounts._last_request.clear()
        self.clock = [100.0]
        self.slept = []

    def now(self):
        return self.clock[0]

    def sleep(self, seconds):
        self.slept.append(seconds)
        self.clock[0] += seconds

    def test_second_request_to_the_same_site_waits(self):
        accounts.pace("example.com", self.now, self.sleep)
        self.clock[0] += 0.5
        accounts.pace("example.com", self.now, self.sleep)
        self.assertEqual(self.slept, [accounts.PAUSE - 0.5])

    def test_other_sites_do_not_wait(self):
        accounts.pace("example.com", self.now, self.sleep)
        accounts.pace("example.org", self.now, self.sleep)
        self.assertEqual(self.slept, [])

    def test_registers_get_a_longer_pause(self):
        host = "find-and-update.company-information.service.gov.uk"
        accounts.pace(host, self.now, self.sleep)
        self.clock[0] += accounts.PAUSE
        accounts.pace(host, self.now, self.sleep)
        self.assertEqual(self.slept, [accounts.REGISTER_PAUSE - accounts.PAUSE])

    def test_no_wait_once_the_pause_has_passed(self):
        accounts.pace("example.com", self.now, self.sleep)
        self.clock[0] += accounts.PAUSE + 1
        accounts.pace("example.com", self.now, self.sleep)
        self.assertEqual(self.slept, [])


class RecordTests(unittest.TestCase):
    def test_valid_records(self):
        records = accounts.parse_records(KEEP + "\n" + DROP, "research-1.md")
        self.assertEqual([r.id for r in records], ["A01", "A02"])
        self.assertEqual([accounts.check_record(r) for r in records], [[], []])
        self.assertEqual(records[1].problems, ["bought", "customer"])
        self.assertEqual(records[0].evidence[3].check, "size")

    def test_keep_needs_evidence_for_each_check(self):
        text = KEEP.replace('  - E4 | size | https://example.gov/accounts.pdf | "average number of employees was 65"\n', "")
        problems = accounts.check_record(accounts.parse_records(text, "r.md")[0])
        self.assertEqual(len(problems), 1)
        self.assertIn("needs evidence for size", problems[0])

    def test_size_can_be_waived(self):
        text = KEEP.replace("- Size: 65 staff (UK company, accounts to 31 March 2025)", "- Size: not needed, the profile sets no size limit")
        text = text.replace('  - E4 | size | https://example.gov/accounts.pdf | "average number of employees was 65"\n', "")
        self.assertEqual(accounts.check_record(accounts.parse_records(text, "r.md")[0], size_limit=False), [])
        refused = accounts.check_record(accounts.parse_records(text, "r.md")[0], size_limit=True)
        self.assertTrue(any("only when the profile sets no staff range" in p for p in refused))

    def test_drop_needs_evidence_for_each_problem(self):
        text = DROP.replace("- Problems: bought, customer", "- Problems: bought, wrong-size, customer")
        problems = accounts.check_record(accounts.parse_records(text, "r.md")[0])
        self.assertEqual(len(problems), 1)
        self.assertIn("wrong-size needs evidence for size", problems[0])

    def test_customer_duplicate_and_a_dead_site_need_no_quote(self):
        text = DROP.replace("- Problems: bought, customer", "- Problems: bought, customer, duplicate, wrong-website")
        text = text.replace("- Website: https://www.rotageek.com/ loads", "- Website: does not load")
        self.assertEqual(accounts.check_record(accounts.parse_records(text, "r.md")[0]), [])

    def test_check_by_hand_cannot_carry_problems(self):
        text = DROP.replace("- Verdict: drop", "- Verdict: check-by-hand")
        self.assertTrue(any("cannot carry" in p for p in accounts.check_record(accounts.parse_records(text, "r.md")[0])))

    def test_drop_needs_a_problem_and_known_types(self):
        text = DROP.replace("- Problems: bought, customer", "- Problems: none")
        self.assertIn("needs at least one problem", accounts.check_record(accounts.parse_records(text, "r.md")[0])[0])
        text = DROP.replace("bought, customer", "acquired")
        self.assertIn("unknown problem types acquired", accounts.check_record(accounts.parse_records(text, "r.md")[0])[0])

    def test_keep_cannot_carry_problems(self):
        text = KEEP.replace("- Problems: none", "- Problems: wrong-size")
        self.assertTrue(any("cannot carry" in p for p in accounts.check_record(accounts.parse_records(text, "r.md")[0])))

    def test_bad_evidence_line_is_refused(self):
        with self.assertRaises(accounts.FormatError):
            accounts.parse_records(DROP.replace('| "Elmo Software Uk Holdings Limited"', "Elmo"), "r.md")


class QuoteTests(unittest.TestCase):
    def test_whole_words_only(self):
        self.assertTrue(accounts.quote_on_page("We can", "Yes, we can help."))
        self.assertFalse(accounts.quote_on_page("We can", "We cannot help."))

    def test_case_spacing_and_punctuation(self):
        page = "The average number of employees during the year was:\n 39 (2024: 41)."
        self.assertTrue(accounts.quote_on_page("average number of employees during the year was 39", page))
        self.assertTrue(accounts.quote_on_page("2024 41", page))

    def test_curly_quotes_and_pounds(self):
        self.assertTrue(accounts.quote_on_page("it's £16.6m", f"BGF{chr(0x2019)}s investment: it{chr(0x2019)}s £16.6m."))

    def test_not_there(self):
        self.assertFalse(accounts.quote_on_page("owned by Sage", "An independent company."))


class VerifyStripReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name)
        (self.run / "working").mkdir()
        (self.run / "companies.md").write_text(
            "| ID | Company | Website given |\n|---|---|---|\n| A01 | RotaCloud | rotacloud.com |\n| A02 | Rotageek | rotageek.com |\n| A03 | Missing Ltd | |\n",
            encoding="utf-8",
        )
        self.research = self.run / "working" / "research-1.md"
        self.research.write_text(KEEP + "\n" + DROP, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_verify_states(self):
        problems, states = accounts.verify(self.run, [self.research], fake(PAGES))
        self.assertEqual(problems, [])
        self.assertEqual(states["research-1.md|A01|E1"], "verified")
        self.assertEqual(states["research-1.md|A01|E4"], "pdf")
        self.assertEqual(states["research-1.md|A02|E1"], "verified")
        saved = json.loads((self.run / "working" / "evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["research-1.md|A01|E2"], "verified")

    def test_verify_reports_a_quote_not_on_its_page(self):
        self.research.write_text(DROP.replace("Elmo Software Uk Holdings Limited\"", "Sage Group plc\""), encoding="utf-8")
        problems, states = accounts.verify(self.run, [self.research], fake(PAGES))
        self.assertEqual(states["research-1.md|A02|E1"], "not-on-page")
        self.assertIn("quote not found", problems[0])

    def test_verify_marks_pages_that_will_not_load(self):
        self.research.write_text(DROP.replace("https://example.gov/owners", "https://gone.example/owners"), encoding="utf-8")
        _, states = accounts.verify(self.run, [self.research], fake(PAGES))
        self.assertEqual(states["research-1.md|A02|E1"], "could-not-load")

    def test_a_page_that_failed_is_tried_again_next_time(self):
        self.research.write_text(DROP, encoding="utf-8")
        _, states = accounts.verify(self.run, [self.research], fake({}))
        self.assertEqual(states["research-1.md|A02|E1"], "could-not-load")
        _, states = accounts.verify(self.run, [self.research], fake(PAGES))
        self.assertEqual(states["research-1.md|A02|E1"], "verified")

    def test_a_page_that_changes_is_loaded_once_more(self):
        self.research.write_text(DROP, encoding="utf-8")
        served = iter([html_page("https://example.gov/owners", "A rotating banner"), PAGES["https://example.gov/owners"]])
        _, states = accounts.verify(self.run, [self.research], lambda url: next(served))
        self.assertEqual(states["research-1.md|A02|E1"], "verified")

    def test_a_pdf_is_not_downloaded(self):
        calls = []
        cache = accounts.PageCache(self.run / "working" / "pages", lambda url: calls.append(url) or Page(url=url))
        self.assertEqual(cache.text("https://example.gov/co/filing-history/x/document?format=pdf&download=0"), ("pdf", ""))
        self.assertEqual(calls, [])

    def test_a_register_that_refuses_is_not_asked_again(self):
        calls = []

        def refuse(url):
            calls.append(url)
            return Page(url=url, status=429, error="HTTP 429")

        cache = accounts.PageCache(self.run / "working" / "pages", refuse)
        base = "https://find-and-update.company-information.service.gov.uk/company/"
        cache.text(base + "01")
        state, _ = cache.text(base + "02")
        self.assertEqual(len(calls), 1)
        self.assertIn("refused", state)

    def test_pages_are_loaded_once(self):
        calls = []
        base = fake(PAGES)

        def counting(url):
            calls.append(url)
            return base(url)

        accounts.verify(self.run, [self.research], counting)
        accounts.verify(self.run, [self.research], counting)
        self.assertEqual(len(calls), len(set(calls)))

    def test_strip_sends_keeps_and_unconfirmed_drops_without_reasons_or_evidence(self):
        accounts.verify(self.run, [self.research], fake(PAGES))
        out = self.run / "check-in" / "to-check-1.md"
        # The drop's only quote was verified, so only the keep goes to the checker.
        self.assertEqual(accounts.strip(self.run, self.research, out), 1)
        text = out.read_text(encoding="utf-8")
        self.assertIn("## A01 | RotaCloud", text)
        self.assertNotIn("Reason", text)
        self.assertNotIn("Evidence", text)
        self.assertNotIn("A02", text)

    def test_strip_sends_a_drop_resting_on_a_pdf(self):
        self.research.write_text(DROP.replace("https://example.gov/owners", "https://example.gov/accounts.pdf"), encoding="utf-8")
        accounts.verify(self.run, [self.research], fake(PAGES))
        self.assertEqual(accounts.strip(self.run, self.research, self.run / "check-in" / "to-check-1.md"), 1)

    def test_report_takes_the_checker_record_and_writes_csvs(self):
        accounts.verify(self.run, [self.research], fake(PAGES))
        overturned = KEEP.replace("- Verdict: keep", "- Verdict: drop").replace("- Problems: none", "- Problems: wrong-size")
        overturned = overturned.split("- Evidence:")[0] + "- Check notes: accounts show 45 staff, not 65.\n- Evidence:\n  - C1 | size | https://example.gov/accounts.pdf | \"average number of employees was 45\"\n"
        (self.run / "working" / "check-1.md").write_text(overturned, encoding="utf-8")
        notes = accounts.report(self.run, today="2026-11-04")
        self.assertEqual(notes[0], "3 companies: 2 drop, 1 no record")
        self.assertIn("no record for A03", notes)
        self.assertIn("checker re-checked 1, changed 1", notes)
        report = (self.run / "checks.md").read_text(encoding="utf-8")
        self.assertIn("### A01 | RotaCloud: drop", report)
        self.assertIn("Checker: changed it, was keep. accounts show 45 staff, not 65.", report)
        self.assertIn("(pdf)", report)
        rows = list(csv.DictReader(io.StringIO((self.run / "checked.csv").read_text(encoding="utf-8"))))
        self.assertEqual([r["verdict"] for r in rows], ["drop", "drop", "not checked"])
        self.assertEqual(rows[0]["rechecked"], "yes")
        keepers = (self.run / "keepers.csv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(keepers), 1)

    def test_report_flags_the_unchecked_line_a_lost_record_and_a_shared_company_number(self):
        accounts.verify(self.run, [self.research], fake(PAGES))
        (self.run / "check-in").mkdir()
        accounts.strip(self.run, self.research, self.run / "check-in" / "to-check-1.md")
        twin = DROP.replace("## A02 | Rotageek", "## A03 | Missing Ltd").replace("06783810", "08012345")
        self.research.write_text(KEEP + "\n" + DROP + "\n" + twin, encoding="utf-8")
        notes = accounts.report(self.run, today="2026-11-04", unchecked=True)
        self.assertIn("sent to the checker but no record came back: A01", notes)
        self.assertIn("possible duplicate: A01 and A03 give the same company number, 08012345", notes)
        report = (self.run / "checks.md").read_text(encoding="utf-8")
        self.assertTrue(report.splitlines()[2].startswith("Not checked:"))
        self.assertIn("Not confirmed by the script: 1 (1 in PDFs", report)

    def test_report_says_when_the_checker_changed_only_the_problems(self):
        accounts.verify(self.run, [self.research], fake(PAGES))
        rechecked = DROP.replace("- Problems: bought, customer", "- Problems: bought, customer, wrong-size")
        rechecked = rechecked.replace("- Evidence:", "- Check notes: agreed: owned by ELMO\n- Evidence:")
        (self.run / "working" / "check-1.md").write_text(rechecked, encoding="utf-8")
        accounts.report(self.run, today="2026-11-04")
        report = (self.run / "checks.md").read_text(encoding="utf-8")
        self.assertIn("- Checker: kept it a drop, changed the problems, were bought, customer. owned by ELMO", report)
        self.assertIn("- Evidence, the checker's:", report)

    def test_split_refuses_a_bad_size(self):
        self.assertEqual(accounts.main(["split", "a", "b", "c", "--size", "x"]), 2)


if __name__ == "__main__":
    unittest.main()
