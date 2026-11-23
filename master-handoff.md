# RELAY — Complete master project handoff

**Status date:** 2026-11-23. **Purpose:** Preserve Relay's startup discovery, strategy, and current build state for future sessions. The research below records what was said and researched; it is not a validated product specification. The founder is 14 with a $0 starting budget.

## Current project state

The invitation-only family release is live at [Relay Production](https://relay-v3-six.vercel.app/). Section 25 records the Actions release and multi-family onboarding status. Section 27 records the trained notice model on protected Preview. The prototype summary immediately below is historical.

The V3 development build supersedes the implementation snapshot immediately below. See §17 for the runtime and open work, and §18 for the Modern Family Home redesign. The original prototype notes and research remain historical context.

- **Product vision:** Relay is an AI product for families. Its provisional direction is a trusted family-commitment system that helps caregivers understand obligations, coordinate responsibility, and follow through when plans change. This direction has not been validated or approved as a final specification.
- **Architecture and implementation:** A local browser prototype exists. It uses plain HTML, CSS, and JavaScript modules, with `localStorage` for browser-only persistence and Node's built-in test runner for commitment-state and presentation tests. The interface was substantially refined on 2026-11-21 for clearer family workflow and responsive use. It has no backend, accounts, AI extraction, integrations, or real shared coordination. This is an exploratory build, not a validated product architecture.
- **Project files:** `master-handoff.md` is the primary continuity document; `AGENTS.md` contains Codex session instructions. `README.md` documents the prototype, `DESIGN.md` its maintained design context, `index.html` and `styles.css` its interface, `src/` its behavior and presentation helpers, and `tests/` its domain and presentation tests. `output/playwright/` contains browser QA captures. The handoff was previously named `relay-master-handoff.md` and was renamed without removing its research.
- **Decisions and outstanding work:** The founder authorized beginning the build stage and delegated the first version choice to Codex. The chosen version is a local, manual-entry commitment workflow so the key idea can be tried without claiming unsupported AI or sharing behavior. The market direction remains provisional. The next substantive product step is to put this workflow in front of prospective families, identify the specific recurring failure it solves, and compare existing tools in practice.
- **Maintenance:** After significant milestones and before ending a Codex session, reconcile this status with the actual project files and update it while preserving the historical research and source archive.

## 1. How Relay emerged and changed

1. The founder first asked for 15 realistic, original online startups that a 14-year-old could start at $0 without cold calls, with guardian help where needed. The answer favored a grant-evidence locker, permit-renewal desk, and accessibility fix queue. These were not Relay concepts; they showed the initial bias toward concrete pain, narrow entry markets, and low-cost validation.
2. The founder then asked for 30 more ambitious AI opportunities with recognizable-brand and viral-demo potential, while remaining commercially honest. Relay appeared as **an AI family action layer**: turn school emails, sports schedules, messages and paper forms into a calm shared plan. It ranked first in that exercise. The early thesis was frequent family friction, a compelling before/after demonstration, potential recurring use, and a path to word of mouth. The conclusion explicitly warned that privacy, reliability and big-platform competition were critical.
3. The founder supplied a broader Relay vision: an intelligent layer between people and everyday responsibilities. Inputs could include emails, screenshots, school announcements, documents, messages, calendars, reminders and notifications. Potential outputs: deadlines, actions, schedules, conflict detection, changed plans, responsibility sharing, memory and schedule Q&A.
4. Deep competitor research overturned the initial claim of differentiation. Sense, Kikko, FamilyGenie, Plancove, Fambee, Cozi Max and others already offer message/photo/email-to-calendar capture. Google CC, announced for families and groups in 2026, explicitly claims a shared brief, task/calendar updates as plans change, selective sharing and form help. Gemini's Nov. 17, 2026 task announcement included free rollout in several countries, email forwarding, calendar updates and a family carpool-conflict example. **The original broad family assistant pitch is crowded.**
5. The recommendation therefore shifted **provisionally** to **Relay for family commitments**: retain the source of each obligation, show what changed, identify who accepted responsibility, and record whether the task was completed. This is a research hypothesis, not a verified market gap. Google and other competitors could add these features. The desired advantage is measured reliability and trusted household workflow, not a proprietary language model or a longer feature list.

## 2. Founder and project identity

- Founder: age 14; $0 initial budget; laptop/phone access; willing to learn coding and AI; prefers online distribution with little cold calling or constant direct selling; guardian can help with accounts, contracts, payments, legal and privacy matters. Ambition: a substantial, recognizable technology company, not a side hustle.
- Name: **Relay** is a working company/product name. No trademark or domain check was completed.
- Original problem: family information arrives across incompatible apps, emails, chats, documents and paper. Capturing dates is tedious and important items can be missed.
- Current problem thesis: even after a date enters a calendar, families may not know **what must happen, who is responsible, whether a change invalidated the plan, and whether the obligation was actually fulfilled**.
- Current provisional vision: a trusted layer for shared family commitments, initially for households with school-age children and at least two adults or caregivers dividing pickups, forms, activities and other logistics.
- Long-term ambition: if accuracy, retention and trust are proven, expand to more household obligations, co-parenting, elder-care handoffs and possibly a broader cross-platform responsibility layer. This expansion is speculative.
- Core philosophy: reduce real work and uncertainty. A polished summary is insufficient if the family still has to remember, reconcile and chase everything.

### Understand → Coordinate → Follow Through

This framework is a **synthesis of the conversation**, not a previously approved formal specification:

| Stage | What Relay would need to do | Risk to control |
|---|---|---|
| **Understand** | Ingest a user-shared source; identify obligations, dates, people and uncertainty; preserve a link to the original wording; compare new information with known plans. | Hallucinated or missed obligations; inaccessible sources; overbroad data collection. |
| **Coordinate** | Show consequences of changes and conflicts; ask the right caregiver to accept a specific responsibility; respect family permissions and one-time exceptions. | Unclear ownership; accidental disclosure; too many notifications. |
| **Follow Through** | Track accepted, outstanding and completed commitments; attach confirmations where useful; escalate only unresolved important items. | A checkmark falsely implying a form, payment or pickup was completed. |

Relay should become a dependable way to know the state of family commitments as life changes. It should **not** position generic email summarization, screenshot-to-calendar capture, a chatbot, a generic task manager, a broad autonomous agent, or a viral demo alone as its competitive advantage.

## 3. Earlier 30-startup discovery ranking

These scores were subjective screening judgments, **not measured market data**. The original scoring dimensions, each out of 10: O originality; I innovation; D documented demand for the underlying problem; U usefulness if executed well; R revenue potential; S social-demo appeal; B brand potential; V investor appeal; M market opportunity; A possible competitive advantage; X scalability; F feasibility for a 14-year-old with $0. Total out of 120. The ranking was not a pure score sort, because data, distribution and safety barriers adjusted judgment. Names outside Relay are preserved to show the choice context, not as Relay product decisions.

|Rank|Idea|O|I|D|U|R|S|B|V|M|A|X|F|Total|
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|1|Relay|7|8|8|9|7|9|9|8|9|6|9|7|97|
|2|Proofline|7|8|10|9|7|9|9|7|10|5|9|6|96|
|3|CivicScene|8|9|7|8|7|10|9|8|8|7|8|5|94|
|4|AccessReplay|8|8|9|9|8|8|7|8|8|7|8|6|94|
|5|CareSignal|7|8|9|9|7|8|8|8|9|6|8|5|92|
|6|FixPath|6|8|8|9|7|10|9|6|8|4|8|7|90|
|7|GrantProof|7|7|8|9|7|6|6|7|7|7|8|8|87|
|8|PermitPilot|6|7|8|9|8|6|7|7|8|6|8|6|86|
|9|DecisionMirror|8|9|6|8|8|10|9|8|9|6|8|3|92|
|10|WasteWindow|7|8|8|8|5|9|8|6|8|5|8|6|86|
|11|SkillTrace|7|8|7|8|7|8|8|8|8|6|8|6|89|
|12|ClaimTrail|7|7|8|8|7|7|7|6|8|6|7|5|83|
|13|ExplainThisPlace|8|8|7|8|6|9|8|7|8|6|8|5|88|
|14|ReturnRoute|5|7|8|8|7|9|8|6|8|4|8|7|85|
|15|VolunteerPulse|7|7|7|8|6|7|6|6|7|6|7|7|81|
|16|LocalSignal|7|8|7|8|7|8|7|7|8|6|8|5|86|
|17|ProofCart|6|7|8|8|7|8|8|6|9|4|9|5|85|
|18|LearningLoop|5|7|9|9|7|8|8|6|10|3|9|5|86|
|19|RouteAble|8|8|7|9|6|9|8|7|8|7|7|3|87|
|20|HomeEnergy Story|6|7|7|8|7|8|7|7|8|5|8|4|82|
|21|DisputeDesk|6|7|8|8|6|8|7|5|8|5|7|6|81|
|22|SourceLens|8|8|7|8|5|9|8|6|8|5|8|5|85|
|23|RepairMatch|6|7|8|8|8|8|8|7|8|6|7|3|84|
|24|QuietFeed|6|7|6|7|5|7|7|5|8|3|9|7|77|
|25|AfterMove|6|7|8|8|6|8|7|5|8|5|7|6|81|
|26|SmallBiz Memory|5|6|8|8|7|5|6|5|8|3|8|8|77|
|27|ClubContinuity|7|6|7|8|4|5|6|4|6|6|6|8|73|
|28|FairShift|5|7|8|8|8|7|7|6|8|4|8|4|80|
|29|EventFlow|6|7|6|7|6|9|7|5|7|5|7|5|77|
|30|MemoryMap|4|6|7|7|6|7|7|4|9|2|9|7|75|

The five originally selected for depth were Relay, Proofline, CivicScene, AccessReplay and CareSignal. Relay won because its pain seemed frequent, its demo understandable, and its early version possible without large partnerships. **That selection predated detailed competitor work and should be discounted accordingly.** DecisionMirror's high score but ninth rank reflected heavy data/retailer barriers; RouteAble's low feasibility reflected safety and coverage concerns. No other idea was formally ruled out forever.

## 4. Detailed competitor map (researched through 2026-11-21)

Feature descriptions below are documented company claims, not independent performance tests. Prices are published figures seen during research; they can vary by region, plan or date. “Not verified” means no reliable current figure was established. Weaknesses are marked as evidence or strategic inference; no systematic hands-on accuracy testing was done.

|Competitor|Audience, verified offering and strength|Published price found|Relay comparison and threat / supported limitation|
|---|---|---|---|
|[Sense](https://getsense.ai/help/en)|Families; calendar, forwarded-email extraction, screenshots/PDFs, reminders, lists, chores, documents, sync. Broad family suite.|Free; [premium advertised $6.99/month/household](https://getsense.ai/ai-chief-of-staff).|Direct competitor. Email-to-calendar, what-to-bring reminders, and broad family organization already covered. Low price and breadth are threats. No verified systematic defect rate.|
|[Kikko](https://kikko.ai/)|Busy parents; forwarded school emails, flyers, messages, PDFs, schedule Q&A; original source attached to an event.|€9.99/month or €79.99/year after 14-day trial.|Direct. Source attachment and multiple input methods are **not unique** to Relay. New product with limited independent review evidence.|
|[FamilyGenie](https://www.familygenie.ai/)|Parents; universal school/family inbox for email, screenshots, photos, files; dates, amounts and deadline extraction.|Beta pricing not verified.|Nearly the original Relay pitch. Its competitor comparison is company-authored, not a controlled test.|
|[Fambee](https://www.getfambee.com/)|Families; reads email, suggests events, shares context, approval for consequential actions; text option on Android.|[Free; Pro $6.99/month or $59.99/year](https://www.getfambee.com/support).|Direct. Approval controls and mental-load language already present. Android app had a waitlist at research time, but text access existed.|
|[Marlow](https://meetmarlow.ai/)|Families; early proposition for school messages, changing schedules, reminders, briefings.|[Early pricing shape $12–$20/month; premium $24–$39/month](https://meetmarlow.ai/pricing).|Very similar positioning. These were presented as proposed tiers, **not verified paid adoption**.|
|[Milo](https://www.gomilo.app/)|Families; assistant via text, call or chat.|Not verified.|Competes on low-friction family assistance. Do not conflate it with a different personal iOS app named Milo found in Reddit search results.|
|[Ohai](https://www.getohai.com/index.html)|Households; family email/calendar integration and daily action view; earlier materials mention human assistants.|Current reliable price not verified.|Experienced family-tech competition. [Trustpilot](https://www.trustpilot.com/review/ohai.ai) showed 12 reviews with praise and negatives; too small to infer recurring patterns.|
|[Plancove](https://plancove.app/about/)|Parents; reviewed per-child school-message plan; approved items to Apple Calendar/Reminders; iPhone only at research time.|$4.99/month or $39.99/year.|Direct school-focused rival. Android/web availability might be an opening, but platform coverage alone is weak defense.|
|[Cozi](https://www.cozi.com/compare-plans/)|Families; mature shared calendar, lists, chores and meals; Max AI email-to-event import.|Free; Gold $39/year; Max $79/year.|Large installed base and low prices. [App Store](https://apps.apple.com/us/app/cozi-family-organizer/id407108860?platform=iphone&see-all=reviews) showed 4.8 and roughly 404K ratings. One reviewer reported occasional altered times and requested event reuse/night-shift support; not a measured failure rate.|
|[FamilyWall](https://www.prod.familywall.com/pricing.html)|Families; calendar, tasks, messaging, location, meals, documents, circles.|Free; $7.99/month or $44.99/year Premium.|Broad low-cost suite. [One App Store reviewer](https://apps.apple.com/us/app/familywall-family-organizer/id496889629?see-all=reviews) requested cross-circle conflict alerts, recurring pickup exceptions and less duplicate entry.|
|[Skylight Calendar](https://skylight.zendesk.com/hc/en-us/articles/51833126965019-Subscription)|Families; wall display and Plus features including Magic Import.|Hardware plus optional Plus; exact current local price not established.|Physical household presence. [Reddit](https://www.reddit.com/r/skylightcalendar/comments/1pd882d/so_confused_about_the_subscriptions/) includes subscription confusion; anecdotal.|
|[Hearth Display](https://hearthdisplay.com/products/2-year-membership)|Families; wall display, routines, tasks, rewards, AI helper.|Hardware listed around $699 before offers; membership $9/month or less on long terms.|Household visibility and brand. Hardware is a different purchase decision from software-only Relay.|
|[Google CC](https://blog.google/innovation-and-ai/models-and-research/google-labs/cc-expanding-to-groups/)|Families/groups; shared daily brief, selected information sharing, task/calendar updates as things change, form help, Google integrations.|Specific Labs-offering price not verified.|**Most dangerous direct threat.** Claims change handling and follow-through, so Relay must prove a narrower superior outcome.|
|[Google Gemini](https://blog.google/innovation-and-ai/products/gemini-app/tasks-in-gemini-free-new-features/)|General consumer agent; Nov. 17 announcement showed email forwarding, calendar updates, family carpool conflict and broader task completion.|Partly free rollout in named countries; account and region restrictions vary.|Distribution, Gmail/calendar access, model and agent capabilities dwarf a startup's. Broad general-assistant competition is implausible.|
|[ChatGPT](https://help.openai.com/en/articles/20001494-connecting-and-managing-app-accounts-in-chatgpt)|General assistant with account connections and [scheduled tasks](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt).|Free; [Plus $20/month](https://help.openai.com/en/articles/6950777-what-is-chatgpt).|Strong reasoning and integrations. Family-specific shared workflow could distinguish Relay, but feature gap may narrow.|
|[Microsoft Copilot in Outlook](https://techcommunity.microsoft.com/blog/Outlook/copilot-in-outlook-new-agentic-experiences-for-email-and-calendar/4499798)|Outlook/work users; agentic email and calendar management.|Plan-dependent; not verified.|Strong within Microsoft households, though cited positioning is work-heavy.|
|[Motion](https://www.usemotion.com/pricing)|Professionals/teams; AI task scheduling, calendar, projects, documents.|Pro AI shown $19/seat/month on viewed selection.|Strong schedule optimization. Family communications less central to its positioning; could expand.|
|[Reclaim AI](https://reclaim.ai/pricing)|Individuals/teams; schedules tasks, habits, meetings, focus time and buffers.|Free Lite; Starter shown $10/seat/month.|Optimizes known commitments; not primarily a family-message product. Could add capture.|
|[Todoist](https://www.todoist.com/ai-tools)|Task users; mature task manager, AI assist, general assistant connectors, email/image/document capture.|[Free; Pro $7/month or $60/year](https://www.todoist.com/es/help/account-and-billing/plans/todoist-plans-pricing-and-billing-faq-Vq2z0HWL6).|Task capture is commodity. Relay needs household coordination rather than another list.|
|[Notion AI](https://www.notion.com/pricing)|Individuals/teams; flexible docs, databases, calendar, AI/agents.|Free; Plus shown $10/member/month; AI entitlements vary.|Flexible but requires configuration; ease could matter to families.|
|[ParentSquare](https://www.parentsquare.com/)|Schools/families; school communication.|Institution purchased; household price not applicable.|Source platform. May improve its own family-facing organization; direct data access cannot be assumed.|
|[ClassDojo](https://www.classdojo.com/)|Schools/families; class communication and engagement.|Relevant family price not verified.|Source platform and potential internal organizer.|
|[Remind](https://help.remind.com/hc/en-us/articles/204430265-What-Remind-texts-look-like)|Schools/families; app/email/text announcements and messages.|[Core messaging described as free](https://help.remind.com/hc/en-us/articles/115000876244-Notify-your-community); institution tiers vary.|Relay could coordinate across channels, but access depends on source and permissions.|

Additional products mentioned during exploration: [TimeTree](https://timetreeapp.com/) as a shared-calendar alternative (no detailed verification or price); [Maple](https://maple.ai/pricing) search result was an unrelated general AI platform and should **not** be treated as the family-management Maple without further verification; Apple Calendar/Reminders and Google Calendar are obvious free substitutes; [Fambot](https://www.fastcompany.com/91599193/ai-wants-to-become-your-familys-chief-of-staff-should-you-let-it) was discussed in 2026 reporting, but features/pricing were not independently verified in this conversation. The 23-row map above is the actual researched comparison.

## 5. Market evidence, feedback and limits

### Verified or documented problem signals

- A [2026 SignUpGenius survey](https://www.signupgenius.com/resources/family-logistics-report) of **697 PreK–12 parents** reported use of shared family calendars (78.5%), payment apps (75.4%), school communication apps (73.3%) and signup/coordination tools (71.1%). It is a vendor survey, not a Relay-specific market-size or willingness-to-pay study.
- A [2025 school-app survey covered by GovTech](https://www.govtech.com/education/k-12/using-too-many-school-apps-may-burden-parents-teachers) involved more than 100 teachers, 125 parents and 50 administrators. It reported burden from multiple educational apps. The sample is modest and the research involved an education vendor.
- [Pew Research Center, 2026](https://www.pewresearch.org/social-trends/2026/06/16/how-working-parents-divide-family-responsibilities/) surveyed 2,242 U.S. working parents and found uneven division of many family responsibilities in different-sex couples. This supports the mental-load context, not automatic demand for software.
- [Census child-well-being publication](https://www2.census.gov/library/publications/2026/demo/p70-212.pdf) reported **72.4 million U.S. children under 18 in 2023**. This is population context only. Multiplying it by a proposed price would be a misleading TAM calculation.
- [GreatSchools parent insights survey](https://www.greatschools.org/gk/wp-content/uploads/2025/12/GreatSchools-Parent-Insights-Survey-Dec-2025-.pdf) linked parent satisfaction with school to their ability to access information and receive communications. It does not isolate Relay's use case.
- [Center for Democracy and Technology, 2025](https://cdt.org/insights/out-of-step-students-teachers-in-stride-with-edtech-threats-while-parents-are-left-behind/) surveyed parents, students and teachers about edtech and privacy. This is relevant to trust and child-data considerations, not product adoption.
- [The Atlantic, Nov. 2026](https://www.theatlantic.com/family/2026/11/school-apps-communication-broken/689312/) and [Star Tribune, Nov. 2026](https://www.startribune.com/parents-kids-school-apps/601905692) reported continuing parent frustration with many school apps. Journalism is qualitative evidence, not a frequency estimate.

### Actual customer reports and what they support

- [A Reddit family-calendar discussion](https://www.reddit.com/r/apps/comments/1s9ipcj/digital_family_calendar_that_actually_syncs/) included a complaint about yet another app requiring manual entry; a parent said flyers are left until entered or lost; another described difficulty allocating pickups around changing work schedules. Some replies were from app makers (including Sense and Plancove), so the thread is selected, not an unbiased sample. One commenter praised Ohai's photo/email capture, which undercuts any claim that competitors cannot do it.
- [FamilyWall App Store reviews](https://apps.apple.com/us/app/familywall-family-organizer/id496889629?see-all=reviews): one detailed reviewer requested snoozing a single recurring pickup, sharing timetables between circles instead of re-entering them, cross-circle double-booking alerts, and easier contact import. A separate reviewer noted location accuracy concerns. These are individual requests; no prevalence was established.
- [Cozi App Store reviews](https://apps.apple.com/us/app/cozi-family-organizer/id407108860?platform=iphone&see-all=reviews): many positive long-term usage reports; one specific reviewer liked multiple childcare providers and kids without email accounts, while reporting occasional event-time glitches and requesting event reuse/night-shift display. The page showed about 404K ratings and 4.8/5 at research time. Reviews cannot measure actual error rates.
- [FamilyWall/Skylight Reddit thread](https://www.reddit.com/r/ADHD/comments/1ota7tn/anyone_any_successful_experience_with_the/): a user described one-way updates in their combination of products. This does not prove all calendar sync fails.
- [Skylight subscription Reddit thread](https://www.reddit.com/r/skylightcalendar/comments/1pd882d/so_confused_about_the_subscriptions/): confusion about Plus/Calendar Plus and pricing. This supports transparent pricing as good product practice, not a defensible Relay capability.
- [Ohai Trustpilot](https://www.trustpilot.com/review/ohai.ai) had only **12 reviews** at research time, both positive and negative. No recurring complaint was responsibly inferred.
- [The Atlantic commentary, 2025](https://www.theatlantic.com/family/archive/2025/09/ai-parenting-app/684303/) raised the serious critique that AI can organize a list while parents still do the work, and perhaps encourage more activity. This is an editorial critique, not a survey.

### What remains unknown

No controlled comparison of competitor accuracy, retention, time saved, task completion or privacy behavior was performed. There is no Relay-specific willingness-to-pay study, reliable market-size estimate, acquisition cost, retention benchmark, investor interest, or proof that the proposed commitment workflow solves more than a calendar already does. Company claims about features are not proof of actual performance. All pricing is subject to date, region and plan changes.

## 6. Ten weaknesses of the original Relay idea

1. Core message/photo/email-to-calendar capture exists already.
2. Audience was too broad: teens, parents, caregivers and professionals have different jobs and payers.
3. “Connect everything” collides with permissions, unsupported platforms and privacy boundaries.
4. Google CC directly addresses family coordination and task changes.
5. A calendar event is not a fulfilled obligation.
6. Wrong or silently stale information may be worse than missing information.
7. Model access and generic extraction are easy for incumbents to replicate.
8. Family inputs include sensitive information about children and routines.
9. Competing subscriptions are cheap or free, creating another-app resistance.
10. A spectacular demo does not establish durable use or a company.

## 7. Ten opportunities to test, not confirmed gaps

1. Explicit commitment state: detected → reviewed → accepted → completed/unresolved.
2. Consequence-aware change handling: what people and plans a revision affects.
3. Handoffs among parents, co-parents, grandparents and caregivers with controlled visibility.
4. Acknowledgment distinct from assignment: “I saw it” versus “I will do it.”
5. Evidence of completion, such as a submission confirmation or receipt.
6. Visible uncertainty and source of each claim, instead of unqualified AI certainty.
7. Side-by-side handling of conflicting notices instead of silently choosing one.
8. One-time exceptions to repeating family routines.
9. Low-noise escalation of important unaccepted or unfinished commitments.
10. An audit trail of who changed a plan and why.

### Full 25-item differentiation analysis

“Existing” = similar documented capability; “partial” = pieces exist or may be easy to extend; “unclear” = not verified in research. Difficulty and willingness to pay are **judgment/hypothesis**, not measured evidence. No feature is a moat by itself. The earlier strategic top ten were **1, 3, 4, 5, 6, 9, 10, 13, 18 and 25**.

|#|Feature and problem solved / user value|Competitor status|Replication difficulty|Potential advantage and payment hypothesis|
|---:|---|---|---|---|
|1|**Commitment state:** track acceptance and completion, not merely a due date. Makes responsibility explicit.|Partial|Medium|Potentially meaningful if used; may support premium household value.|
|2|**Source-linked action:** show exact original instruction behind a task. Builds trust.|Existing partly in Kikko|Low|Trust feature; weak standalone moat and unlikely to raise price alone.|
|3|**Change impact map:** show every affected task/person after a changed event. Reduces stale plans.|Google CC claims changes kept current; depth unclear|Medium|Value depends on superior reliability; possible premium.|
|4|**Conflict evidence:** compare two contradictory notices and request a human decision. Avoids false certainty.|Unclear|Medium|Could distinguish if accurate; possible premium.|
|5|**Acceptance receipt:** record a caregiver's explicit commitment. Prevents assumed ownership.|Partial in task apps|Low–medium|Useful in shared care; likely core plan.|
|6|**Completion receipt:** preserve confirmation of a form, registration or payment. Shows outcome, not just intention.|Partial|Medium|Potentially meaningful workflow advantage; possible premium.|
|7|**Unresolved question queue:** ask for missing details before declaring a plan final.|Google CC says it asks for missing details|Low–medium|Reliability requirement, not unique.|
|8|**One-time routine exception:** change a single Tuesday without altering the series.|Partly supported by calendars|Low|Necessary polish; weak moat.|
|9|**Cross-circle conflict detection:** find overlap across households/caregiver groups.|Requested by a FamilyWall reviewer; actual competitor coverage unverified|Medium|Specific value for complex families; possible premium.|
|10|**Handoff view:** show the next caregiver what they need to do and know.|Partial|Medium|Strong niche fit if trusted; possible premium.|
|11|**Decision history:** record why a family picked an arrangement.|Unclear|Medium|Helpful during changes; unlikely to sell alone.|
|12|**Priority by consequence:** separate optional events from forms, pickups and payments.|Partial|Medium|Reduces noise; core value.|
|13|**Quiet escalation:** alert another authorized adult only when something important remains unaccepted.|Partial|Medium|Potential premium if it reduces nagging.|
|14|**Personal visibility rules:** show necessary event details without exposing unrelated email.|Google CC offers selective sharing|Medium|Trust requirement; privacy should not be an expensive add-on.|
|15|**School-term memory:** learn teachers, locations, supplies and household preferences with review.|Kikko and Google describe memory|Medium|Useful; feature-level copying is easy.|
|16|**Source freshness label:** show when a fact was last confirmed.|Unclear|Medium|Trust feature, likely core.|
|17|**Coverage disclosure:** tell users which sources Relay cannot see.|Unclear|Low–medium|Honest and brand-building; weak moat.|
|18|**Failure detection:** flag broken syncs or unread attachments rather than appearing up-to-date.|Unclear|Medium|Potential reliability advantage; should be core.|
|19|**Family workload view:** show who manages planning, follow-up and execution.|Partial in task apps|Medium|May address mental load; avoid judgmental scoring.|
|20|**Suggested reassignment:** propose a feasible handoff when schedules conflict.|Google demonstrated carpool conflict help|Low–medium|Quality matters; not unique.|
|21|**Multilingual instruction preservation:** translate while retaining original wording.|Translation common|Low|Reach and trust; weak moat alone.|
|22|**Student/parent paired view:** student responsibility with parent consent/oversight.|Partial|Medium|Potential niche; minor-data safeguards important.|
|23|**Outcome-based brief:** show only actions requiring attention.|Daily briefs exist|Low|Good design, weak defense.|
|24|**Portable commitment history:** export sources, decisions and completion records.|Some products export|Low|Trust and switching benefit; weak price lever.|
|25|**Measured reliability:** publish independently checked missed-obligation, wrong-date, false-task and corrected-change rates.|Comparable public benchmark not verified|Hard to establish credibly|Best potential long-term advantage if achieved and sustained; could support a trust brand.|

## 8. Ten Relay versions considered

|Version|Advantages|Disadvantages and competitors|Revenue / differentiation judgment|
|---|---|---|---|
|1. General AI family assistant|Broad, frequent use.|Google CC, Sense, Kikko, Ohai and others already pursue it.|Household subscription; **weak differentiation**.|
|2. **Family commitment system**|Targets acceptance, change and completion.|Could feel like home project management; Fambee, CC and task apps can add pieces.|Best conditional opportunity; household subscription.|
|3. School notice translator|Simple, obvious demo.|Kikko, Plancove, Cozi Max and others already do capture.|Low-price subscription; weak moat.|
|4. Co-parent handoff assistant|Important, specific coordination need.|Sensitive permissions, conflict; specialized co-parent tools and shared calendars.|Possibly higher household price; moderate differentiation.|
|5. Student assignment assistant|Daily use; reachable audience.|School LMS, Gemini, Todoist; minor-data concerns, weak direct payer.|Family/school buyer uncertain.|
|6. Family change detector|Changes make plans stale.|Google CC explicitly claims updates as things change.|Only valuable if measurably more reliable.|
|7. Autonomous household agent|Could truly complete forms/bookings.|Google has integrations/capital; consequential mistakes.|Higher price possible, poor initial feasibility.|
|8. Cross-platform personal inbox|Large audience.|Gemini, ChatGPT, Copilot; permissions and weak differentiation.|Consumer subscription, little initial defense.|
|9. Family caregiver coordinator|Serious recurring need.|Health privacy/liability and harder sales; care apps/portals.|Later vertical, family or organization plan.|
|10. Reliability layer for other family tools|Could verify commitments across calendars.|Integration burden; uncertain direct consumer purchase.|Possible later API/partner model.|

Five with most strategic merit: 2, 4, 6, 9, 10. Version 2 was recommended as the clearest first use and payer. No UI mockup or dashboard specification was produced. The only discussed experience was source capture → reviewed obligation → shared acceptance → change handling → completion evidence, with source links, uncertainty and privacy controls. No feature was formally committed for development.

## 9. Audience, pricing and investment analysis

|Audience|Pain/frequency|Payer and access|Alternatives / retention thesis|Conclusion|
|---|---|---|---|---|
|Parents coordinating school-age children across 2+ caregivers|High during school terms; pickups, forms and changes matter.|Parent household subscription plausible; online parent communities crowded.|Sense, Kikko, Cozi, Google CC; weekly retention only if commitments are actually closed.|**Provisional initial audience.**|
|Single-caregiver families|High information burden, fewer handoffs.|Price sensitivity varies.|Existing organizers; strong capture use, weaker shared-acceptance differentiation.|Adjacent.|
|Co-parenting across homes|High coordination pain, complex permissions.|Potential willingness to pay, unmeasured.|Specialized co-parent tools; trust and disputes hard.|Promising but sensitive.|
|Preschool families|Frequent forms/notices.|Household pricing plausible.|Parent apps and family suites.|Adjacent.|
|Teens/students|Daily deadlines, easy social reach.|Weak direct payer; guardian may pay.|LMS, Gemini, Todoist, homework products.|Not the first paying segment.|
|College students|Frequent deadlines.|Price-sensitive.|Notion, Todoist, Gemini, school LMS.|Crowded, weaker family distinction.|
|Busy professionals|Daily tasks and money.|Reachable online.|Motion, Reclaim, Copilot, Todoist, Gemini.|Avoid initially.|
|Elder-care families|Serious ongoing handoffs.|Possible family/organization payer.|Care apps, portals, general assistants.|Possible later vertical, high privacy/liability.|
|Small businesses|Many obligations, higher budgets.|Sales more demanding.|Work suites.|Different company strategy.|

**Pricing context, verified:** FamilyWall $44.99/year; Fambee $59.99/year; Cozi Max $79/year; Kikko €79.99/year; Plancove $39.99/year; Sense advertises $6.99/month. A Relay plan of **$6–$10/month per household** was suggested **as a test hypothesis**, with multiple caregivers included; charging per adult would obstruct the coordination mechanism. Higher pricing would require proven prevention of mistakes or real task completion. No financial projection, actual willingness-to-pay measurement, TAM or investor commitment was established.

**Possible investor positives:** sustained weekly family retention; multiple caregivers accepting/completing obligations; independently measured low missed/false/wrong-date rates; organic invitation growth; healthy margins after AI, messaging, support and security costs; a trusted workflow that becomes useful over time without locking in data. **Investor negatives:** a generic AI wrapper; abandonment after setup; unmeasured or poor accuracy; Google/free substitutes; high acquisition cost; privacy incidents; unsupported integration promises; misleading population-times-price market calculations. Potential expansion into co-parenting, elder care, household obligations or an API is speculative and contingent on winning the initial use.

**Brand thesis:** “Plans you can trust when life changes.” The strongest proposed demonstration is a practice moving from Tuesday to Thursday, with Relay showing the old and new source, a resulting pickup conflict, a caregiver accepting the handoff, and a confirmation of the changed plan. This is a *conceptual demonstration*, not a built product. A one-shot flyer-to-calendar video is already commodity. Social attention is not evidence of retention or investment.

## 10. Decision register

|Decision or judgment|Status|Why / what could change it|
|---|---|---|
|Pursue the Relay research line rather than the original 15 practical business ideas.|Founder choice, current.|The founder explicitly requested successive Relay investigations.|
|Relay should be a broad family AI assistant.|**Rejected as initial positioning.**|Direct competitors and Google CC already cover it. New evidence of superior distribution or unique use could reopen it.|
|Email/flyer-to-calendar is a differentiator.|**Rejected.**|Multiple competitors document it.|
|Relay should initially investigate multi-caregiver family commitments.|**Provisional recommendation, not founder-approved final spec.**|It focuses on an outcome existing calendars may not fully deliver. Must validate demand, actual competitor quality, trust and payment.|
|Measured reliability and trusted workflow could become a moat.|Unproven hypothesis.|Requires real comparative outcomes and sustained execution; incumbents can copy features.|
|The first buyer should be school-age families with 2+ caregivers.|Provisional.|Recurring handoff pain; price and reach still untested.|
|Price $6–$10/month per household.|Unproven test range.|Anchored to published competitor prices, not stated willingness to pay.|
|Build a broad autonomous agent immediately.|Not recommended.|Google is far ahead in integrations; consequential errors and sensitive data raise risk.|
|Begin a local prototype of the commitment workflow.|Founder-authorized 2026-11-21; implementation scope chosen by Codex.|The founder said to start the build stage and delegated the first version choice. This tests a hypothesis; it does not approve the narrowed direction as a final product specification.|

No unresolved disagreement with the founder was recorded; the founder did not confirm or reject the narrowed commitment direction after the research. Important open questions: What exact commitment failure occurs often enough to motivate a separate product? Can any incumbent already handle it well in practice? How would a family decide Relay is trustworthy? What minimum false-positive/missed-obligation rates are acceptable? Who pays? What data can Relay access legitimately and safely? Does the second caregiver participate or ignore another app? Can a founder-funded $0 product deliver sufficient reliability? Is “Relay” name available?

## 11. Source and link archive

Each link was encountered in this conversation's research unless explicitly labeled as an unverified mention. Links support the noted point, not broader performance claims.

### Direct family AI and organizing competitors

- Sense: [site](https://getsense.ai/), [help/features](https://getsense.ai/help/en), [pricing](https://getsense.ai/pricing), [App Store](https://apps.apple.com/us/app/sense-ai-family-calendar/id6739470108).
- Kikko: [site/features/pricing](https://kikko.ai/), [partner invitation help](https://kikko.ai/help/invite-your-partner), [App Store](https://apps.apple.com/us/app/kikko-ai-family-assistant/id6789952071?platform=ipad).
- FamilyGenie: [site/beta/feature claims](https://www.familygenie.ai/).
- Fambee: [site](https://www.getfambee.com/), [support/pricing/privacy claims](https://www.getfambee.com/support).
- Marlow: [site](https://meetmarlow.ai/), [proposed pricing](https://meetmarlow.ai/pricing).
- Milo: [family assistant](https://www.gomilo.app/). [miloai.app terms](https://miloai.app/terms-of-service) appeared in results and should not automatically be assumed to be the same company.
- Ohai: [site](https://www.getohai.com/index.html), [Trustpilot small review set](https://www.trustpilot.com/review/ohai.ai), [2024 launch reporting](https://www.axios.com/2024/01/22/ohai-ai-virtual-assistant-startup-sheila-lirio-marcelo-care).
- Plancove: [site](https://plancove.app/), [features, iPhone availability and price](https://plancove.app/about/).
- Cozi: [plans](https://www.cozi.com/compare-plans/), [feature overview](https://www.cozi.com/feature-overview/), [App Store reviews](https://apps.apple.com/us/app/cozi-family-organizer/id407108860?platform=iphone&see-all=reviews).
- FamilyWall: [site](https://www.familywall.com/), [pricing](https://www.prod.familywall.com/pricing.html), [App Store reviews](https://apps.apple.com/us/app/familywall-family-organizer/id496889629?see-all=reviews).
- Skylight: [subscription help](https://skylight.zendesk.com/hc/en-us/articles/51833126965019-Subscription), [Calendar Plus help](https://skylight.zendesk.com/hc/en-us/articles/32171114576283-What-is-Calendar-Plus), [subscription discussion](https://www.reddit.com/r/skylightcalendar/comments/1pd882d/so_confused_about_the_subscriptions/).
- Hearth: [membership and hardware page](https://hearthdisplay.com/products/2-year-membership).
- Google CC: [family/group announcement](https://blog.google/innovation-and-ai/models-and-research/google-labs/cc-expanding-to-groups/), [September AI update](https://blog.google/innovation-and-ai/technology/ai/google-ai-updates-september-2026/).

### General assistants, task/calendar tools and school channels

- Google Gemini: [Nov. 17, 2026 task execution announcement](https://blog.google/innovation-and-ai/products/gemini-app/tasks-in-gemini-free-new-features/), [shared calendar capabilities](https://support.google.com/gemini/thread/405845474/new-manage-your-secondary-and-shared-google-calendars-with-gemini?hl=en-AU), [plan overview](https://one.google.com/intl/en/about/google-ai-plans/?gl=US&hl=en).
- ChatGPT: [connected apps help](https://help.openai.com/en/articles/20001494-connecting-and-managing-app-accounts-in-chatgpt), [scheduled tasks](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt), [Plus price](https://help.openai.com/en/articles/6950777-what-is-chatgpt).
- Microsoft Copilot Outlook: [agentic email/calendar announcement](https://techcommunity.microsoft.com/blog/Outlook/copilot-in-outlook-new-agentic-experiences-for-email-and-calendar/4499798).
- Motion: [pricing/features](https://www.usemotion.com/pricing). Reclaim: [pricing/features](https://reclaim.ai/pricing). Todoist: [AI tools](https://www.todoist.com/ai-tools), [plan FAQ](https://www.todoist.com/es/help/account-and-billing/plans/todoist-plans-pricing-and-billing-faq-Vq2z0HWL6). Notion: [pricing](https://www.notion.com/pricing).
- School source platforms: [ParentSquare](https://www.parentsquare.com/), [ClassDojo](https://www.classdojo.com/), [Remind message help](https://help.remind.com/hc/en-us/articles/204430265-What-Remind-texts-look-like), [Remind free messaging help](https://help.remind.com/hc/en-us/articles/115000876244-Notify-your-community).
- Additional discovery, not fully profiled: [TimeTree](https://timetreeapp.com/); [Fambot reporting](https://www.fastcompany.com/91599193/ai-wants-to-become-your-familys-chief-of-staff-should-you-let-it).

### Market studies, reporting and customer experiences

- [SignUpGenius Family Logistics Report 2026](https://www.signupgenius.com/resources/family-logistics-report); [Pew working parents 2026](https://www.pewresearch.org/social-trends/2026/06/16/how-working-parents-divide-family-responsibilities/); [Census child well-being publication](https://www2.census.gov/library/publications/2026/demo/p70-212.pdf); [GreatSchools parent insights survey](https://www.greatschools.org/gk/wp-content/uploads/2025/12/GreatSchools-Parent-Insights-Survey-Dec-2025-.pdf); [CDT parent/student/teacher edtech survey](https://cdt.org/insights/out-of-step-students-teachers-in-stride-with-edtech-threats-while-parents-are-left-behind/).
- [School app survey coverage, GovTech](https://www.govtech.com/education/k-12/using-too-many-school-apps-may-burden-parents-teachers); [Star Tribune 2026 school-app reporting](https://www.startribune.com/parents-kids-school-apps/601905692); [Atlantic 2026 school-app reporting](https://www.theatlantic.com/family/2026/11/school-apps-communication-broken/689312/); [Atlantic 2025 family-AI critique](https://www.theatlantic.com/family/archive/2025/09/ai-parenting-app/684303/).
- [Reddit family-calendar and manual-input discussion](https://www.reddit.com/r/apps/comments/1s9ipcj/digital_family_calendar_that_actually_syncs/); [Reddit FamilyWall/Skylight one-way-sync report](https://www.reddit.com/r/ADHD/comments/1ota7tn/anyone_any_successful_experience_with_the/); [Reddit Skylight subscription confusion](https://www.reddit.com/r/skylightcalendar/comments/1pd882d/so_confused_about_the_subscriptions/); [Cozi App Store reviews](https://apps.apple.com/us/app/cozi-family-organizer/id407108860?platform=iphone&see-all=reviews); [FamilyWall App Store reviews](https://apps.apple.com/us/app/familywall-family-organizer/id496889629?see-all=reviews); [Ohai Trustpilot reviews](https://www.trustpilot.com/review/ohai.ai).
- A related but distinct later-expansion source: [family caregiver coordination study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12631485/).

### Earlier broad startup-discovery sources, not Relay validation

These informed the original 30-idea landscape, and should not be repurposed as evidence for Relay: [FTC fraud losses](https://www.ftc.gov/news-events/news/press-releases/2025/03/new-ftc-data-show-big-jump-reported-losses-fraud-125-billion-2024), [WebAIM Million 2025](https://webaim.org/projects/million/2025), [UNEP Food Waste Index](https://www.unep.org/en/news-and-stories/press-release/world-squanders-over-1-billion-meals-day-un-report), [repair-barriers research](https://journals.aau.dk/index.php/plate2025/article/view/10426), [U.S. Chamber small-business compliance](https://www.uschamber.com/small-business/small-businesses-are-spending-more-time-money-on-regulatory-compliance), [Urban Institute nonprofit challenges](https://www.urban.org/research/publication/nonprofit-leaders-concerns-about-finances-programming-and-workforce-challenges). The initial 15-idea answer also cited [Carleton grant-reporting research](https://carleton.ca/cicp-pcpob/2025/the-burden-of-reporting/), [Harbor Compliance](https://www.harborcompliance.com/business-licensing-service), [Instrumentl](https://help.instrumentl.com/en/articles/3730779-export-your-data-with-reports) and [WAVE](https://wave.webaim.org/about).

## 12. Exact current status and continuation instructions

**Completed research:** broad 15-idea exercise; broader 30-idea scored exercise; Relay selected for deeper investigation; a 23-product competitor map; published pricing comparisons; anecdotal feedback review; 25 proposed differentiators; 10 Relay versions; preliminary target, brand and investor analysis; correction of the original market-gap claim after Google and direct competitor research.

**Completed build milestone (2026-11-21):** A local prototype was created with a commitment list/detail view, manually entered source notice, task, due date, caregiver, acceptance state, completion note, revision history, and browser-local persistence. `src/commitments.mjs` holds state transitions; `src/app.mjs` renders and operates the browser interface; `tests/commitments.test.mjs` checks core state behavior. `README.md` gives run instructions and `DESIGN.md` records the initial visual direction. This is a single-browser demonstration, not real caregiver collaboration. The exact verification status for this milestone should be read from the latest session record; future agents should re-run tests and browser checks rather than assume they passed.

**Frontend refinement milestone (2026-11-21):** The founder requested a significant design and UX improvement. The work kept the existing vanilla HTML/CSS/JavaScript architecture and the commitment-state model. `index.html` now presents a compact family plan, a clear acceptance-attention summary, a filterable commitment list, a responsive detail view, and accessible create/completion dialogs. `styles.css` now implements the refined blue/teal design system, responsive list/detail behavior, visible focus states, reduced-motion support, and consistent controls. `src/app.mjs` now renders status counts, an honest source → acceptance → completion progress thread, an explicit next step, change history, mobile back navigation, form-field errors, and persistent browser-storage failure feedback. `src/presentation.mjs` is a small reusable presentation unit for sorting, counts, and due-date wording; `tests/presentation.test.mjs` verifies it. `DESIGN.md` records the revised design decisions and maps normative values to CSS variables; `README.md` was updated.

**Design rationale:** The original large hero pushed the actual plan down; the revised screen puts pending family decisions first. A divided list and selected detail retain the existing source/owner/history model while making it easier to scan. Mobile uses a list-to-detail transition because stacking the detail below a long list hid the result of selection. The progress thread uses distinct states so a named caregiver is not mistaken for one who accepted, and the interface repeatedly states that notes are manual and local. No React migration, external dependencies, or decorative AI-chat layout were introduced because the current product has one small working flow and no existing component framework.

**Verification recorded for this refinement:** `node --check` passed on application modules; the full `node --test tests/*.test.mjs` suite passed 8/8; the frontend premium static audit reported zero findings. A local Microsoft Edge browser walkthrough exercised create → acceptance → completion → revision, empty and filtered states, validation focus and `aria-invalid`, modal Escape/focus restoration, keyboard filter operation, phone back navigation/focus, reduced-motion CSS, and viewport widths 320, 390, 800, 801, 1024, and 1440 pixels without horizontal overflow or page errors. Screenshots are in `output/playwright/`. The official `designmd` linter could not run offline because its package was not cached; the Codex computer-use browser host was unavailable, so the local browser runtime was used instead. Re-run these checks after future changes.

**Outstanding design and product issues:** No real caregiver identity or shared acceptance exists, so “yes” is only a local manual note. There is no edit-title or remove flow, no cross-device sync or backup, no full privacy model for family data, and no AI extraction. No usability study with actual families has tested whether this workflow saves work or whether the terminology is natural. There is no asynchronous loading state because the prototype has no network operations. Before a public release, add a proper data/permission architecture, production error and conflict handling, accessibility testing with assistive technology, and user research on the core commitment loop. The official design-context lint remains to be run when its package is available.

**Not completed:** no incorporated company, trademark check, domain selection, customer interviews, survey of Relay prospects, hands-on competitor benchmark, full technical feasibility analysis, validated product specification, integrations, privacy architecture, launched public website, payments, paid customers, measured retention, or verified advantage. No financial forecast or reliable Relay TAM exists. The narrowed strategy is a **recommendation**, not a final founder decision. The current prototype lacks AI extraction, accounts, multi-device sync, real caregiver acceptance, notifications, calendar connections, and production data protection.

**How the next AI should work:** act as the founder's critical co-founder, product strategist, AI technology advisor, market researcher, branding strategist and business advisor. Build on this research rather than repeating it. Recheck current competitor facts and pricing when they matter, because the market changed during this research. Separate verified facts, user anecdotes, inference and speculation. Challenge weak assumptions, especially that an unlisted feature is absent or that a demo predicts willingness to pay. Explore ambitious directions, but use the prototype to learn before treating it as the foundation of a full product. Respect the founder's age and $0 start without shrinking the long-term ambition. Do not invent demand, market size, financial projections or defensibility.

### Suggested skills for the next agent

- `superpowers:using-superpowers` for routing a new task to applicable skills.
- `engineering-suite-grill-me:idea-refine` for refining or stress-testing Relay's direction.
- `engineering-suite-grill-me:interview-me` if the founder wants an interactive one-question-at-a-time discovery process.
- `engineering-suite-grill-me:domain-modeling` if defining the product's core terms or creating a CONTEXT.md.
- `superpowers:brainstorming` for genuinely new product behavior or strategy concepts.

## THE MOST IMPORTANT THING THE NEXT AI MUST UNDERSTAND

Relay's ambition is a recognizable, substantial AI company that helps people reliably handle everyday responsibilities. The **original broad family-assistant concept is already crowded**: several startups ingest family messages, and Google CC/Gemini cover much of the proposed vision. The current **provisional** direction is a trusted family-commitment system that helps households **understand, coordinate and follow through** when plans change—showing the source, the responsible person and the outcome. That direction has **not yet been validated**. The next job is to determine whether it solves a painful, recurring problem better than existing tools and is worth paying for, while staying brutally honest about privacy, accuracy and Google's advantages.

## 13. Relay V1 build milestone (2026-11-21)

The founder authorized a foundational V1 build based on the later product reassessment. The implemented product direction is an **AI family coordination assistant** for adults in school-age households who share logistics. V1 focuses on fragmented messages becoming a reviewed, traceable family plan. This remains an implementation hypothesis. The founder has not validated demand, retention, willingness to pay, or a durable advantage over Google and direct family-assistant competitors.

### Verified implementation

- `server.py` is a loopback-only Python HTTP service backed by SQLite. It creates a separate synthetic household for each browser session using an HttpOnly, SameSite=Strict cookie whose token is hashed in storage. The server restricts host and origin, accepts only JSON mutations, validates size and field values, retains sources and plan versions transactionally, serves only approved runtime assets, and avoids default request logging of household content. It is a local evaluation server and requires a production server, TLS, identity system, authorization model, rate limits, monitoring, backups, and security review before any networked family pilot.
- The V1 flow is paste source text → inspect a suggestion → approve or reject → see the current plan and source history. A pending source can update a selected plan after a compare-and-swap check on the latest source version. Rejection never alters a plan. Export and local deletion are available from Household.
- Intake performs a deliberately limited deterministic extraction of explicit labelled fields: `Date: YYYY-MM-DD`, `Time: HH:MM`, and `For: Alex` or `For: Sam`. It abstains from conversational dates, ambiguous formats, OCR, file interpretation, email access, and AI inference. The review screen clearly requires a human to check or fill everything else.
- `src/intelligence.mjs` provides model-independent read-only briefing and lookup projections. It identifies current plans, pending sources, missing fields, exact date/time/person conflicts, revisions, and exact duplicate wording. Its bounded question grammar supports today, tomorrow, changes, conflicts, pending review, and a person listed on a matching plan title. Every answer returns plan and source references. It declares `interpretSource` unavailable with no provider, key, transport, model, or tool access.
- `index.html`, `styles.css`, `src/app.mjs`, and `src/neighbourhood.mjs` provide the responsive V1 experience. The interface has Briefing, Family plan, Inbox, Ask Relay, source review, plan history, export, and deletion flows. The briefing uses a custom procedural neighborhood illustration rather than an external image. Desktop and 320px views were visually inspected.
- `docs/v1-product.md`, `docs/technical-architecture.md`, `docs/technology-decisions.md`, `docs/relay-intelligence-architecture.md`, and `DESIGN.md` document product scope, runtime architecture, local technology decisions, trust boundaries, intelligence roadmap, and design rules. `README.md` documents running and testing.

### Verification recorded for V1

- `node --test tests/*.test.mjs` passed 27 tests for historical commitment behavior, presentation helpers, deterministic intelligence projections, question grammar, conflicts, history, duplicate checks, abstention, and unavailable-model boundaries.
- `python -m unittest discover -s tests -v` passed 4 loopback integration tests for intake, review, immutable history, export, restart persistence, deletion, household isolation, request validation, stale-write protection, and concurrent approvals.
- `node --check` passed for browser modules. `python -m py_compile server.py` passed. Strict TypeScript checking of `src/intelligence.mjs` and `src/household.d.ts` passed using the locally installed compiler. `tools/package_local.py` created and integrity-checked `output/relay-local.zip`.
- A Microsoft Edge browser walkthrough on `127.0.0.1` verified intake → review → approval → family plan → grounded question lookup, explicit deterministic prefill of `Date: 2026-12-04`, `Time: 16:15`, `For: Sam`, 320px layout without horizontal overflow, and no browser errors. Captures are `output/playwright/v1-final-desktop.png` and `output/playwright/v1-final-mobile.png`.

### Known limitations and continuation

- The application has no live AI capability, provider configuration, external connection, email ingestion, document upload, OCR, model evaluation against real consented data, real authentication, family invitation, multi-device synchronization, production authorization, or remote deployment. The V1 data is synthetic.
- The current `person` field means the person affected or scheduled. It does not mean a caregiver accepted ownership. Any future responsibility, approval, completion, and external-action model needs distinct fields, permissions, evidence, and audit states.
- Exact-time collision detection does not consider duration, travel, care availability, time zones, recurring plans, or calendar integration. The source duplicate check only detects identical normalized wording.
- Run locally with `python server.py --port 4173`; read the V1 product and intelligence documents before extending the code. Future work should begin with prospective-family research and a competitor workflow benchmark before expanding integrations or authorizing model inference.

### Post-build local-runtime verification (2026-11-21)

The reported “Briefing unavailable” screen was reproduced and traced to several stale test instances of `server.py` competing on port 4173; the browser was reaching an older process rather than the current V1 process. After stopping those instances and starting one fresh `python server.py --port 4173` process, `GET /api/state` returned 200 and initialized the sample household. The README now explicitly distinguishes the required local server from a static-file preview and gives the recovery step.

The final regression run passed: 27 Node tests, 4 Python HTTP/SQLite integration tests, module syntax checks, Python compilation, and local package creation. A fresh Edge walkthrough loaded the briefing, pasted labelled source data, checked deterministic prefill (`2026-12-04`, `16:15`, `Sam`), approved it into the plan, found no browser errors, and confirmed no horizontal overflow at 390px. Fresh captures are `output/playwright/v1-final-verified.png` and `output/playwright/v1-final-mobile-verified.png`.

## 14. Product-depth and visual-system reconstruction (2026-11-21)

The prior illustrated/editorial V1 surface was replaced after a complete screen audit. The new design system is a high-density household signal ledger: fog-grey stock, black ruling, restrained vermilion signals, an operational typography hierarchy, a decision band, and paired ledger rails rather than cards and decorative illustration. `PRODUCT.md` now records the durable product context; `DESIGN.md` records the replacement visual world and its responsive/interaction rules. Baseline and post-redesign captures are stored in `output/playwright/audit-before-*.png` and `output/playwright/redesign-final-*.png`.

Meaningful V1 depth added: `tasks` is now a SQLite-backed, household-scoped follow-through model. `POST /api/tasks` validates creation and open/done toggles, enforces household/plan boundaries, persists through export and restart, and is cleared transactionally with the household. Tasks appear in the briefing and each plan's detail flow where a user can add, assign, and complete a practical action. `src/intelligence.mjs` now produces separate open/completed task projections. The coverage added a red/green Python integration test for task creation, tenancy, validation, export, and toggling plus a JavaScript briefing projection test.

Verification for this milestone: Impeccable detector returned zero findings on `styles.css`, `src/app.mjs`, and `index.html`; 28 Node tests and 5 Python HTTP/SQLite integration tests passed; `python -m py_compile server.py` passed. Final Edge browser capture covered Briefing, Family plan, Inbox, Ask Relay, task creation/completion in one persistent session, desktop screenshots, a 390px responsive screenshot without horizontal overflow, and no browser errors.

## 15. V2 delivery-hardening milestone (2026-11-21)

V2 remains a **local, single-operator evaluation application**, not an internet-ready family service. The current supported authorization model is a loopback-only, HttpOnly/SameSite session cookie with server-side hashed tokens and household-scoped queries. There is no user account, invitation, external identity provider, cross-device sharing, or cloud deployment. Those are documented deployment prerequisites, not implemented claims.

The server now has an ordered, idempotent SQLite migration ledger (`schema_migrations`) and `GET /api/health`, covered by a regression test. The repository now includes `.gitignore` rules for SQLite data, journals, artifacts, keys, environment files, caches, and editor files; `UX-CONTRACT.md` records the canonical form/dialog/toast/CRUD behavior; `docs/deployment.md` states why GitHub Pages is unsuitable and lists required network-deployment controls. `README.md`, technical architecture, and intelligence architecture were updated to V2 reality.

Git was initialized locally and the complete V2 milestone was committed as `a883a03cfdabd94b6ed7c5bae8fbffb4a28c871e` (`Build Relay V2 local coordination workflow`). On 2026-11-21, the founder authorized a private GitHub upload. The private repository [`HubGitCoder3141/relay-v2`](https://github.com/HubGitCoder3141/relay-v2) was created with no generated README, license, or server-side `.gitignore`; local `origin` tracks its `main` branch. `git push -u origin main` and `git ls-remote --heads origin main` both verified that exact commit on the remote. The GitHub CLI remains unavailable, but the browser-authenticated GitHub account was used for this one upload. Do not make the repository public without founder approval.

## 16. V3 development milestone (2026-11-21)

The latest directive reiterates Relay's broader family coordination vision and authorizes an iterative transformation under the original zero-budget and no-model constraints. The implementation keeps the dependency-free Python/SQLite and native browser runtime. The new default workspace starts empty and fictional data is opt-in with `--demo`. V3 changes are in the local working tree.

- Migrations 2 and 3 add versioned preparation and instructions, persistent extraction evidence, and a household roster. New migrations and ledger updates are atomic. Existing records retain prior values, versions, and the available names.
- `relay_intake.py` handles explicit labels and records source line evidence. It leaves competing or invalid values unresolved. The reviewed values, source text, and captured evidence remain separate. A revision requires the latest source ID and is validated in a write transaction.
- The UI brings back mobile navigation, restores status feedback, and pairs source evidence and approval on desktop, with a compact evidence disclosure on phones. Roster, review, plan details/history, and data export/reset are wired to the same scoped store. Weekly schedule and preparation lookups use current approved records with citations.
- Verified 30 Node tests, 10 loopback HTTP tests, JS syntax checks, Python compilation, ZIP packaging, a strict frontend audit with no findings, and an Edge journey from an empty workspace through roster, intake, validation, approval, lookup, reload, and follow-through. Captures are in `output/playwright/v3-*.png`. No full screen-reader or performance benchmark was conducted.
- Use `python server.py --port 4173` and open `http://127.0.0.1:4173`. `PROJECT_CONTEXT.md` and `docs/v3-delivery.md` capture active scope, audit, and milestones. There is no networked identity or sharing, live model inference, file/OCR or email integration. Next priorities are stale review recovery, richer coordination context and permissions, and evaluation of interpretation reliability.

## 17. V3 household access, reconciliation and design continuation (2026-11-21)

- Migration 4 preserves existing owners' browser cookies, creates role-bearing access grants and stores invitation hashes. Local owners manage roles, membership removal, export and reset. Administrators manage invites and the plan roster. Adult members can read household content and participate in intake, review and follow-through. A one-time 24-hour code joins an adult browser to a household. Role and access checks run inside the server transaction on every request. This is a loopback proof of adult collaboration, with one household per browser session. Verified identities, cross-device login, recovery, and per-record permissions are open.
- On a stale approval, the form keeps the active draft and reads the new authorized snapshot. Reviewers compare the previous, newly confirmed and draft values, can read the new approved source, apply choices and resubmit against the newer version. The UI carries forward unedited, omitted fields when targeting an existing plan. The database retains source-backed revision history and blocks each stale write. Drafts are held on the open page.
- The visual redesign uses a shared seven-day board, a real date filter with day counts, a yellow today marker, evergreen typography, a loop wordmark and consistent source, history and access treatments. Desktop, tablet and mobile Edge captures are in `output/playwright/v3-*.png`. The source review keeps its title and close action in view during comparison.
- Verified 30 Node tests and 14 HTTP tests, including cross-household isolation, one-time invite races, expiry and revocation, role restrictions and competing approvals. Edge verified the local two-browser flow and 320px overflow, accessible navigation names and keyboard date filtering with preserved focus. A 25-request loopback sample with 123 synthetic sources returned about 199 KB per snapshot, with a 6.0 ms p95 in the recorded run. This is a local baseline. No full assistive-technology walkthrough or production load test was performed. TypeScript was unavailable offline.
- `docs/saas-readiness.md` assesses identity, data isolation, files and email, jobs, deployment, sync, operations, recovery and billing. Stripe and Paddle were researched from first-party documentation. No service, provider, or hosted environment was activated. Build remains local and unpushed. Next priorities are protected draft recovery across reload, reviewer attribution, adult identity and account recovery, and tenant-aware pilot deployment prerequisites.

## 18. Modern Family Home redesign (2026-11-21)

The founder supplied two family app visual references and asked for an original identity grounded in Relay's workflows. `DESIGN.md` records the Home, Journal and Command Center alternatives and the chosen blend. The design uses editorial typography, ivory paper, forest and clay arrival panels, a butter date marker, sage evidence, and plum lookup. Names from the actual plan roster supply consistent initials. Selecting a person opens their filtered timeline. The briefing surfaces approved preparation for the visible forward week, and the plan groups dated and undated events without repeating date badges in each row.

The change is local and frontend-only. Browser checks verified the new person filter, date filtering, source intake and approval, revision recovery, household access, lookup, persistence, and follow-through. Synthetic captures cover desktop, tablet and phone in `output/playwright/v3-*.png`. The Node suite passed 30 tests, the portable package rebuilt, and the strict frontend audit found no issues. The Impeccable detector flagged the explicitly requested warm cream palette.

## 19. Intake reliability and responsive motion (2026-11-21)

The previous parser was limited to exact labels and ISO values. Migration 5 now carries location, responsible person, and deadline from intake through review and plan history. The parser accepts common event, email subject, venue, assignment and deadline labels, combined When lines with explicit year, 12- and 24-hour time, and full Please bring lines. It preserves original wording and line evidence, and leaves relative, ambiguous, unrecognized or contradictory values for a reviewer. The intake API returns `createdSourceId` for the request's exact suggestion. Duplicate warnings and transactional revision checks still apply. There is no model inference.

Motion is tied to route entry, directional week changes, filtered results, unfolding a competing revision and confirmed actions. Reduced-motion users receive the same immediate state and confirmation cues. Verification includes 16 HTTP tests and 30 JS tests, Python and JS syntax checks, ZIP packaging, and Edge on desktop, tablet and phone. The browser walkthrough checks approval, persistence of new fields through a competing revision, keyboard date filtering, and reduced motion. Current screenshots are in `output/playwright/v3-*.png`. Restart the local server to load migration 5.

## 20. V3 publication and hosted deployment status (2026-11-21)

The founder authorized pushing V3 to the existing private GitHub repository and requested Vercel hosting with Supabase. The V3 application commit `5c551f7f6f1c8261b5853f163ee4a6d445cf5dc0` was pushed and verified on `origin/main`. A fresh verification passed 30 JavaScript tests and 16 local HTTP integration tests. The local SQLite household database, generated artifacts and environment files were excluded.

Vercel team access was initially denied and then became available. The empty `relay-v3` Vercel project was created under `robotadvance2102-6779s-projects` (project ID `prj_kqcYTts5tfvJB1J3TrFPi1lRHASS`). The team had no existing Supabase integration and no Supabase project was accessible from this session. Git is not linked to the Vercel project. No hosted release, database provisioning, household-data migration, or billing setup occurred. Next steps are to connect an empty free-tier Supabase project, implement the serverless/Postgres runtime with private database access, preserve the local authorization and revision guarantees, and verify an isolated preview using synthetic data before sharing a hosted URL.

## 21. Verified hosted preview (2026-11-21)

The founder connected the Supabase Free Plan resource `supabase-yellow-engine` to Vercel Preview. Relay now has a protected [Vercel preview](https://relay-v3-f8uhi61h3-robotadvance2102-6779s-projects.vercel.app/) using Postgres schema version 5, verified by hosted health and a browser walkthrough that pasted, extracted, approved, reloaded and reopened a synthetic plan. Local SQLite remains a separate store. The connected Postgres resource uses an unexposed schema. Secrets remain in Vercel environment variables.

Vercel labeled the first API upload Production. The runtime rejects Production and the database is scoped to Preview. The first schema apply reached the earlier empty Supabase project rather than the Marketplace resource, so that earlier project also contains an unused, empty private schema. The final preview pins the actual Marketplace resource and initializes only its isolated schema. No local family data was migrated.

The deployed preview used an explicit file upload. The GitHub repository is still private and Vercel is not configured for automatic Git deployment. For a public production release, independent Production database configuration, production identity and authorization review, and deployment validation remain outstanding. Local verification passed 16 HTTP and 30 JavaScript tests after adding the hosted adapter.

## 22. Public release preparation and preview cleanup

The founder requested a public production release with Relay sign-in and a separate database, and asked to remove the synthetic hosting check. A protected preview maintenance deployment removed two exact fixtures from the preview Postgres database. A repeated check removed zero additional rows. The deletion matched complete original text and expected plan fields and excluded plans with tasks, later sources, or other versions.

Production uses the separate Supabase project `relay` (`tryyihbuzexsgvrfeuwn`) with the private `relay_production` schema and account identity bindings. The schema migration succeeded. The Production-only Supabase publishable key is configured in Vercel. The code adds email OTP sign-in with a Secure HttpOnly account cookie and server-side identity verification before household access. Preview continues to use its separate provider resource and existing protection.

Vercel now has a sensitive `POSTGRES_URL` scoped to Production, using the production Supabase transaction pooler and a dedicated `relay_production_runtime` login. The role has operation-specific grants on Relay tables and separate row-level security policies. Supabase catalog checks confirmed schema version 5, nine policies for the runtime role, and no private schema access for the anonymous and authenticated Data API roles. Vercel still lists a separate Preview credential. The pooled connection still needs verification from a deployment.

The production Supabase dashboard requires a custom SMTP sender before it will allow edits to Auth email templates. No sender is configured. Configure SMTP for external delivery, then include `{{ .Token }}` in the confirmation and magic link email templates. `RELAY_PRODUCTION_ENABLED` remains absent. Stage a protected Production candidate, check the pooled connection, verify sign-in with an external account and household isolation, then release. Previous local verification passed 18 Python checks and 30 JavaScript tests. Live production sign-in and delivery remain unverified.

## 23. Private family production release (2026-11-22)

The founder requested a family-only site without Gmail or Vercel accounts. [Relay Production](https://relay-v3-six.vercel.app/) now serves deployment `dpl_9MwNRr1ctejyqvRPDFuFFCoJ5E7S` from an explicit Vercel source upload. `RELAY_PRODUCTION_ENABLED=1` and `RELAY_ACCESS_MODE=family` select the invitation-only mode. The owner credential is stored as a Vercel Production secret and in a Git-ignored local `.relay/family-owner.key` for the founder. No SMTP was needed. The previous section describes the optional email path and the state before this release.

`api/relay.py` gates production requests to the one pinned family workspace, requires an owner key or single-use invitation, and issues separate Secure HttpOnly browser cookies. `src/app.mjs` presents the private code form. The owner creates and revokes member access from Household access. Member re-entry requires a new invite after signing out or clearing browser storage. No preview data was moved to Production. Changes were deployed directly and remain in the local working tree.

Verification passed 19 Python tests and 30 JavaScript tests. Anonymous HTTPS checks reached the production sign-in page without Vercel authentication and received 401 from state and export. Hosted health reached the separate Supabase database. Live checks verified owner sign-in and reload, invite creation and redemption in a second session, replay rejection, member export denial, revocation and sign-out. The temporary verification member was revoked and removed. The next step is for the founder to sign in with the owner key and create a private invite per family member's browser.

## 24. Family release hardening (2026-11-23)

Code commit `5f5eb2dc7e1689cb8c54d2a40755ab835480528a` was pushed to the private GitHub `origin/main`. The source was uploaded to the protected Vercel Preview (`dpl_6sYxHhCySvKkVdSC2CtPCLHYpL53`) and Production (`dpl_BjiM2bjEUgAVVTsysHRJvV2MM54t`). Production serves the existing family URL. Preview and Production retain separate Postgres resources. Vercel deploys are still explicit source uploads.

The owner can copy a private, single-use invitation link in Household access. The browser removes the link fragment, prefills the code, and asks the recipient to confirm before redeeming it. Hosted Household settings now identify the shared workspace. Owner sessions have random per-browser credentials that expire after 30 days. Sign-out revokes its server-side session. The previous owner cookie requires one sign-in with the existing key. Existing member cookies remain valid until sign-out or revocation. Family state and export use read-only repeatable-read Postgres snapshots without the global write lock.

The production Supabase migrations add the private `family_owner_sessions` table and remove API-role execution privileges from the RLS event-trigger function. Verified table RLS, runtime privileges, anonymous schema denial, and removal of both advisor warnings. The remaining advisor entries are informational and relate to the unused old preview schema inside the production project. The Vercel error/fatal log query returned no groups after the smoke test.

Verification passed 19 Python and 30 JavaScript tests. Preview health returned 200 on its pinned database. Live production tests verified health, anonymous access denial, wrong-code rejection, independent owner sessions, invite redemption and replay denial, member export denial, owner export, and server-side sign-out for both roles. The temporary membership was removed. No managed backup restore drill, long-running load test, or broader public launch was performed. Keep the service family-only while those operational requirements remain open.

## 25. Family Actions and multi-family onboarding

The founder requested more useful daily features and access for households beyond their own. Actions adds a dedicated view with overdue, today, upcoming, undated, and completed groups. Household members can create standalone or plan-linked actions, set dates and assignees, edit, complete, reopen, and delete them. The briefing prioritizes the earliest action deadlines. Completion sends the desired state so a retried request cannot flip it back. Migration 6 adds an optional due date while preserving existing actions.

The separate `accounts` runtime mode now requires a verified Supabase identity and makes household creation explicit. A newly signed-in adult can either create their own household or redeem an invitation. Tests model two independent owner identities and a third invited member, including idempotent creation and identity-to-household bindings. The live site still runs in `family` mode. Public registration requires a configured external sign-in provider, a protected multi-family rollout target, verified delivery/sign-in, and the remaining operational checks in Section 24. No household data was migrated between environments.

Protected Preview deploy `dpl_AgaaxHxEKNqMN1RYmhj2ssMFD2Yx` and family Production deploy `dpl_Hui5rj35DuzwD87tKrXgvn2wtN5P` returned Postgres health at schema version 6. Production also passed live checks of the Actions route, account gate, family sign-in, state read and sign-out without adding household records. Production Supabase confirmed the due-date column and task RLS. The Marketplace preview was not writable through the Supabase connector, so its pinned protected health endpoint performed the additive upgrade. Local verification passed 21 Python tests, 31 JavaScript tests, a strict UI audit, and an Edge desktop/mobile walkthrough of the new action flow. Captures are `output/playwright/v3-actions-390.png`, `v3-actions-820.png`, and `v3-actions-1440.png`.

## 26. Notice interpretation and Ask Relay

The founder reported poor suggested plans and Ask Relay answers. The notice interpreter now handles common event sentences, roster names in activities, explicit start ranges, multi-line preparation, response deadlines, and quoted mail or sender headers. The source date is an optional user input for relative dates. Inferred dates retain both the message date and the source wording in the existing extraction evidence. Conflicting options or multiple activities and canceled schedules remain in review. Earlier stored suggestions are kept as originally generated.

Ask Relay now refreshes current household data before answering and supports named-person schedules, calendar windows, plan details, due and overdue actions, combined attention, and a follow-up about a single referenced plan. It links answers to recorded sources, plans, and actions. Ambiguous plan names prompt the user to narrow the request. Questions are processed locally in the browser and intake runs on Relay's server with deterministic rules. No model provider was added.

Verified 25 Python tests, 34 JavaScript tests, and a synthetic Edge walkthrough covering the original approval path, natural-message review, fresh answers, follow-ups, and action links. A comparison on six synthetic notices recovered 3 of 26 expected values before the change and 26 after. This fixture comparison does not establish real-world accuracy. Vercel Preview `dpl_3RFHxjTsDdvsaZrPFKNWN2bSmZ24` passed health. Production `dpl_AxwWa9txEznFvhDByMhBNzy9uuzf` served the new assets, returned schema version 6, and rejected anonymous reads and exports. No database migration was needed. Captures include `output/playwright/v3-plain-notice-review.png` and `output/playwright/v3-ask-mobile.png`.

## 27. Trainable notice understanding

Implemented a shared bidirectional GRU with nine contextual span heads and classifiers for plan type and notice intent. PyTorch training uses labeled synthetic examples plus optional JSONL inputs. The bundled NPZ is 225,131 bytes and runs on NumPy in Relay's existing `/api/intake` endpoint. It contains no real household data. The server combines learned role spans with exact source evidence, date and roster validation, confidence thresholds, explicit no-plan guards, and the existing approval step. The model has no external provider, write access, or approval action. Ask Relay's lookup behavior is separate.

Final artifact used 5,642 training examples, nine calibration examples, and ten synthetic evaluation examples. Raw exact-span precision 0.697, recall 0.742, F1 0.719, and warm CPU inference p95 approximately 1.8 ms. The corpus is a development check, not a realistic accuracy estimate. Verified 33 Python tests, 34 JavaScript tests, PyTorch/NumPy export parity, the package build, and an Edge test importing the founder's soccer example. Protected Preview `dpl_FZUfwynT9KjjfmBqsFdmPYLsgVBk` returned schema version 6 and `noticeModelAvailable: true`. Production remains on its earlier family deployment. There was no schema migration or transfer of family data.

Next steps are a larger household-held-out evaluation, better calibration and measurement for rare roles and ambiguous dates, and a comparison against a compact pretrained encoder. See `docs/notice-nlu.md` for training, evaluation, deployment, and fallback. Browser evidence is `output/playwright/v3-learned-notice-review.png`.
