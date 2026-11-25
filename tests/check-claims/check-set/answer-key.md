# Answer key

What each planted claim should get, and the page that proves it. Written by hand on 25 November 2026, before any run of the skill, from the first publishers' own pages. Every page below was read that day with `curl` and a browser identity, and the words are copied from it. Where a page has curly quote marks, they are written straight here. None of this came from a reader, a researcher, a checker or the script.

A run's reader gives the claims their numbers, so this key names each claim by its sentence in `article.md` or `email.md` and by the draft's words. `S` numbers are the ones `claims.py number` gives.

The two drafts are made up. So are the seller Quillmere, its sender Rowan, the reader Dana and the person named Tamsin Ravenhall. Where a draft says something about a real company that its own page does not say, that is the planted problem, not a fact.

## How a run is graded

- **Required verdict** and **required type** decide pass or fail. A claim that carries the required type and other types too passes, and the other types are noted.
- **"Either"** under verdict means the spec lets the type sit on a supported claim or a differing one, so the key does not pin it.
- **A clean claim fails only if it is marked `differs`.** A clean claim that comes back `could-not-open` or `no-source` is noted, not failed.
- **A reader may split a sentence further than this key does.** Then each part is graded against the row it belongs to.

## article.md: planted

| Key | Sentence | Draft's words | Planted | Required verdict | Required type |
|---|---|---|---|---|---|
| A1 | S6 | "it costs £50 to register a company online at Companies House" | Stated as the present position. The fee is now £100 | differs | out-of-date |
| A2 | S10 | "53% of businesses had suffered a cyber breach or attack in the previous 12 months" | The survey says 43% | differs | number-wrong |
| A3 | S11 | "40% of businesses reported their most disruptive breach outside their organisation" | The 40% is of businesses that identified a breach or attack, not of all businesses | differs | base-dropped |
| A4 | S13 | "The law now caps payment terms between businesses at 60 days" | A plan made firm. The government intends to, and the bill has not passed | differs | strength-changed |
| A5 | S14 | "said in March 2026 that it intends to give every commercial contract a right to statutory interest at 8% above the Bank of England base rate, according to the law firm Mayer Brown" | The draft credits a law firm's page that repeats the government's response | supported | second-hand |
| A6 | S17 | "86% of B2B purchases stall during the buying process" | Forrester's press release says 86%. Its own blog post on the same report, the same day, says 91% | either | publisher-disagrees |
| A7 | S20 | "Salesforce's research found that teams that deeply use AI generate 77% more revenue per rep" | The research is Gong's, not Salesforce's | differs | source-mislabelled |
| A8 | S21 | "said in March 2025 that it had passed $300 million in annual recurring revenue" | Stated as a past finding. Gong has since said $500 million | supported | out-of-date |
| A9 | S18 | "Its State of Business Buying 2026 report puts the average stall at 11 weeks" | The report is sold to Forrester's clients and cannot be read. The figure is made up for this draft, so nobody knows whether the report agrees | could-not-open | none required |
| A10 | S23 | "stop up to 99.9% of spam, phishing and malware" | Understated. Google says "more than 99.9%" | either | strength-changed |
| A11 | S24 | "64% of UK finance directors delete any cold email longer than 90 words" | Made up for this draft. No source should be found | no-source | none |
| A12 | S26 | "The most important thing founders have to do at the start is to recruit users manually." | The essay says "most common unscalable thing", not "most important thing" | differs | misquoted |
| A13 | S30 | "they signed their first 50 customers that way" | The story's made-up part. The essay does not say it | no-source (never supported) | none |
| A14 | S33 | "(https://www.salesforce.com/news/press-releases/2020/12/01/salesforce-signs-definitive-agreement-to-acquire-slack/)" | The link the draft gives does not load. The fact is on Slack's copy of the joint release | supported | page-gone |
| A15 | S38 | "RollWorks' case study on PayScale reports a 500% increase in traffic from target accounts" | The first publisher's page has gone and nothing else of RollWorks' holds the claim | could-not-open | page-gone |

**The story, S30.** It must be split into three or more claims. Two parts are supported by the essay: that the Collison brothers said "Right then, give me your laptop" and set people up on the spot, and that Y Combinator calls this a "Collison installation". The third, A13, is not. A run that lists S30 as one claim fails, whatever verdict it gives.

## article.md: clean

None of these may be marked `differs`.

| Key | Sentence | Draft's words |
|---|---|---|
| A16 | S5 | "At the start of 2026 there were 5.6 million private sector businesses in the UK" |
| A17 | S27, S28 | "You can't wait for users to come to you." and "You have to go out and get them." |
| A18 | S30 | "the Collison brothers would say "Right then, give me your laptop" and set them up on the spot" |
| A19 | S30 | "a technique Y Combinator calls a "Collison installation"" |
| A20 | S33 | "Salesforce agreed to buy Slack at an enterprise value of approximately $27.7 billion" (the same claim as A14, which is supported and carries page-gone for its link) |
| A21 | S34 | "Intuit completed its purchase of Mailchimp on 1 November 2021" |

## email.md

| Key | Sentence | Draft's words | What it should get |
|---|---|---|---|
| E1 | S3 | "Tamsin Ravenhall ran credit control at her last firm for nine years" | Listed and not traced: a named person. On the confirm list |
| E2 | S7 | "Our customers get paid 11 days faster on average" | Listed and not traced: the sender's own company. On the confirm list |
| E3 | S8 | "Slack and Mailchimp, which are both part of Salesforce now" | **differs, wrong-subject.** True of Slack. Mailchimp is Intuit's. If the reader splits it in two, the Mailchimp claim must differ with wrong-subject and the Slack claim must not differ |
| E4 | S4 | "late payments cost the UK economy £11 billion a year" | Clean |
| E5 | S4 | "close 38 UK businesses every day" | Clean |
| E6 | S5 | "the National Living Wage rose to £12.71 an hour in April 2026" | Clean |

S6 ("Quillmere chases overdue invoices for you") and the first half of S8 ("It plugs into the tools you already use") are about the sender's own product. A reader may list them as own-company claims or leave them as no claim. Either passes. Tracing them fails.

## The pages

Read on 25 November 2026. "Loads" means `curl` with a browser identity got the page and the words below are in it.

**A1, Companies House fees.** `https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees`, updated 25 September 2026. Loads. In the table "Company incorporation and registration", the row "Incorporation" reads £100 online, £100 by software and £124 on paper. The words to look for: "Incorporation" then "£100".

**A2 and A3, Cyber Security Breaches Survey 2025/2026.** `https://www.gov.uk/government/statistics/cyber-security-breaches-survey-20252026/cyber-security-breaches-survey-20252026`, published 30 April 2026, commissioned by the Department for Science, Innovation and Technology and the Home Office. Loads.
- A2: "Just over four in ten businesses (43%) and around three in ten charities (28%) reported having experienced any kind of cyber security breach or attack in the last 12 months."
- A3: "External reporting was less common: among those identifying breaches or attacks, 40% of businesses and 36% of charities reported their most disruptive breach outside their organisation."

**A4 and A5, the government's response on late payments.** `https://www.gov.uk/government/consultations/late-payments-tackling-poor-payment-practices/outcome/late-payment-consultation-time-to-pay-up-government-response-web-version`, published 24 March 2026, updated 24 July 2026. Loads.
- A4: "Maximum payment terms: we intend to impose maximum payment terms of 60 days, with strictly limited exemptions, to ensure that smaller businesses are paid in a maximum of 60 days." And: "We will legislate as soon as Parliamentary time allows." The government's overview of the Commercial Payments Bill (`https://www.gov.uk/government/publications/commercial-payments-bill-factsheets/commercial-payments-bill-overview`, published 19 May 2026) still speaks of what the bill "will" do: "imposing maximum payment terms of 60 days, with strictly limited exemptions". A web search on 25 November 2026 found the bill still in Parliament and no Royal Assent. If the bill has become law and the cap is in force by the time of a later run, A4 is no longer a planted problem and this row must be rewritten.
- A5 as first written said "The government also intends to", in the present. Run 1's checker marked that out of date, because the bill has been introduced since. It was right, and the sentence now dates the intention to March 2026.
- A5: "Mandatory interest on late payments: we intend to make it a requirement that all commercial contracts will contain a right to statutory interest at 8% above the Bank of England base rate". The page the draft credits, `https://www.mayerbrown.com/en/insights/publications/2026/03/uk-government-response-to-late-payment-consultation` (31 March 2026), loads and repeats it: "All commercial contracts will be required to contain a right to statutory interest at 8% above the Bank of England base rate".

**A6, Forrester.** Both pages load.
- `https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/`, 4 December 2024: "86% of B2B purchases stall during the buying process and 81% of buyers express dissatisfaction with their chosen providers." The page's code splits "86" from "%", so its text reads "86 %".
- `https://www.forrester.com/blogs/state-of-business-buying-2024/`: "Nearly all (91%) of purchases stall at some point in the process, our survey data shows."

**A9, Forrester's 2026 report.** Forrester's release of 21 January 2026, `https://www.forrester.com/press-newsroom/forrester-2026-the-state-of-business-buying/`, loads and links to the report at `https://www.forrester.com/report/the-state-of-business-buying-2026/RES186878`. That address gives `curl` a page with no text in it. Read with the built-in reader, it shows a summary and then "Log in to continue reading this research.", "Contact us to become a client" and "This report is available for individual purchase". Neither the summary nor the release gives a figure for how long a stalled purchase waits. The draft's "11 weeks" is made up.

**A7 and A8, Gong.** Both pages load.
- A7: `https://www.gong.io/press/new-gong-labs-research-finds-ai-is-now-a-trusted-decision-maker-in-revenue-teams`: "Teams that deeply leverage AI generate 77% more revenue per representative". The research is Gong Labs' own: "the Gong Labs research team analyzed 7.1 million sales opportunities across 3,613 companies".
- A8: `https://www.gong.io/press/gong-surpasses-300m-arr-amid-increased-demand-for-ai-powered-revenue-solutions`, 5 March 2025: "surpassed $300 million in ARR for fiscal year 2025". Newer: `https://www.gong.io/press/gong-growth-accelerates-past-55-yoy-arr-tops-500m`, 12 May 2026: "Annual recurring revenue (ARR) has now surpassed $500 million."

**A10, Google.** `https://blog.google/products/gmail/gmail-security-authentication-spam-protection/`, 3 October 2023. Loads, at a longer address it redirects to. "Gmail's AI-powered defenses stop more than 99.9% of spam, phishing and malware from reaching inboxes and block nearly 15 billion unwanted emails every day."

**A12, A13, A17, A18 and A19, Paul Graham.** `https://paulgraham.com/ds.html`, "Do Things that Don't Scale", July 2013. Loads.
- A12: "The most common unscalable thing founders have to do at the start is to recruit users manually."
- A17: "You can't wait for users to come to you. You have to go out and get them."
- A18: "When anyone agreed to try Stripe they'd say "Right then, give me your laptop" and set them up on the spot."
- A19: "At YC we use the term "Collison installation" for the technique they invented."
- A13: the essay gives no count of customers signed this way. The number 50 is not on the page.

**A14 and A20, Salesforce and Slack.** The address in the draft, `https://www.salesforce.com/news/press-releases/2020/12/01/salesforce-signs-definitive-agreement-to-acquire-slack/`, answers HTTP 404 with an empty page. Slack's own copy of the joint release loads: `https://slack.com/blog/news/salesforce-signs-definitive-agreement-to-acquire-slack`: "representing an enterprise value of approximately $27.7 billion based on the closing price of Salesforce's common stock on November 30, 2020". Slack is one of the two companies that issued the release, so its copy is a first publisher's page. Both runs found that Salesforce has moved its own copy to `https://www.salesforce.com/news/press-releases/2020/12/01/salesforce-definitive-agreement-update/`. I read it after run 2: it loads, is dated December 1, 2020, and carries the same sentence. Either page supports the claim.

**A15, RollWorks.** `https://www.rollworks.com/resources/case-studies/payscale` no longer holds the case study. It lands on `https://www.adroll.com/resources`, AdRoll's resource library, which does not mention PayScale. `https://www.adroll.com/resources/case-studies/payscale` answers HTTP 404. The test of the problem, the same day, found the case study only in a web archive, which the skill does not use. If a run finds the case study on a live RollWorks or AdRoll page, the claim is supported, this row is wrong, and the key must say so.

**A16, business population estimates.** `https://www.gov.uk/government/statistics/business-population-estimates-2026/business-population-estimates-for-the-uk-and-regions-2026-statistical-release`, published 5 November 2026. Loads. "The number of private sector businesses in the United Kingdom (UK) at the start of 2026 was 5.6 million". This is the newest edition.

**A21 and E3, Intuit and Mailchimp.** `https://www.intuit.com/company/press-room/press-releases/2021/intuit-completes-acquisition-of-mailchimp/`, 1 November 2021. Loads. "Intuit has closed the acquisition of Mailchimp". Mailchimp's own page, `https://mailchimp.com/about/`, loaded in Spanish for both `curl` and the built-in reader on 25 November 2026, and says the same in Spanish.

**E3, Slack.** `https://slack.com/blog/news/salesforce-completes-acquisition-of-slack`, 21 July 2021. Loads. "today announced it has completed its acquisition of Slack Technologies, Inc."

**E4 and E5, late payments.** The government's response, as for A4: "We will legislate to end the scourge of late payments which costs the UK economy £11 billion per year and closes down 38 UK businesses every day."

**E6, National Living Wage.** `https://www.gov.uk/national-minimum-wage-rates`. Loads. Under "Current rates", the row "April 2026" gives £12.71 for "21 and over". The page also says: "An apprentice aged 21 who has completed the first year of their apprenticeship is entitled to a minimum hourly rate of £12.71."

## What run 1 changed in this key

The key was written before run 1. Two rows were changed after it, on 25 November 2026, and both changes are to the check set, not to what counts as a pass.

- **A9 was a claim about Gong's State of Revenue AI 2026 report**, planted as "behind a sign-up form". The form is real, but Gong also hosts the report as a file anyone can open, and run 1's researcher and checker both read all of it. So nothing stood in the way, and the row tested nothing. It now points at a Forrester report that is sold to clients.
- **A5's sentence was stale as I wrote it**, as its page note says. The required type, second-hand, did not change.

## Pages that refuse

Found while the key was written, and not used for any required verdict:

- `businesswire.com` answered HTTP 403 to `curl` and to the built-in reader.
- `demandgenreport.com` answered HTTP 403 to both.
- `sage.com` and `about.linkedin.com` answered HTTP 403 to `curl`.
- `mailchimp.com/about/` loads, in Spanish.

## What goes stale

Before each release, read every page above again. The likeliest to change: the Companies House fee (A1), whether the Commercial Payments Bill has become law (A4), a newer Cyber Security Breaches Survey (A2, A3) or business population estimate (A16), a newer figure from Gong (A8), the National Living Wage (E6, which changes each April), and whether RollWorks' case study has come back (A15).
