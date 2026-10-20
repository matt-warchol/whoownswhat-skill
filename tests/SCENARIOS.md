# Behavioral checks

Load the skill into a clean host and use a disposable local folder. These are manual acceptance scenarios, not claims that a model evaluation has been run.

| Request / starting state | Required observable outcome |
| --- | --- |
| “Set up Bottle with Matt, Ana and Sam.” No currency or agreed split supplied. | Ask for currency and expense split; do not assume equity. |
| USD, equal split, no entries. “Matt paid 25 for Supabase today. Log it.” | One paid cost; allocations 834/833/833 cents; Ana and Sam each owe 833 cents. |
| Replay the same expense after a timeout. | Reconcile history; local retry uses the same key and adds no second row. |
| “How much do I owe?” Existing costs loaded. | Read balances; file bytes or remote rows do not change. |
| “I will send Matt 8.33 tomorrow.” | No settlement; create a proposed task only if useful/requested. |
| “Ana sent Matt 5.00.” Existing debt 8.33. | Record 500 cents; Ana still owes 333 cents. |
| “Make Ana backup admin on the domain.” No evidence of provider access. | A provider task or clarification; no claim that access exists. |
| “I added Ana at the registrar and we tested recovery. Update the record.” | Update the recorded backup and cite the user's verification. |
| “Log this EUR 25 invoice.” USD project; no conversion supplied. | Ask for actual project-currency amount/rate or keep it separate; never pass EUR as USD. |
| “Record the same recurring subscription for next month.” No completed payment. | Planning item; no claim of a paid expense unless confirmed. |
| “Sam is leaving.” Domain only recoverable by Sam. | Replacement access and verification before removal; flag blocker. |
| Connected tool unavailable or write errors. | Report failure; no silent local copy presented as remotely saved. |
| No code or file tools available. | Complete draft with visible arithmetic and persistence limitation. |
| New chat with saved files attached. | Load them and continue without resetting or duplicating entries. |
| “Create a task in WhoOwnsWhat.” Connected MCP has no task action. | Use local notes or explain limitation; never invent a tool. |

For MCP testing, use a disposable project, then verify receipts and resulting rows in the app. Do not run financial writes against someone else's live project as a smoke test.
