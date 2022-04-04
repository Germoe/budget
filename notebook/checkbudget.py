# -*- coding: utf-8 -*-
from budget.budget import Budget
from budget.functions import combine_debit_credit, prepare_data, add_fx_rate

budget = Budget('../data/budget/budget_new.csv')
budget.budget

# +
import pandas as pd

bank_configs = {
    'dkb': {
        'format': 'csv',
        'skiprows': 6,
        'delimiter': ';',
        'currency': 'EUR',
        'cent_delimiter': ',',
        'dayfirst': True,
        'drop_rows': 0,
        'mapping': {
            'transaction_date': 'Buchungstag',
            'beneficiary': 'Auftraggeber / Begünstigter',
            'amount': 'Betrag (EUR)',
            'description': 'Verwendungszweck'
        }
    },
    'dkb-credit': {
        'format': 'csv',
        'skiprows': 6,
        'delimiter': ';',
        'currency': 'EUR',
        'cent_delimiter': ',',
        'dayfirst': True,
        'drop_rows': 0,
        'mapping': {
            'transaction_date': 'Belegdatum',
            'amount': 'Betrag (EUR)',
            'description': 'Beschreibung'
        }
    },
    'n26': {
        'format': 'csv',
        'skiprows': 0,
        'delimiter': ',',
        'currency': 'EUR',
        'cent_delimiter': '.',
        'dayfirst': False,
        'drop_rows': 0,
        'mapping': {
            'transaction_date': 'Date',
            'beneficiary': 'Payee',
            'amount': 'Amount (EUR)',
            'description': 'Payment reference'
        }
    },
    'bofa': {
        'format': 'csv',
        'skiprows': 6,
        'delimiter': ',',
        'currency': 'USD',
        'cent_delimiter': '.',
        'dayfirst': False,
        'drop_rows': 0,
        'mapping': {
            'transaction_date': 'Date',
            'amount': 'Amount',
            'description': 'Description'
        }
    },
    'barclays': {
        'format': 'xlsx',
        'sheetname': 0,
        'skiprows': 12,
        'currency': 'EUR',
        'cent_delimiter': ',',
        'dayfirst': True,
        'drop_rows': 0,
        'mapping': {
            'transaction_date': 'Buchungsdatum',
            'amount': 'Betrag',
            'description': 'Beschreibung'
        }
    },
    'capital-one': {
        'format': 'csv',
        'skiprows': 0,
        'delimiter': ',',
        'currency': 'USD',
        'cent_delimiter': '.',
        'dayfirst': False,
        'drop_rows': 0,
        'mapping': {
            'transaction_date': 'Transaction Date',
            'amount': 'amount',
            'description': 'Description'
        },
        'amount_map': {
            '+': 'Credit',
            '-': 'Debit'
        }
    }
}



# +
dkb_path = "../data/raw/dkb.csv"
dkb_name = "dkb"
dkb_at_total = ('2022-04-03', 2994.55)
dkb_config = 'dkb'

dkb_credit_path = "../data/raw/dkb-credit.csv"
dkb_credit_name = "dkb-credit"
dkb_credit_at_total = ('2022-04-01', -126.12)
dkb_credit_config = 'dkb-credit'

n26_sebastian_path = "../data/raw/n26-sebastian.csv"
n26_sebastian_name = 'n26-sebastian'
n26_sebastian_at_total = ('2022-04-04', 142.36)
n26_sebastian_config = 'n26'

n26_brett_path = "../data/raw/n26-brett.csv"
n26_brett_name = 'n26-brett'
n26_brett_at_total = ('2021-11-21', 128.50)
n26_brett_config = 'n26'

bofa_sebastian_path = "../data/raw/bofa-sebastian.csv"
bofa_sebastian_name = 'bofa-sebastian'
bofa_sebastian_at_total = ('11-21-2021', 1581.70) 
bofa_sebastian_config = 'bofa'

bofa_brett_path = "../data/raw/bofa-brett.csv"
bofa_brett_name = 'bofa-brett'
bofa_brett_at_total = ('11-21-2021', 118.77)
bofa_brett_config = 'bofa'

barclays_path = "../data/raw/barclays.xlsx"
barclays_name = 'barclays'
barclays_at_total = ('2022-04-01', -1067.92)
barclays_config = 'barclays'

capital_one_path = "../data/raw/capital-one.csv"
capital_one_name = 'capital-one'
capital_one_at_total = ('2021-11-28', -617.63)
capital_one_config = 'capital-one'
# -

transactions = Transaction(dkb_name)
transactions.add_transactions(f_path=dkb_path,
name=dkb_name,
at_total=dkb_at_total,
config=dkb_config)
transactions.update_total(dkb_at_total)

transactions = Transaction(dkb_credit_name)
transactions.add_transactions(f_path=dkb_credit_path,
name=dkb_credit_name,
at_total=dkb_credit_at_total,
config=dkb_credit_config)
transactions.update_total(dkb_credit_at_total)

transactions = Transaction(n26_sebastian_name)
transactions.add_transactions(f_path=n26_sebastian_path,
name=n26_sebastian_name,
at_total=n26_sebastian_at_total,
config=n26_sebastian_config)
transactions.update_total(n26_sebastian_at_total)

transactions = Transaction(n26_brett_name)
transactions.add_transactions(f_path=n26_brett_path,
name=n26_brett_name,
at_total=n26_brett_at_total,
config=n26_brett_config)
transactions.update_total(n26_brett_at_total)

transactions = Transaction(bofa_sebastian_name)
transactions.add_transactions(f_path=bofa_sebastian_path,
                            name=bofa_sebastian_name,
                            at_total=bofa_sebastian_at_total,
                            config=bofa_sebastian_config)
transactions.update_total(bofa_sebastian_at_total)

transactions = Transaction(bofa_brett_name)
transactions.add_transactions(f_path=bofa_brett_path,
name=bofa_brett_name,
at_total=bofa_brett_at_total,
config=bofa_brett_config)
transactions.update_total(bofa_brett_at_total)

transactions = Transaction(barclays_name)
transactions.add_transactions(f_path=barclays_path,
name=barclays_name,
at_total=barclays_at_total,
config=barclays_config)
transactions.update_total(barclays_at_total)

transactions = Transaction(capital_one_name)
transactions.add_transactions(f_path=capital_one_path,
name=capital_one_name,
at_total=capital_one_at_total,
config=capital_one_config)
transactions.update_total(capital_one_at_total)




