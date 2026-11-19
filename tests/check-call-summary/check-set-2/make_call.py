"""Writes the second check set's call, halvercombe-follow-up.txt, as a plain-text export.

    python3 make_call.py <out file>

Kept so the call can be rebuilt exactly. Everything in it is fictional.
"""

import sys
out = sys.argv[1]
J, D, R, G = "Joe Ferris", "Dana Whitlock", "Raj Sandhu", "Gemma Okafor"
turns = [
 (J, ["Morning all. Thanks for making time again. Dana, I think Raj is with you?"]),
 (D, ["He is, yeah, we're in the same room today. Gemma's going to try and join later, she's in another meeting till half past."]),
 (R, ["Morning."]),
 (J, ["Morning Raj. So last time we mostly talked about the problem, so today I wanted to get into the detail, the IT side and what a rollout would look like. Is that okay?"]),
 (D, ["Yeah, that's perfect."]),
 (J, ["Great. Can you just remind me of the size of things? Homes, contracts, that sort of thing."]),
 (D, ["So at Halvercombe Homes we manage three thousand two hundred homes across the district.",
      "And on the contracts side, um, it's about four hundred live contracts at any one time. Repairs, grounds maintenance, lifts, gas servicing, all of that."]),
 (J, ["And where do those live today?"]),
 (D, ["Spreadsheets. One master spreadsheet, in theory, and then everyone's got their own copy, in practice."]),
 (R, ["Which is the problem."]),
 (D, ["Which is the problem, yes. [laughs]"]),
 (J, ["And what's that actually cost you? Last time you mentioned notice dates."]),
 (D, ["Yeah. So we had three contracts roll over last year because nobody caught the notice date in time. One of those was the lift maintenance contract, which we really wanted to retender."]),
 (J, ["Ouch. Okay."]),
 (R, ["Honestly, I'd pay double just to never open that spreadsheet again."]),
 (D, ["Don't tell him that, Raj. [laughs]"]),
 (R, ["Ha, yeah, scrap that. Strike it from the record."]),
 (J, ["I didn't hear a thing. [laughs] Raj, can I move on to the IT side? What do you need from us?"]),
 (R, ["Two things really. Single sign-on is non-negotiable, we're all on Microsoft, so it has to work with that. And then there's the security questionnaire."]),
 (J, ["Sure. SSO with Microsoft is standard for us, so that's fine. And the questionnaire, did you get the one I sent over?"]),
 (R, ["I did. I'll get the security questionnaire back to you, but it has to go past our DPO first, so give it a couple of weeks."]),
 (J, ["That's fine. And to scope the import, it would really help to see the contract register as it is today."]),
 (R, ["I can send you an export of the contract register, that's easy. I'll do it tomorrow."]),
 (J, ["Great, so Raj, the export tomorrow. Thanks, Raj, that's helpful."]),
 (D, ["And just so you know, Raj will be the one supporting it day to day, so it needs to be something he can live with."]),
 (R, ["Dana's being polite. The spreadsheets are a nightmare, anything is better."]),
 (J, ["Understood. On timing, what are you working towards?"]),
 (D, ["Ideally we'd want to be live before the summer. Our licence for the old document system runs out then as well, so it would be nice to do it all at once."]),
 (J, ["Okay, that's doable if we start the import in the new year. Oh, I think someone's joining."]),
 (G, ["Sorry, Gemma here, I've just joined. Ran over."]),
 (J, ["No problem at all, Gemma. We've just been through the IT side and timings. I was about to get onto price."]),
 (G, ["Good timing then. [laughs]"]),
 (J, ["So for four hundred contracts and your size, I'd say somewhere around thirty-eight thousand a year. But don't hold me to that until I've seen the register."]),
 (G, ["Okay. If the business case stacks up I don't see a problem. But it's not my call alone. Anything above fifty thousand goes to the audit committee."]),
 (J, ["Is that fifty thousand a year, or over the whole contract?"]),
 (G, ["Over the whole contract. So if we're talking three years, it goes to committee."]),
 (J, ["Understood. When does the committee next meet?"]),
 (G, ["January. Then not again until March."]),
 (J, ["Okay. So if we want to be live before the summer, January is the one to aim for."]),
 (D, ["That makes sense to me."]),
 (J, ["Right. So let me play back next steps. Raj, you're sending the register export tomorrow, and the security questionnaire once your DPO's seen it."]),
 (R, ["Yep."]),
 (J, ["I'll send a revised proposal on Friday, with a firmer price once I've seen the register. And Gemma, would it help if I put together a one-page business case for the committee?"]),
 (G, ["That would help, yes. Send it to Dana and she can shape it."]),
 (J, ["Will do. Anything I've missed?"]),
 (D, ["No, I think that's it. Thanks, Joe."]),
 (J, ["Thanks all. Speak soon."]),
]
# Seconds between turns. The last turn starts at 00:09:38.
t = 5
lines = ["Title: Halvercombe Homes follow-up", "Date: 12 November 2026",
         "Participants: Joe Ferris, Dana Whitlock, Raj Sandhu, Gemma Okafor", ""]
for i, (who, paras) in enumerate(turns):
    lines.append(f"{who}  {t//3600:02d}:{t%3600//60:02d}:{t%60:02d}")
    lines.extend(paras)
    lines.append("")
    words = sum(len(p.split()) for p in paras)
    t += 4 + int(words * 0.45) + (25 if i in (12, 21, 27, 32) else 0)
open(out, "w").write("\n".join(lines))
print("ends at", f"{t//60} min")
