"""Tests for check-call-summary's transcript.py: numbering, the quote check, coverage and the report."""

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
SCRIPT = ROOT / "skills" / "check-call-summary" / "scripts" / "transcript.py"
spec = importlib.util.spec_from_file_location("transcript", SCRIPT)
assert spec and spec.loader
transcript = importlib.util.module_from_spec(spec)
# Dataclasses look their module up in sys.modules, so register it before running it.
sys.modules[spec.name] = transcript
spec.loader.exec_module(transcript)

VTT = """\
WEBVTT

NOTE recorded by a tool

1
00:00:01.000 --> 00:00:04.500
<v Priya Shah>Thanks for making the time, Dan.</v>

2
00:00:05.000 --> 00:00:09.000 align:start
<v Dan Okafor>No problem. We've got <c>forty</c> people in support.</v>

00:01:02.250 --> 00:01:05.000
Ben: I'll send the pricing over on Friday.
"""

SRT = """\
1
00:00:01,000 --> 00:00:03,000
Priya: Hello both.

2
00:00:03,500 --> 00:00:06,000
[Dan] Hi Priya,
good to see you.
"""

PLAIN_FORMATS = {
    "stamp first": "[00:00:01] Priya: Hello.\n00:00:05 Dan: Hi there.\n",
    "name then stamp": "Priya (00:00:01): Hello.\nDan [0:05]: Hi there.\n",
    "name only": "Priya: Hello.\nDan: Hi there.\n",
    "heading lines": "Priya Shah  00:00:01\nHello.\n\nDan Okafor - 00:05\nHi there.\nSecond paragraph.\n",
}

LINES = """\
[L1] 00:00:01 Priya: Thanks for making the time, Dan.
[L2] 00:00:05 Dan: We've got forty people in support right now, maybe sixty by the summer.
[L3] 00:00:12 Priya: And who signs off on something like this?
[L4] 00:00:15 Priya: That would be me, with our CFO for anything over twenty thousand.
[L5] 00:00:20 Ben: I'll send the pricing over on Friday.
[L6] 00:00:24 Dan: Honestly, just send the contract and I'll sign it today.
[L7] 00:00:26 Ben: Ha, I wish.
"""

FACTS = """\
# Key facts

## K1. Ben sends the pricing on Friday  (kind: next-step)
- Quote: [L5] Ben: "I'll send the pricing over on Friday"

## K2. CFO signs off anything over twenty thousand  (kind: who-decides)
- Quote: [L4] Priya: "with our CFO for anything over twenty thousand"

# Doubtful labels

## D1. [L4] labelled Priya, more likely Dan
- Quote: [L4] Priya: "That would be me"
- Why: Priya asks who signs off in L3, so the answer is unlikely to be hers.
"""

SUMMARY = """\
# Call summary

Attendees: Priya, Dan, Ben

- Support team is 40 people, growing to 60 by summer.
- Dan signs off, CFO above 20k.
- Ben sent pricing.

Next steps:
- Dan to sign the contract today.
"""

CHECK = """\
# Summary: tool-a

## C1. Support team is 40 people  [said]
- From: "Support team is 40 people, growing to 60 by summer."
- Quote: [L2] Dan: "We've got forty people in support right now"
- Label: ok
- Failures: none

## C2. Growing to 60 by summer  [said]
- From: "Support team is 40 people, growing to 60 by summer."
- Quote: [L2] Dan: "maybe sixty by the summer"
- Label: ok
- Failures: overstated
- Note: "maybe" became firm.

## C3. Dan signs off, CFO above 20k  [inferred]
- From: "Dan signs off, CFO above 20k."
- Quote: [L4] Priya: "That would be me, with our CFO for anything over twenty thousand"
- Label: doubtful (D1)
- Failures: none

## C4. Ben sent pricing  [contradicted]
- From: "Ben sent pricing."
- Quote: [L5] Ben: "I'll send the pricing over on Friday"
- Label: ok
- Failures: intention-as-done, owner-or-date-wrong
- Note: Ben said he would send it on Friday. Nothing says it was sent.

## C5. Dan to sign the contract today  [said]
- From: "Dan to sign the contract today."
- Quote: [L6] Dan: "just send the contract and I'll sign it today"
- Label: ok
- Failures: tone-read-as-sincere
- Note: Ben's reply treats it as a joke.

## C6. Attendees were Priya, Dan and Ben  [inferred]
- From: "Attendees: Priya, Dan, Ben"
- Quote: [L1] Priya: "Thanks for making the time, Dan"
- Label: ok
- Failures: none

## Key facts
- K1: carried wrongly (C4)
- K2: carried (C3)
"""


def write(folder: Path, name: str, text: str) -> Path:
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


class Numbering(unittest.TestCase):
    def test_vtt_voice_tags_names_and_inline_tags(self) -> None:
        lines = transcript.number(VTT)
        self.assertEqual([l.speaker for l in lines], ["Priya Shah", "Dan Okafor", "Ben"])
        self.assertEqual(lines[1].text, "No problem. We've got forty people in support.")
        self.assertEqual(lines[2].time, "00:01:02")
        self.assertEqual(lines[0].render(), "[L1] 00:00:01 Priya Shah: Thanks for making the time, Dan.")

    def test_srt_joins_wrapped_lines_and_reads_bracketed_names(self) -> None:
        lines = transcript.number(SRT)
        self.assertEqual([(l.speaker, l.text) for l in lines], [("Priya", "Hello both."), ("Dan", "Hi Priya, good to see you.")])

    def test_plain_text_formats(self) -> None:
        for label, text in PLAIN_FORMATS.items():
            with self.subTest(label):
                lines = transcript.number(text)
                self.assertEqual(lines[0].text, "Hello.")
                self.assertTrue(lines[0].speaker.startswith("Priya"))
                self.assertTrue(lines[1].speaker.startswith("Dan"))
                self.assertEqual(lines[1].text, "Hi there.")

    def test_heading_format_keeps_paragraphs_with_their_speaker(self) -> None:
        lines = transcript.number(PLAIN_FORMATS["heading lines"])
        self.assertEqual(lines[2].speaker, "Dan Okafor")
        self.assertEqual(lines[2].text, "Second paragraph.")
        self.assertEqual([l.time for l in lines], ["00:00:01", "00:00:05", ""])

    def test_a_phrase_before_a_colon_is_not_a_speaker(self) -> None:
        for phrase in ("So the real question for us is: what next?", "So the thing is: we have no budget.", "Note to self: chase."):
            with self.subTest(phrase):
                lines = transcript.number(f"Priya: Here is the thing.\n{phrase}\n")
                self.assertEqual((lines[1].speaker, lines[1].text), (transcript.UNLABELLED, phrase))

    def test_a_spoken_time_is_not_a_heading(self) -> None:
        lines = transcript.number("Priya Shah  00:00:01\nCan we meet again?\nShall we say 2:30\nBen  00:00:09\nWorks for me.\n")
        self.assertEqual([(l.speaker, l.text) for l in lines][1], ("Priya Shah", "Shall we say 2:30"))
        self.assertEqual(lines[2].speaker, "Ben")

    def test_more_label_styles(self) -> None:
        cases = {
            "**Priya:** Hello there.\n": ("Priya", "Hello there."),
            "Priya Shah (Acme): Hello there.\n": ("Priya Shah", "Hello there."),
            "\u00c9lodie Martin: Hello there.\n": ("\u00c9lodie Martin", "Hello there."),
            "Anna van der Berg: Hello there.\n": ("Anna van der Berg", "Hello there."),
            "Speaker 1 (00:00:05):\nHello there.\n": ("Speaker 1", "Hello there."),
            "[Priya Shah] 14:02:31\nHello there.\n": ("Priya Shah", "Hello there."),
            "Date: 4 March 2026\nAttendees: Priya, Ben\nPriya: Hello there.\n": ("Priya", "Hello there."),
        }
        for text, expected in cases.items():
            with self.subTest(text):
                lines = transcript.number(text)
                self.assertEqual((lines[0].speaker, lines[0].text), expected)

    def test_a_caption_with_two_turns_is_split(self) -> None:
        two_voices = "WEBVTT\n\n00:00:01.000 --> 00:00:04.000\n<v Priya>Do you sign off?</v><v Dan>Yes, up to twenty thousand.</v>\n"
        dashes = "WEBVTT\n\n00:00:01.000 --> 00:00:04.000\n- Priya: Do you sign off?\n- Dan: Yes, I do.\n"
        for text in (two_voices, dashes):
            with self.subTest(text):
                lines = transcript.number(text)
                self.assertEqual([l.speaker for l in lines], ["Priya", "Dan"])

    def test_a_time_range_before_the_speaker(self) -> None:
        lines = transcript.number("[00:05 - 00:08] Priya Shah: Hello there.\n[01:12 - 01:15] Ben: Hi.\n")
        self.assertEqual([l.render() for l in lines], ["[L1] 00:00:05 Priya Shah: Hello there.", "[L2] 00:01:12 Ben: Hi."])

    def test_json_in_the_shapes_recorders_use(self) -> None:
        cases = {
            "sentences, seconds": {"sentences": [{"speaker_name": "Priya", "start_time": 5.2, "text": "Hello."}]},
            "speaker object, clock": [{"speaker": {"display_name": "Priya"}, "timestamp": "00:00:05", "text": "Hello."}],
            "milliseconds": {"items": [{"speaker": "Priya", "startTime": 5000, "text": "Hello."}, {"speaker": "Ben", "startTime": 90000, "text": "Hi."}]},
        }
        for label, data in cases.items():
            with self.subTest(label):
                lines = transcript.number(json.dumps(data))
                self.assertEqual(lines[0].render(), "[L1] 00:00:05 Priya: Hello.")

    def test_an_unparsed_line_is_unlabelled_not_given_to_the_last_speaker(self) -> None:
        lines = transcript.number("[00:05 - 00:08] Priya Shah: Hello.\n[00:09 - 00:12] dan_acme: We will sign by Friday.\n")
        self.assertEqual(lines[1].speaker, transcript.UNLABELLED)

    def test_an_en_dash_range_and_an_agenda_line(self) -> None:
        lines = transcript.number("09:00 - 09:30 Intro: welcome and context\n[00:05 \u2013 00:08] Priya: Hello.\n")
        self.assertEqual([(l.speaker, l.text) for l in lines], [(transcript.UNLABELLED, "09:00 - 09:30 Intro: welcome and context"), ("Priya", "Hello.")])

    def test_connector_metadata_above_the_call_is_skipped(self) -> None:
        lines = transcript.number("Title: Weekly\nOrganizer: someone\nDuration: 32 minutes\n[00:05 - 00:08] Priya: Hello.\n")
        self.assertEqual([l.speaker for l in lines], ["Priya"])

    def test_json_picks_the_conversation_not_the_summary(self) -> None:
        data = {
            "action_items": [{"text": "Dan to send pricing by Friday"}],
            "summary": {"bullets": [{"content": "Pricing discussed"}]},
            "words": [{"text": "Hello.", "start": 1.0, "speaker": "Priya"}, {"text": "Hi.", "start": 2.0, "speaker": "Ben"}],
            "transcript": [{"speaker": "Priya", "start": 1.0, "text": "Hello there."}, {"speaker": "Ben", "start": 2.0, "text": "Hi, good to see you."}],
        }
        lines = transcript.number(json.dumps(data))
        self.assertEqual([(l.speaker, l.text) for l in lines], [("Priya", "Hello there."), ("Ben", "Hi, good to see you.")])

    def test_json_paragraphs_keep_every_sentence_and_speaker(self) -> None:
        data = {"paragraphs": [
            {"speaker": "Priya", "sentences": [{"text": "Hello.", "start": 1}, {"text": "Welcome.", "start": 2}]},
            {"speaker": "Ben", "sentences": [{"text": "Hi.", "start": 3}]},
        ]}
        lines = transcript.number(json.dumps(data))
        self.assertEqual([(l.speaker, l.text) for l in lines], [("Priya", "Hello."), ("Priya", "Welcome."), ("Ben", "Hi.")])

    def test_json_times_in_milliseconds_on_a_short_call_and_clock_time(self) -> None:
        short = [{"speaker": "Priya", "start": 5000, "text": "Hello."}, {"speaker": "Ben", "start": 9000, "text": "Hi."}]
        epoch = [{"speaker": "Priya", "start": 1762250000, "text": "Hello."}, {"speaker": "Ben", "start": 1762250065, "text": "Hi."}]
        self.assertEqual([l.time for l in transcript.number(json.dumps(short))], ["00:00:05", "00:00:09"])
        self.assertEqual([l.time for l in transcript.number(json.dumps(epoch))], ["00:00:00", "00:01:05"])

    def test_json_holding_the_transcript_as_one_string(self) -> None:
        lines = transcript.number(json.dumps({"transcript": "[00:05 - 00:08] Priya: Hello.\n[00:09 - 00:12] Ben: Hi."}))
        self.assertEqual([l.speaker for l in lines], ["Priya", "Ben"])

    def test_json_without_speakers_is_unlabelled_not_lost(self) -> None:
        lines = transcript.number(json.dumps({"data": [{"text": "Hello."}]}))
        self.assertEqual((lines[0].speaker, lines[0].text), (transcript.UNLABELLED, "Hello."))

    def test_word_files_are_read(self) -> None:
        xml = (
            '<w:document xmlns:w="w"><w:body>'
            '<w:p><w:r><w:t>Priya Shah  00:00:01</w:t></w:r></w:p>'
            '<w:p><w:r><w:t xml:space="preserve">Hello </w:t></w:r><w:r><w:t>there &amp; welcome.</w:t></w:r></w:p>'
            '<w:p/>'
            '<w:p><w:r><w:t>Ben: Hi</w:t></w:r><w:r><w:br w:type="textWrapping"/><w:t>there, I don&#8217;t mind</w:t></w:r></w:p>'
            '<w:p><w:moveFrom><w:r><w:t>moved away</w:t></w:r></w:moveFrom><w:r><w:t>Ben: co</w:t><w:noBreakHyphen/><w:t>operate.</w:t></w:r></w:p>'
            '</w:body></w:document>'
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "call.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("word/document.xml", xml)
            lines = transcript.number(transcript.read_transcript(path))
        self.assertEqual(
            [(l.speaker, l.text) for l in lines],
            [("Priya Shah", "Hello there & welcome."), ("Ben", "Hi"), (transcript.UNLABELLED, "there, I don\u2019t mind"), ("Ben", "co-operate.")],
        )

    def test_a_text_file_starting_with_pk_is_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "call.txt"
            path.write_text("PK: Thanks for joining.\n", encoding="utf-8")
            self.assertEqual(transcript.number(transcript.read_transcript(path))[0].speaker, "PK")

    def test_pdf_is_refused_with_a_way_round(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "call.pdf"
            path.write_bytes(b"%PDF-1.7 rest")
            with self.assertRaises(transcript.FormatError) as caught:
                transcript.read_transcript(path)
        self.assertIn("Export the transcript as", str(caught.exception))

    def test_a_sound_tag_is_kept_and_never_a_speaker(self) -> None:
        lines = transcript.number("WEBVTT\n\n00:00:01.000 --> 00:00:02.000\n[laughs] Ha, I wish.\n")
        self.assertEqual((lines[0].speaker, lines[0].text), (transcript.UNLABELLED, "[laughs] Ha, I wish."))

    def test_unlabelled_lines_are_marked(self) -> None:
        lines = transcript.number("just some words with no speaker\n")
        self.assertEqual(lines[0].speaker, transcript.UNLABELLED)

    def test_byte_order_mark_and_windows_line_endings(self) -> None:
        lines = transcript.number("\ufeffPriya: Hello.\r\nDan: Hi there.\r\n")
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0].speaker, "Priya")

    def test_numbered_file_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write(Path(tmp), "lines.md", LINES)
            lines = transcript.read_lines(path)
        self.assertEqual(len(lines), 7)
        self.assertEqual(lines[6].speaker, "Dan")
        self.assertEqual(lines[6].time, "00:00:24")


class Quotes(unittest.TestCase):
    def setUp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.lines = transcript.read_lines(write(Path(tmp), "lines.md", LINES))

    def quote(self, start: int, end: int, speaker: str, words: str):
        return transcript.check_quote(transcript.Quote(start, end, speaker, words), self.lines)

    def test_word_for_word_ignoring_case_punctuation_and_quote_marks(self) -> None:
        self.assertIsNone(self.quote(2, 2, "Dan", "WE\u2019VE got forty people in support, right now"))

    def test_changed_words_fail(self) -> None:
        self.assertIn("not on the cited line", self.quote(2, 2, "Dan", "we have forty people in support"))

    def test_wrong_speaker_fails(self) -> None:
        self.assertIn("credited to Priya", self.quote(5, 5, "Priya", "I'll send the pricing over"))

    def test_missing_line_fails(self) -> None:
        self.assertIn("L99 is not in the transcript", self.quote(99, 99, "Dan", "anything"))

    def test_a_range_must_be_one_speaker(self) -> None:
        self.assertIn("credited to Dan", self.quote(6, 7, "Dan", "sign it today ha i wish"))

    def test_a_range_joins_its_lines(self) -> None:
        self.assertIsNone(self.quote(3, 4, "Priya", "something like this that would be me"))


class Verify(unittest.TestCase):
    def run_verify(self, check: str = CHECK, summary: str = SUMMARY, facts: str = FACTS, *flags: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            args = [
                str(write(folder, "lines.md", LINES)),
                str(write(folder, "facts.md", facts)),
                str(write(folder, "summary.md", summary)),
                str(write(folder, "check.md", check)),
            ]
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                code = transcript.main(["verify", *args, *flags])
        return code, out.getvalue()

    def test_a_good_check_passes(self) -> None:
        code, out = self.run_verify()
        self.assertEqual(code, 0, out)

    def test_invented_quote_fails(self) -> None:
        code, out = self.run_verify(CHECK.replace('"We\'ve got forty people', '"We have forty people'))
        self.assertEqual(code, 1)
        self.assertIn("C1: quote", out)

    def test_from_line_not_in_summary_fails(self) -> None:
        code, out = self.run_verify(CHECK.replace('- From: "Ben sent pricing."', '- From: "Ben will send pricing."'))
        self.assertEqual(code, 1)
        self.assertIn('C4: From "Ben will send pricing." is not in the summary', out)

    def test_an_unchecked_summary_line_fails(self) -> None:
        code, out = self.run_verify(summary=SUMMARY + "- Budget agreed at 50k.\n")
        self.assertEqual(code, 1)
        self.assertIn('summary line not checked: "Budget agreed at 50k."', out)

    def test_a_claim_on_a_doubtful_line_must_say_so(self) -> None:
        code, out = self.run_verify(CHECK.replace("- Label: doubtful (D1)", "- Label: ok"))
        self.assertEqual(code, 1)
        self.assertIn("C3: quotes L4, a doubtful label (D1)", out)

    def test_every_key_fact_must_be_marked(self) -> None:
        code, out = self.run_verify(CHECK.replace("- K2: carried (C3)\n", ""))
        self.assertEqual(code, 1)
        self.assertIn("K2: not marked", out)

    def test_unknown_verdict_and_failure_type_fail(self) -> None:
        bad = CHECK.replace("[contradicted]", "[wrong]").replace("Failures: overstated", "Failures: exaggerated")
        code, out = self.run_verify(bad)
        self.assertEqual(code, 1)
        self.assertIn("verdict 'wrong'", out)
        self.assertIn("failure type 'exaggerated'", out)

    def test_a_said_claim_needs_a_quote(self) -> None:
        bad = CHECK.replace('- Quote: [L6] Dan: "just send the contract and I\'ll sign it today"', "- Quote: none")
        code, out = self.run_verify(bad)
        self.assertEqual(code, 1)
        self.assertIn("C5: a 'said' claim needs a quote", out)

    def test_a_quote_marked_failed_is_reported_not_passed_silently(self) -> None:
        bad = CHECK.replace('"We\'ve got forty people', '"We have forty people').replace(
            "- Failures: none\n\n## C2", "- Failures: none\n- Quote check: failed\n\n## C2"
        )
        code, out = self.run_verify(bad, SUMMARY, FACTS, "--by-hand")
        self.assertEqual(code, 0, out)
        self.assertIn("check by hand: tool-a C1", out)

    def test_a_checker_cannot_mark_its_own_quote_failed(self) -> None:
        bad = CHECK.replace('"We\'ve got forty people', '"We have forty people').replace(
            "- Failures: none\n\n## C2", "- Failures: none\n- Quote check: failed\n\n## C2"
        )
        code, out = self.run_verify(bad)
        self.assertEqual(code, 1)
        self.assertIn("never by a checker", out)

    def test_part_of_a_word_is_not_a_quote(self) -> None:
        bad = CHECK.replace('"We\'ve got forty people in support right now"', '"ve got forty people in sup"')
        code, out = self.run_verify(bad)
        self.assertEqual(code, 1)
        self.assertIn("C1: quote", out)

    def test_a_quote_line_out_of_shape_is_a_problem_not_ignored(self) -> None:
        bad = CHECK.replace("- Label: ok\n- Failures: none\n\n## C2", '- Quote: [L9] "invented"\n- Label: ok\n- Failures: none\n\n## C2')
        code, out = self.run_verify(bad)
        self.assertEqual(code, 1)
        self.assertIn("C1: this Quote line is not in the format", out)

    def test_curly_quote_marks_are_read(self) -> None:
        curly = CHECK.replace('"I\'ll send the pricing over on Friday"', "\u201cI'll send the pricing over on Friday\u201d")
        code, out = self.run_verify(curly)
        self.assertEqual(code, 0, out)

    def test_short_field_lines_must_be_checked(self) -> None:
        code, out = self.run_verify(summary=SUMMARY + "Stage: Proposal\n**Budget:** 50k\n")
        self.assertEqual(code, 1)
        self.assertIn('summary line not checked: "Stage: Proposal"', out)
        self.assertIn('summary line not checked: "**Budget:** 50k"', out)

    def test_every_word_of_a_line_must_be_covered(self) -> None:
        bad = CHECK.replace('- From: "Dan to sign the contract today."', '- From: "Dan to sign the contract"')
        code, out = self.run_verify(bad)
        self.assertEqual(code, 1)
        self.assertIn('summary line not checked: "Dan to sign the contract today."', out)

    def test_bold_labels_and_colon_labels_need_no_claim(self) -> None:
        code, out = self.run_verify(summary=SUMMARY + "**Key points**\nOther:\n")
        self.assertEqual(code, 0, out)

    def test_carried_wrongly_needs_a_failure_and_carried_needs_none(self) -> None:
        bad = CHECK.replace("- K2: carried (C3)", "- K2: carried wrongly (C3)").replace("- K1: carried wrongly (C4)", "- K1: carried (C4)")
        code, out = self.run_verify(bad)
        self.assertEqual(code, 1)
        self.assertIn("K2: carried wrongly by C3", out)
        self.assertIn("K1: C4 has failures", out)

    def test_a_key_fact_marked_twice_fails(self) -> None:
        code, out = self.run_verify(CHECK + "- K2: missing\n")
        self.assertEqual(code, 1)
        self.assertIn("K2: marked more than once", out)

    def test_failures_need_a_note(self) -> None:
        code, out = self.run_verify(CHECK.replace("- Note: \"maybe\" became firm.\n", ""))
        self.assertEqual(code, 1)
        self.assertIn("C2: a claim with failures needs a Note", out)

    def test_a_doubtful_label_must_be_on_a_cited_line(self) -> None:
        code, out = self.run_verify(CHECK.replace("- Label: ok\n- Failures: none\n\n## C2", "- Label: doubtful (D1)\n- Failures: none\n\n## C2"))
        self.assertEqual(code, 1)
        self.assertIn("C1: Label says D1, but no quote cites that line", out)

    def test_key_facts_with_a_bad_quote_fail(self) -> None:
        code, out = self.run_verify(facts=FACTS.replace("send the pricing over on Friday", "send the pricing on Monday"))
        self.assertEqual(code, 1)
        self.assertIn("K1: quote", out)

    def test_a_malformed_header_is_an_error_not_a_lost_claim(self) -> None:
        code, out = self.run_verify(CHECK.replace("## C3. Dan signs off, CFO above 20k  [inferred]", "## C3 Dan signs off"))
        self.assertEqual(code, 1)


class Report(unittest.TestCase):
    def test_counts_confirm_list_and_key_facts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            facts = write(folder, "facts.md", FACTS)
            check = write(folder, "check-1.md", CHECK)
            second = write(folder, "check-2.md", CHECK.replace("tool-a", "tool-b").replace("- K2: carried (C3)", "- K2: missing"))
            out = folder / "check.md"
            with contextlib.redirect_stdout(io.StringIO()):
                code = transcript.main(["report", str(out), str(facts), str(check), str(second)])
            text = out.read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn("| | tool-a | tool-b |", text)
        self.assertIn("| claims | 6 | 6 |", text)
        self.assertIn("| inferred | 2 | 2 |", text)
        self.assertIn("| intention-as-done | 1 | 1 |", text)
        self.assertIn("| left-out | 0 | 1 |", text)
        self.assertIn("**K1** Ben sends the pricing on Friday (tool-a: carried wrongly (C4); tool-b: carried wrongly (C4))", text)
        self.assertIn("**tool-a C3** Dan signs off, CFO above 20k (rests on a doubtful label (D1))", text)
        self.assertIn("**tool-a C5** Dan to sign the contract today (may have been said for effect)", text)
        self.assertIn("| K2 | who-decides | CFO signs off anything over twenty thousand | carried (C3) | missing |", text)
        self.assertIn("**K2** CFO signs off anything over twenty thousand (tool-a: carried (C3); tool-b: missing; rests on a doubtful label (D1))", text)
        self.assertIn("**tool-a C4** Ben sent pricing (a next step the summary got wrong)", text)


if __name__ == "__main__":
    unittest.main()
