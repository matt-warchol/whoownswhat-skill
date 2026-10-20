#!/usr/bin/env python3
"""A local, single-writer expense ledger. Python standard library only."""
import argparse
from datetime import date
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import json
from math import lcm
import os
from pathlib import Path
import re
import tempfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def amount(raw):
    require(bool(re.fullmatch(r'[0-9]+(?:\.[0-9]{1,2})?', raw)),
            'Use a positive amount like 25.00, without symbols or separators.')
    cents = int(Decimal(raw) * 100)
    require(cents > 0, 'Amount must be greater than zero.')
    return cents


def iso_day(raw):
    require(date.fromisoformat(raw).isoformat() == raw, 'Use YYYY-MM-DD.')
    return raw


def members(specs):
    result = {}
    for spec in specs:
        name, sep, weight = spec.partition('=')
        name = name.strip()
        require(name and name not in result, 'Member names must be nonempty and unique.')
        try:
            value = Decimal(weight if sep else '1')
        except InvalidOperation as exc:
            raise ValueError('Member weights must be positive numbers.') from exc
        require(value.is_finite() and value > 0, 'Member weights must be positive finite numbers.')
        result[name] = str(value)
    require(len(result) >= 2, 'Add at least two members.')
    return result


def allocate(cents, weights):
    """Largest remainder, ties by member order; every cent is assigned once."""
    # Convert decimal weights to integers so allocation never depends on Decimal precision.
    values = [Fraction(x) for x in weights.values()]
    denominator = lcm(*(x.denominator for x in values))
    integers = [x.numerator * (denominator // x.denominator) for x in values]
    total = sum(integers)
    shares = [cents * w // total for w in integers]
    order = sorted(range(len(shares)), key=lambda i: (-(cents * integers[i] % total), i))
    for i in order[:cents - sum(shares)]:
        shares[i] += 1
    return dict(zip(weights, shares))


def balance(data):
    result = dict.fromkeys(data['members'], 0)
    for entry in data['entries']:
        if entry['type'] == 'cost':
            result[entry['payer']] += entry['cents']
            for member, cents in entry['shares'].items():
                result[member] -= cents
        else:
            result[entry['from']] += entry['cents']
            result[entry['to']] -= entry['cents']
    return result


def validate(data):
    require(isinstance(data, dict) and data.get('version') == 1, 'Unsupported ledger format.')
    require(isinstance(data.get('project'), str) and data['project'].strip(), 'Missing project name.')
    require(data.get('currency') in ('USD', 'EUR', 'GBP', 'PLN'), 'Supported currencies: USD, EUR, GBP, PLN.')
    require(isinstance(data.get('members'), dict), 'Missing members.')
    checked = members([f'{k}={v}' for k, v in data['members'].items()])
    require(checked == data['members'], 'Invalid member names or weights.')
    require(isinstance(data.get('entries'), list), 'Missing entries.')
    keys = set()
    for entry in data['entries']:
        require(isinstance(entry, dict), 'Invalid entry.')
        key = entry.get('key')
        require(isinstance(key, str) and key.strip() and key not in keys, 'Missing or duplicate operation key.')
        keys.add(key)
        require(type(entry.get('cents')) is int and entry['cents'] > 0, 'Invalid cents.')
        iso_day(entry.get('date', ''))
        if entry.get('type') == 'cost':
            require(entry.get('payer') in checked, 'Unknown payer.')
            require(isinstance(entry.get('vendor'), str) and entry['vendor'].strip(), 'Missing vendor.')
            shares = entry.get('shares')
            require(isinstance(shares, dict) and set(shares) == set(checked), 'Shares must include all members.')
            require(all(type(x) is int and x >= 0 for x in shares.values()), 'Invalid cost shares.')
            require(sum(shares.values()) == entry['cents'], 'Cost shares do not equal the amount.')
            require(type(entry.get('recurring')) is bool, 'Invalid recurring flag.')
        else:
            require(entry.get('type') == 'settlement', 'Unknown entry type.')
            require(entry.get('from') in checked and entry.get('to') in checked, 'Unknown settlement member.')
            require(entry['from'] != entry['to'], 'Settlement members must differ.')
    require(sum(balance(data).values()) == 0, 'Ledger does not balance.')
    return data


def save(path, data, *, new=False):
    validate(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Single-writer only. Atomic replacement protects against an interrupted write.
    if new:
        with path.open('x', encoding='utf-8') as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write('\n')
        return
    temp = None
    try:
        with tempfile.NamedTemporaryFile('w', dir=path.parent, encoding='utf-8', delete=False) as handle:
            temp = handle.name
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp and os.path.exists(temp):
            os.unlink(temp)


def summary(data):
    balances = balance(data)
    debtors = [[name, -value] for name, value in balances.items() if value < 0]
    creditors = [[name, value] for name, value in balances.items() if value > 0]
    plan = []
    for debtor in debtors:
        for creditor in creditors:
            cents = min(debtor[1], creditor[1])
            if cents:
                plan.append({'from': debtor[0], 'to': creditor[0], 'cents': cents})
                debtor[1] -= cents
                creditor[1] -= cents
    return {'project': data['project'], 'currency': data['currency'],
            'total_cost_cents': sum(x['cents'] for x in data['entries'] if x['type'] == 'cost'),
            'balance_cents': balances, 'suggested_payments': plan}


def run(args):
    path = Path(args.file)
    if args.command == 'init':
        data = {'version': 1, 'project': args.project, 'currency': args.currency,
                'members': members(args.members), 'entries': []}
        save(path, data, new=True)
        return {'saved_to': str(path), **summary(data)}
    data = validate(json.loads(path.read_text(encoding='utf-8')))
    if args.command == 'status':
        return summary(data)
    cents = amount(args.amount)
    entry = {'key': args.key, 'type': 'cost' if args.command == 'cost' else 'settlement',
             'cents': cents, 'date': iso_day(args.date)}
    if args.command == 'cost':
        require(args.payer in data['members'], 'Unknown payer.')
        entry.update(vendor=args.vendor, payer=args.payer, recurring=args.recurring,
                     shares=allocate(cents, data['members']))
    else:
        require(args.sender in data['members'] and args.recipient in data['members'], 'Unknown member.')
        require(args.sender != args.recipient, 'A person cannot reimburse themselves.')
        entry.update({'from': args.sender, 'to': args.recipient})
    for previous in data['entries']:
        if previous['key'] == args.key:
            require(previous == entry, 'Operation key already used for different facts. Nothing changed.')
            return {'already_saved': True, 'entry': previous, **summary(data)}
    before = balance(data)
    if args.command == 'settle':
        require(before[args.sender] < 0 and before[args.recipient] > 0,
                'Payment direction does not match the current balance. Nothing changed.')
        require(cents <= min(-before[args.sender], before[args.recipient]),
                'Payment exceeds the current outstanding balance. Nothing changed.')
    data['entries'].append(entry)
    save(path, data)
    return {'saved_to': str(path), 'entry': entry, 'balance_before_cents': before, **summary(data)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', required=True, help='Path to the private project ledger JSON file.')
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--project', required=True)
    init.add_argument('--currency', required=True, choices=['USD', 'EUR', 'GBP', 'PLN'])
    init.add_argument('--members', nargs='+', required=True, help='Names or relative weights: Ana=60 Sam=40.')
    sub.add_parser('status')
    for command in ('cost', 'settle'):
        action = sub.add_parser(command)
        action.add_argument('--key', required=True, help='Unique operation ID. Reuse it for a retry.')
        action.add_argument('--amount', required=True)
        action.add_argument('--date', required=True, help='Actual payment date, YYYY-MM-DD.')
        if command == 'cost':
            action.add_argument('--vendor', required=True)
            action.add_argument('--payer', required=True)
            action.add_argument('--recurring', action='store_true')
        else:
            action.add_argument('--from', dest='sender', required=True)
            action.add_argument('--to', dest='recipient', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args), indent=2, ensure_ascii=False))
    except (ValueError, OSError, KeyError, TypeError, OverflowError) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
