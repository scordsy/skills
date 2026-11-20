# Profile

The goal is a profile sharp enough that someone who has never met this person could say whether a company on the list fits. Every check after this measures against it.

## How to ask

- **One question per message.** A message asks one numbered question below and nothing else: no second question, no question this file does not have, and never a request for the list being checked, which comes after the profile is approved. Where a question has parts (questions 4 and 5), they go in that one message as one list. A draft offered for a yes is the question, not an extra one. Wait for the answer.
- **Draft before you ask.** Wherever you can guess, offer the guess to confirm: "From Breathe's site it looks like a UK software company selling HR tools to small businesses. Is that what makes it a good customer?" Correcting a draft is easier than writing an answer.
- **"Not sure" is always a fine answer.** Use the default given below, say what you used, and mark it as an assumption.
- **Never ask what you already know.** If an earlier answer covered a later question, offer it as a draft.
- **Build it from the user's answers, never from the list.** The profile is what the list is checked against, so nothing in it may come from the list. If the user has already given the list, take no competitor, customer or draft from it.
- Keep it to a few minutes.

## The questions, in order

### 1. What you sell

Ask for their website, or what they sell in a line. With a website, read the homepage and up to 2 more pages from the same site (pricing, customers). Use only your built-in page reading or `curl`. Draft "you sell X to Y" and ask them to correct it.

This answer decides the competitor check, so do not skip it. Default if not sure: none. Say the competitor check will only catch companies they name in question 5.

### 2. Your best customers

Ask for one to three customers the list should look like, with their websites. Read each customer's homepage and about page, and look it up once on its country's free register (`registers.md`) to see who owns it: a list built to look like a customer often holds its sister companies. Then draft what they have in common, in four lines: **what they sell**, **who they sell to**, **where they are**, **how big they are** (say where any size figure came from, or "not known").

### 3. Why they are your best customers

Ask what makes them good customers: what they buy, how fast they signed, the deal size, who you deal with there, anything else. This is often not on any website, and it is the part most lists miss.

Default if not sure: "they look like the customers above". Mark it as an assumption.

### 4. Hard limits

Draft these from the answers so far and ask for a yes or a change to each:

- **Countries** where a company must be based. Default if not sure: no limit. Say in one line that evidence for size and owners is only as good as each country's free company register, so in some countries size will often come back unverified and need a check by hand.
- **Staff range**, such as 50 to 200. Default if not sure: no limit, and size is not checked.
- **Who buys from you there**, such as "the marketing team".
- **Owned by a larger group:** does a company bought by a larger group still count? Default: no, because the buying decision often moves to the owner. Private equity ownership that is older than five years counts as independent unless they say otherwise. A company a trading group bought longer ago still counts as group-owned.

### 5. Who to drop on sight

Ask for both, in one message:

- **Your competitors**, by name. Suggest any you can see on the user's own site, and include the kind of product as well as the names ("any review or referral platform").
- **Your existing customers**, optionally, as names or a file. Say why in one line: a list built to look like your customers will contain some of them.

Every name here comes from the user's answer, or from the user's own site with the user's yes. **Never add a company from the list being checked**, even one you have seen and are sure of. Finding competitors and customers on the list is the check's job, and a name added here from the list hides whether the check can catch it by the kind of product.

## The profile file

Write `profile.md` in the run folder, in exactly this shape, and show it. Wait for the user to approve or edit it. **Check nothing before approval.**

```
# Profile

- You sell: <one line>
- Best customers: <name (website), owned by <group, or "independent", or "not found">>; <...>
- What they have in common:
  - Sell: <what>
  - To: <whom>
  - Based in: <where>
  - Size: <staff, with where the figure came from, or "not known">
- Why they are good customers: <answer>
- Countries: <list>, or no limit
- Staff range: <from> to <to>, or no limit
- Buyer: <who buys from the user>
- Owned by a larger group: not wanted | fine
- Competitors to drop: <names and kinds of product, from the user's answers>, or none given
- Existing customers to drop: <names from the user's answers, or "file: customers.csv">, or none given
- Assumptions: <each answer filled in by a default>, or none
```

**In a chat:** show the profile in your reply and ask for approval there.
