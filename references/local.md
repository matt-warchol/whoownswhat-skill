# Local files: private, portable, explicit

Requires Python 3.9+ with its standard library. Resolve the helper path relative to this skill, not the user's working directory. Store the user's records in their project workspace, outside the installed skill and any public repository. Two files are enough:

- `project.ledger.json`: costs, reimbursements, member weights and exact integer cents.
- `project-notes.md`: ownership, backlog, decisions and handover, copied from the template.

Read existing files before making changes. Never reset an existing ledger with `init`. If the user brings an older export, establish which version is authoritative before editing. One writer at a time: this helper is not a multi-user database and does not lock concurrent edits.

## Commands

Run from the skill folder, substituting the actual private project path:

```sh
python3 scripts/ledger.py --file /path/to/my-project/project.ledger.json init \
  --project Bottle --currency USD --members Matt Ana Sam

python3 scripts/ledger.py --file /path/to/my-project/project.ledger.json cost \
  --key cost-2026-10-20-supabase-1 --vendor 'Supabase Pro' --payer Matt \
  --amount 25.00 --date 2026-10-20 --recurring

python3 scripts/ledger.py --file /path/to/my-project/project.ledger.json status

python3 scripts/ledger.py --file /path/to/my-project/project.ledger.json settle \
  --key payment-2026-10-21-ana-1 --from Ana --to Matt \
  --amount 8.33 --date 2026-10-21
```

The settlement command is for an already completed payment. A plan returned by `status` is a suggestion, not a record that money moved.

For an agreed 60/40 split use `--members Matt=60 Ana=40` when initializing. Weights are relative and need not sum to 100. Names must be unique; reuse them exactly. An omitted weight is 1. Currency is one of USD, EUR, GBP, PLN (two decimal places). Amounts accept `25` or `25.00`, without currency signs or grouping separators. Reject excess precision rather than silently rounding an invoice.

Dates are required and must be `YYYY-MM-DD`. Use the user's current date for “today”; do not copy example dates. `recurring` labels the paid cost and never generates later charges. Every cost stores its own allocated cents so historical shares are preserved. The helper deliberately has no membership/share-edit command; a change in membership or expense rules needs a separately reconciled new period or the full app. Do not edit old allocations silently.

## Exact money and retries

Expense cents are allocated by largest remainder. Ties follow the member order from initialization. A 25.00 expense shared equally by Matt, Ana and Sam allocates 8.34, 8.33, 8.33. Matt's net credit is 16.66; Ana and Sam each owe 8.33. This is the local helper's rounding convention; remote service receipts remain authoritative in connected mode.

Positive `balance_cents` means the member should receive money; negative means they owe money. Settlement suggestions pair debtors and creditors deterministically; they do not claim the globally fewest possible transfers. Costs remain in the history after reimbursement.

Give each real operation a stable unique `--key`. Reusing a key with the same facts is a safe retry; reusing it with changed facts fails. Two different keys can still represent the same real expense, so check the existing ledger before importing or creating another key. A payment is capped at the sender's debt and recipient's credit. Refunds, overpayments, multi-currency conversion and reversals are not supported by this helper; explain that limitation instead of inserting a negative expense or rewriting history.

Write commands return the saved entry, balances before and after, and the output path. Reads never change the file. Existing files are replaced atomically after validation. On a nonzero exit, read the error and do not claim the entry was saved. For a correction, preserve the original file, identify the affected entry and make a clearly explained revision only when requested; never manufacture a reimbursement to hide an error.

## Hosts without a shell or durable files

Use the supplied template as a draft in chat. Show each cost's payer, date, currency, amount and allocated shares, followed by balances and completed reimbursements. Keep planned purchases separate. Recalculate with an available calculator or code tool; if unavailable, make the arithmetic visible. Provide the complete updated record to copy or download. Say explicitly that it is a draft until saved by the user. Ask them to bring that record into a later chat rather than relying on assistant memory.
