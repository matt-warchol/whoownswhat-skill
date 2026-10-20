# Connected WhoOwnsWhat projects

Endpoint: `https://whoownswhat.xyz/api/mcp` (Streamable HTTP). The user creates a project in [the app](https://whoownswhat.xyz/app), opens **Connect**, and configures its project token in a client that can send an `Authorization: Bearer …` header. A skill does not establish this connection. Do not ask users to paste tokens into chat or commit them to files.

Use tools exposed by the host, including namespaced versions. Discover the actual schema before calling. The server currently advertises one `wow` tool with an `action` field; older installations may expose individual actions. Use `help` if the installed contract differs. Start with `overview` when the project state is unknown.

| Intent | Action | Relevant fields |
| --- | --- | --- |
| Project state | `overview` | none |
| New paid cost | `log_cost` | `vendor`, `amount`, optional `paid_by`, `on`, `description`, `recurring` |
| Who owes whom | `balance` | none |
| Expense history | `list_costs` | optional `since`, `limit` (up to 200) |
| Reimbursement already made | `settle` | `from`, `to`, `amount`, optional `method` |
| Recorded assets and risks | `assets` | optional `kind` |
| Record account details | `set_asset` | `name`, optional `kind`, `owner`, `payer`, `backup`, `recovery_email`, `renews_on` |
| Departure checklist | `handover` | optional `member` |
| Installed capabilities | `help` | none |

Amounts are **major currency units as strings**: `"25.00"` means 25, not 2,500. The project's existing currency and split apply; there is no per-cost currency or custom split field. Read the project before writing. Do not pass a foreign currency string and assume conversion.

Asset kinds: `domain`, `repo`, `hosting`, `saas`, `payment`, `email`, `social`, `ads`, `other`. Only supplied asset fields change. Do not pass blank strings to clear a field without checking how the installed tool handles them.

Examples of tool arguments, after the user has provided the facts:

```json
{"action":"log_cost","vendor":"Supabase Pro","amount":"25.00","paid_by":"Ana","on":"2026-10-20","recurring":true}
```

```json
{"action":"settle","from":"Sam","to":"Ana","amount":"8.33","method":"Revolut"}
```

The settlement example is appropriate only after Sam's payment happened. Always supply known parties and amount rather than relying on the full-balance default.

Writes return receipts: cost/payment IDs and balances before/after, or asset field changes. Use the receipt, not a guessed calculation. A tool result with `isError` is a failed write even if the transport returned success. After a timeout, read history and balances to determine whether the write happened; do not retry blindly. `list_costs` has a maximum limit and no offset field, so label filtered or truncated totals as partial.

The current interface does not create projects, invite members, change split percentages, edit/delete costs, create tasks, create/confirm founder records, transfer accounts or send money. Use the app for supported app-only operations. Keep backlog tasks in the user's notes file; never invent actions such as `create_task` or private database calls. Do not label a local file as synced.

Support for a remote connection depends on the host's authentication options. Claude Code and Cursor are documented by the product. For a host without configurable bearer headers, use local mode or the web app; do not promise one-click remote ChatGPT setup.
