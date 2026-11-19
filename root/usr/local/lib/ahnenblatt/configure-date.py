#!/usr/bin/env python3
"""Apply an explicitly requested Windows short-date format before app startup."""
import os
import re
import subprocess


def date_values(pattern):
    match = re.fullmatch(r'(d{1,2}|M{1,2}|yyyy|yy)([./-])(d{1,2}|M{1,2}|yyyy|yy)\2(d{1,2}|M{1,2}|yyyy|yy)', pattern)
    if not match:
        raise ValueError('DATE_FORMAT must be numeric, e.g. dd.MM.yyyy, MM/dd/yyyy or yyyy-MM-dd')
    first, separator, second, third = match.groups()
    order = first[0] + second[0] + third[0]
    if order not in ('dMy', 'Mdy', 'yMd'):
        raise ValueError('DATE_FORMAT must use day-month-year, month-day-year or year-month-day')
    return {'sShortDate': pattern, 'sDate': separator,
            'iDate': {'Mdy': '0', 'dMy': '1', 'yMd': '2'}[order]}


def configure(pattern):
    if not pattern:
        return
    values = date_values(pattern)
    for name, value in values.items():
        subprocess.run(['wine', 'reg', 'add', r'HKCU\Control Panel\International',
                        '/v', name, '/t', 'REG_SZ', '/d', value, '/f'],
                       check=True, timeout=30)
    subprocess.run(['wineserver', '-w'], check=True, timeout=60)
    print(f'[ahnenblatt] Windows date format: {pattern}', flush=True)


if __name__ == '__main__':
    configure(os.environ.get('DATE_FORMAT', ''))
