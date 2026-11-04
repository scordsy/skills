# Company registers

Where to find status, owners, previous names and staff numbers for free, by country. Researched on 4 November 2026 from the registers' own pages and the governments' pages about them. Where a fact could not be confirmed on an official page, this file says "not confirmed": treat it as a lead, not a fact.

## Reading a register

- **Read it the way a person would.** Search for the company, open its page and the one or two pages you need, and move on. Never page through results, never loop over a register, never run a script against one.
- **Keep to each register's published limits** (below). Every researcher in a run shares one internet connection, so a limit per hour is shared between them.
- **Never get past a bot check, CAPTCHA, login or payment.** Several registers turn away anything that is not a full browser (marked "blocks automated readers" below). If one turns you away, stop using it for this run and mark what it would have given as `unverified`.
- **Name traps.** Match a register entry to the company by website, address or directors, never by name alone.
- **Where nothing below fits**, the company's own site (about, terms, privacy and imprint pages often name the legal entity and its owner) and the buyer's own announcement of a takeover are still primary sources.

## By country

| Country | Register | Free without an account | Notes |
|---|---|---|---|
| United Kingdom | Companies House: find-and-update.company-information.service.gov.uk | Status, owners (persons with significant control), previous names, filed accounts | Staff numbers are in the notes to the accounts ("average number of persons employed"), a PDF. Companies House says its search is "not intended to be a source for bulk downloads" and heavy users "may be denied access to these services without notice". |
| Ireland | Companies Registration Office: core.cro.ie | Status and basic details (not confirmed) | Documents and accounts are paid. Beneficial owners are closed to the public. Blocks automated readers. |
| United States | No national register. One per state, such as Delaware and California | Varies by state. Delaware charges for status | Delaware "strictly prohibits mining data". Listed companies only: SEC EDGAR (sec.gov) has every filing free, including previous names, and the annual 10-K must state the number of employees. EDGAR asks callers to say who they are and may refuse anonymous readers. |
| Canada | Federal: Corporations Canada (ised-isde.canada.ca). Québec: Registraire des entreprises. Other provinces: their own registers | Federal: status, individuals with significant control, name history. Québec: status, top shareholders and ultimate beneficiaries, previous names, number of employees in Québec (declared by the company) | Most companies are provincial. Ontario's profile report is paid. |
| Australia | ASIC (asic.gov.au) and ABN Lookup (abr.business.gov.au) | ABN Lookup: whether the business number is active or cancelled | ASIC's free fields do not include officeholders; extracts are paid. No staff numbers. |
| New Zealand | Companies Office: app.companiesoffice.govt.nz | Status, shareholdings with percentages, ultimate holding company, previous names | No staff numbers. |
| Singapore | ACRA Bizfile: bizfile.gov.sg | Status and registered address | Owners and officers are in a paid profile. |
| India | Ministry of Corporate Affairs: mca.gov.in | Nothing useful without a login (not confirmed) | Documents are paid. Blocks automated readers. |
| Germany | Handelsregister: handelsregister.de. Accounts: unternehmensregister.de | Register prints, including history and previous names; shareholder lists for GmbHs; published accounts | Staff numbers are in the annual accounts (average employees). **Limit: no more than 60 searches or company views an hour, and IP addresses are blocked.** Use it only where the company's own site leaves status or owner in doubt. The whole run shares the 60, so at most 5 searches or views per researcher or checker, and never retry after a refusal. |
| France | Annuaire des Entreprises: annuaire-entreprises.data.gouv.fr. Same data from the government's free, keyless lookup: recherche-entreprises.api.gouv.fr | Status and closure date, officers, staff band (INSEE "tranche d'effectif") with its year | The website blocks automated readers; the keyless lookup does not. Beneficial owners are restricted. |
| Netherlands | KVK: kvk.nl/zoeken | Name, address and KVK number only | Officers, history and staff numbers are paid. |
| Belgium | Crossroads Bank for Enterprises: kbopub.economie.fgov.be | Status, legal situation, directors | Filed accounts at the National Bank (consult.cbso.nbb.be) are reported free and include staff numbers (not confirmed; blocks automated readers). |
| Spain | Registro Mercantil (paid) and the official gazette BORME (boe.es, free) | BORME notices: dissolution, insolvency, name changes, sole-shareholder changes | A gazette, searched by date, not a company page. No staff numbers. |
| Italy | Registro Imprese: registroimprese.it | Address, legal form and activity only (not confirmed) | Status, owners and staff numbers are in the paid "visura". |
| Switzerland | Zefix: zefix.admin.ch, linking to 28 cantonal registers | Extracts are free | No staff numbers. |
| Austria | Firmenbuch | Nothing free: extracts are paid | Status is available free through the EU search below (not confirmed). |
| Denmark | CVR: datacvr.virk.dk | Status, owners, beneficial owners, staff band (from payroll reports) | Blocks automated readers. **Advertising protection:** some companies are flagged "reklamebeskyttet", and the CVR Act says their register data "ikke må benyttes af private juridiske enheder med henblik på direkte markedsføring" (must not be used by private businesses for direct marketing). If you see the flag, put it in Conflicts and the Reason. |
| Norway | Brønnøysund: virksomhet.brreg.no. Same data from the free, keyless lookup data.brreg.no/enhetsregisteret/api/enheter/{organisation number} | Status (including bankruptcy and winding up), previous names, exact number of employees, key figures from filed accounts | The website needs JavaScript; the keyless lookup is the readable route. Beneficial owners are not public. |
| Sweden | Bolagsverket: foretagsinfo.bolagsverket.se | Status (not confirmed) | Annual reports are paid. Shows an image CAPTCHA to automated readers. |
| Finland | PRH and YTJ: ytj.fi. Free, keyless lookup: avoindata.prh.fi | Register status, name history | Staff numbers and accounts are not free. |
| Estonia | e-Business Register: ariregister.rik.ee | Free basic data; quarterly workforce from the tax board is reported on the portal (not confirmed) | Blocks automated readers. |
| Poland | KRS: prs.ms.gov.pl/krs. Free, keyless lookup: api-krs.ms.gov.pl | Current extract: status, liquidation and insolvency, shareholder fields. Filed financial documents are free to download | Where staff numbers sit in the accounts is not confirmed. |
| Czechia | ARES: ares.gov.cz | Staff band from the statistics office's register | The statistics office says these bands are estimates, not proof: say so in the record. |
| Slovakia | Register of financial statements: registeruz.sk | Size code from the statistics office, filed accounts | |
| Other EU countries, Norway, Iceland, Liechtenstein | e-Justice "Find a company": e-justice.europa.eu | Status and representatives, under EU law (not confirmed) | A fallback for status where the national register is paid. No owners or staff numbers. |

## Where staff numbers come from, in short

- **On the register page or a keyless lookup:** Norway (exact), Denmark, France, Czechia and Slovakia (bands), Québec (declared).
- **Inside free filed accounts:** United Kingdom, Germany, Poland, and US listed companies (the 10-K).
- **Nowhere free:** most other countries. Use a figure the company states on its own site, with the page, or mark size `unverified`.
