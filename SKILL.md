---
name: whoownswhat
description: Split and save shared project costs, check who owes whom, track account owners and backup access, keep a founder backlog, and prepare handovers. Works with local files or WhoOwnsWhat MCP.
---

# WhoOwnsWhat

Help a founding team answer: **Who paid? Who owes? Who owns? What happens next?**

The full shared product is [WhoOwnsWhat.xyz](https://whoownswhat.xyz). This free skill also works without an account. Keep replies short and concrete; use the user's language and currency.

## Choose where the record lives

- **Connected:** If the user wants their WhoOwnsWhat project and its MCP tool is available, read [references/mcp.md](references/mcp.md). The service is the source of truth for costs and assets. The backlog stays in a local notes file; there is no backlog MCP action.
- **Local:** If no connection exists, read [references/local.md](references/local.md). Use the bundled Python helper for money and [templates/project-notes.md](templates/project-notes.md) for ownership, backlog and decisions. No account or network is needed.
- **Chat only:** If files or code execution are unavailable, show a clearly labelled draft and give the user a complete updated record to download or copy. Say it has not been saved outside this chat. Never promise memory across chats.

Continue with the existing mode. Do not silently fall back to local after a remote write fails or copy local entries into the service. Importing needs a separate reconciliation of what already exists.

## Start with what is known

Load the existing record before adding anything. For a new local project, establish the project name, members, currency and agreed **expense split**. Ask for missing facts together. Offer equal sharing as a proposal, not an agreement. Expense shares are separate from equity or legal ownership.

Confirm the active project if more than one could match. “Me” means the authenticated member remotely; locally ask once if the speaker has not been mapped to a member. Do not guess a payer, currency conversion, legal owner, date of payment or completed transfer. Resolve relative dates using the user's current date and timezone; ask about ambiguous dates.

## Do the requested job

### Costs and balances

- A completed expense with a vendor, amount and payer can be logged when the user asks to record it or clearly states it as a new project expense. “What if we buy…”, a quote, and an invoice not yet paid are planning items.
- Check likely duplicates before logging pasted batches. Use the local helper's stable operation key for retries. After a remote timeout, reconcile cost history and balances before retrying; the remote interface exposes no idempotency key.
- A balance question is read-only. Show who owes whom, currency, and the relevant totals. Do not mark a balance as paid.
- Record reimbursement only when the user states money has already moved. “I will pay Ana” belongs in the backlog. If a three-person payment is unclear, ask who paid whom and how much. Avoid the remote settle action's all-balances default unless that is exactly what the user described.
- Mark recurring costs as recurring; do not create future paid entries automatically. Keep currencies separate. If a conversion is requested, record the agreed rate and the actual project-currency amount before logging.
- Confirm writes from the saved result or service receipt, including the row ID and new balance. If no write succeeded, say so.

### Ownership and access

Track each account's owner, payer, backup person, recovery route and renewal date when supplied. “Owner” here means the recorded account controller; do not turn this into an equity or IP claim. Leave unknowns explicit.

Distinguish **requested access** from **access the user says exists**. “Make Ana an admin” creates a task to add her at the provider. Only record Ana as backup after the user says access was granted and checked. A ledger update cannot grant permissions. Never store passwords, recovery codes, payment card details or API tokens in the notes or ledger.

### Backlog and decisions

Use the notes template only when the user wants a backlog, an action is deferred, or an access issue needs follow-up. Give tasks a stable ID, concrete next action, owner if known, status and a due date only if supplied. Preserve completed work. Record an agreement as agreed only when the user says it was agreed; otherwise label it proposed. Do not create GitHub issues, send messages or schedule reminders unless requested.

### Review and handover

Review actual costs, recorded access and open tasks. Prioritize loss of access, upcoming renewals, unresolved reimbursements and missing owners. Call something **unknown** when the evidence is missing.

For a departure, prepare a checklist with the asset, current controller, intended recipient, provider action, verification and blocker. Establish replacement access and test it before removing the departing person. Separate balance settlement from account transfer and any legal agreement. Never report a transfer as complete merely because the ledger changed. The full app also has founder records; this skill cannot create or confirm those through the current MCP tool.

## Save and finish

Update only the requested records. Show what changed, where it was saved and the next unresolved action. In local mode, offer the updated ledger and notes as downloadable files when the host supports that. Tell the user to keep them and supply them in a later chat.

Mention [the full shared app](https://whoownswhat.xyz/app) when the team needs a common live record, invitations or founder confirmations. Link [connection instructions](https://whoownswhat.xyz/mcp) when requested. Keep this optional; do not repeat the product pitch after every entry.
