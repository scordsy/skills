# Ground truth

Every fact behind `answer-key.json`, with the page it came from. Read by hand on 4 November 2026, before any run, from Companies House, the Norwegian register and the companies' own sites. None of it came from a checker or a researcher.

`CH` is `https://find-and-update.company-information.service.gov.uk/company/`. Staff numbers are the average for the year from the company's filed accounts on Companies House, a PDF. Owners are the persons with significant control on Companies House (`CH <number>/persons-with-significant-control`).

The seller in `profile.md` is made up. Breathe HR, every company below and the two existing customers have nothing to do with it.

## Clean: should not be dropped

| ID | Company | Company and status | Owner | Staff | Sells to | Sources |
|---|---|---|---|---|---|---|
| A01 | RotaCloud | Kettle and Keyboard Ltd, 08625682, active. Footer: "A product of Kettle & Keyboard" | Three founders' holding companies, each 25 to 50%, since 19 May 2022 | 65 (year to 31 July 2025) | "5,000 small and medium businesses" | rotacloud.com; CH 08625682; accounts `filing-history/MzUxOTE3NDY1OWFkaXF6a2N4` |
| A05 | Payescape (now unsettled, see below) | Payescape Ltd, NI625726 (Northern Ireland), active | Two people, each 25 to 50%, since 2016 and 2017, as the register's summary page still shows | 83 (group, year to 31 March 2025) | Payroll, HR and time software; site has a "Small Businesses" section | payescape.com; CH NI625726; accounts `filing-history/MzUwMjUzNDYzNGFkaXF6a2N4` |
| A09 | SeedLegals | SeedLegals Ltd, 10368887, active | Two founders with significant influence, since 2016 | 155 (2025) | "Startups made easy", contracts and funding rounds for founders | seedlegals.com; CH 10368887; accounts `filing-history/MzUzODMzNTMyM2FkaXF6a2N4` |
| A12 | CyberSmart | CyberSmart Ltd, 10088945, active | No registrable person since 16 March 2023; accounts: "no ultimate controlling party" | 60 (2025) | "Cyber Essentials and Cyber Security for SMEs" | cybersmart.co.uk; CH 10088945; accounts `filing-history/MzUzMzgwNjIxMWFkaXF6a2N4` |
| A15 | Apron | Apron Payments Ltd, 13779960, active. Footer gives the number | Founder Bogdan Uzbekov since 3 December 2021; accounts: "controlled by B Uzbekov" | 68 (2025) | Bills, payroll and expenses for business owners and their accountants; accounts: founded "with a focus on supporting small businesses" | getapron.com; CH 13779960; accounts `filing-history/MzUzNjk5ODYzOGFkaXF6a2N4` |
| A18 | Commusoft | Commusoft Limited, 11611736, active. Footer: "Commusoft Ltd." | Jason Morjaria, 75% or more, since 9 October 2018 | 79 (2024; the 2025 accounts are not due until 31 December 2026) | Job management for trades businesses | commusoft.com/en-gb/; CH 11611736; accounts `filing-history/MzQ4MzI1MDc0NGFkaXF6a2N4` |

## Unsettled

Payescape (A05) was written as clean. Run 3's medium checker found, and I then confirmed on the filing itself, a change of details filed on 31 July 2026 that puts Steven Ira Sarowitz above 50% of the shares and votes from 17 July 2026 (`filing-history/MzUzNjMzNDk0NWFkaXF6a2N4`). The register's summary page still shows 25 to 50%. He has held a stake since 2017. Whether an existing investor taking control is a change of control the skill should call bought is not settled, so the key passes keep, check by hand, or a drop for bought alone.

## Planted: should be dropped

| ID | Company | Required problem types | The facts | Sources |
|---|---|---|---|---|
| A02 | Rotageek | customer, bought | Rota Geek Limited, 06783810, active. Elmo Software UK Holdings Limited has controlled it since 30 May 2025. The same company has controlled Breathe (Breathe HR's company, 03020608) since 7 October 2020, so Rotageek is in the best customer's own group. Its site says "HR powered by ELMO" and pitches to mid-market and enterprise. | CH 06783810 and 03020608 persons with significant control; rotageek.com |
| A03 | Capsule CRM | wrong-size | Footer: "Capsule is a service of Zestia Ltd, registered in England with No 06418281". Zestia Limited employed 35 people in 2025, excluding directors. Owned by Bidco Koru Limited since 13 July 2020, more than five years ago, so not bought. | capsulecrm.com; CH 06418281; accounts `filing-history/MzU0MTIwNTM4NWFkaXF6a2N4` |
| A04 | Feefo | competitor | feefo.com lands on business.feefo.com, "Verified Customer Reviews Platform". | business.feefo.com |
| A06 | Weekly10 | bought | https://www.weekly10.com lands on https://zensai.com/; https://weekly10.com does not load. Its company, Zensai UKI Ltd (08225904), was Binary Geek Limited. The founder ceased control on 8 August 2023, and Omni Elearning 2017 ApS (Denmark) controls it now. | weekly10.com; CH 08225904 |
| A07 | Pinpoint | not-in-country | Pinpoint's legal page: "The Infuse Group Limited (t/a Pinpoint Software)", St. Helier, Jersey. Name trap: Pinpoint Software Limited (11298465) on Companies House is a Bicester company, dissolved on 11 October 2022, with nothing to do with it. Closed would be wrong. | pinpointhq.com/legal; CH 11298465 |
| A08 | Zestia | duplicate | The company behind Capsule CRM, A03: same company number, 06418281. zestia.com is a short page about Capsule. | zestia.com; capsulecrm.com |
| A10 | Wejo | closed | Wejo Limited, 08813730: "In Administration". https://wejo.com does not load. | CH 08813730 |
| A11 | Interact | bought, wrong-fit | Interact's company is Odyssey Interactive Limited (03275461), controlled by Hasgrove Limited (05247414). Maia Bidco Limited has controlled Hasgrove since 18 December 2025. Site: "The AI- native modern intranet for enterprises". Name trap: Interact Software Limited (01235166) is a family-owned Aylesbury company, active and unrelated. Closed would be wrong. | interactsoftware.com; CH 03275461, 05247414, 01235166 |
| A13 | Goodlord | wrong-size | goodlord.co lands on www.goodlord.com, the same company: Oh Goodlord Ltd, 08933499, active, no registrable person since 15 October 2020. 318 employees in the group and 277 in the company, year to 31 August 2025. | goodlord.com; CH 08933499; accounts `filing-history/MzUyMjE3MTc2OGFkaXF6a2N4` |
| A14 | Engager | bought, wrong-size | Client Engager Online Limited, 11652499, active, at TaxCalc's Wokingham address. Malbec Bidco Limited has controlled it since 11 June 2025; the founder ceased the same day. 3 employees, year to 31 March 2025. Site: "With TaxCalc and Engager working together". Name trap: Companies House lists two Engager Ltd companies (14496023 and 12208724), both dissolved and unrelated. Closed would be wrong. | engager.app; CH 11652499; accounts `filing-history/MzQ5NjAyMzMwNmFkaXF6a2N4` |
| A16 | Mention Me | competitor | "The Referral Marketing Platform Brands Trust". | mention-me.com |
| A17 | Fiken | not-in-country | Fiken AS, organisation number 913312465, Karl Johans gate 41A, Oslo, Norway. 81 employees on the register. Accounting software "for de små bedriftene". | data.brreg.no/enhetsregisteret/api/enheter/913312465; fiken.no |
| A19 | Titania | wrong-website | https://titaniasecurity.com does not load. Titania's site is www.titania.com: Titania Ltd, 06870498, active, owned by Titania Group Limited since 30 May 2017. It "secures the networks of the largest enterprises, service providers, and government organi[sations]". | titania.com; CH 06870498 |
| A20 | Crunch | customer | Named in the profile as an existing customer. crunch.co.uk loads. | profile.md |

## Notes

- **Problems that may also be found.** A planted company can carry other true problems: Rotageek sells to mid-market and enterprise, Weekly10's site is now another company's, Wejo's site does not load. The key requires only the problem types proved above, and the grader lists any others as notes. A note is not a failure, and not proof the extra type is right.
- **The five-year line.** Five years before 4 November 2026 is 4 November 2021. Capsule's owner (July 2020), Breathe's owner (October 2020) and Titania's owner (May 2017) are older, so none of them is bought. RotaCloud's 2022 owners are its founders' own companies, not a sale.
- **What goes stale.** Owners, administrations and websites change. Before each release, re-read every source above: the status and owners on Companies House, the latest accounts' staff figure, and each website's address and wording.
