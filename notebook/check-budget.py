# -*- coding: utf-8 -*-
from budget.budget import Budget
from budget.functions import combine_debit_credit, prepare_data, add_fx_rate

budget = Budget('../data/budget/budget_new.csv')
budget.budget

# +
import glob, datetime, re
import numpy as np
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

class Transaction():
    latest_historic_file = None
    base_path='../data/transactions/'
    transactions=None
    
    def __init__(self):
        pass
    
    def add_transactions(self, f_path, name, at_total, config):
        if config not in bank_configs:
            raise ValueError(f'Not Existing Configuration: {config}')
        df = self._prepare_transactions(f_path, name, at_total, bank_configs[config])
        self.transactions = self.merge_with_existing_data(df, name)
    
    def read_transaction_data(self, source):
        historic_files = glob.glob(self.base_path + f'{source}-20*.csv')

        if len(historic_files) == 0:
            raise ValueError(f"No Transaction Data Available for {source}")

        historic_files_max_idx = np.argmax([ re.search(r'(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})',f).group() for f in historic_files])
        self.latest_historic_file = historic_files[historic_files_max_idx]
        latest_df = pd.read_csv(self.latest_historic_file, parse_dates=['transaction_date'], dtype={
                                'amount':np.float32,
                                'description': object,
                                'beneficiary': object,
                                'currency': object,
                                'name': object,
                                'total': np.float32,
                                'label': object
                            }).sort_values(['transaction_date','description','beneficiary','amount'],ascending=False)

#         latest_df['source'] = source
#         latest_df['fx_rate'] = add_fx_rate(latest_df)
        return latest_df

    def merge_with_existing_data(self, df, source):
        historic_files = glob.glob(self.base_path + f'{source}*.csv')
        new = df.sort_values(['transaction_date','description','beneficiary','amount'],ascending=False)
        new['label'] = ''
        upload_datetime = datetime.datetime.strftime(datetime.datetime.utcnow(),'%Y-%m-%d-%H-%M')

        if len(historic_files) == 0:
            print('No historic files. New File is written.')
            df_new = new
        else:
            df = self.read_transaction_data(source)
            latest_transaction = df['transaction_date'].max()
            # TODO Improve merge procedure to avoid missing data
            new = new.loc[new['transaction_date'] > latest_transaction,:]
            df_new = pd.concat([new, df])
            if df_new.equals(df):
                print(f'Warning: No new transactions added. No Output written for {source}.')
                return
            elif len(df_new) <= len(df):
                print(f'Warning: Data has changed but new output is shorter or of equal length. No Output written for {source}.')
                return

        df_new.to_csv(self.base_path + f'{source}-{upload_datetime}.csv', index=False)
        return df_new

    def _prepare_transactions(self, f_path, name, at_total, json_config):
        if json_config['format'] == 'csv':
            df = pd.read_csv(f_path, 
                             delimiter=json_config['delimiter'], 
                             skiprows=json_config['skiprows'], 
                             encoding= 'unicode_escape')
        elif json_config['format'] == 'xlsx':
            df = pd.read_excel(f_path, 
                               sheet_name=json_config['sheetname'], 
                               skiprows=json_config['skiprows'], 
                               engine="openpyxl")
        
        df = df.iloc[json_config['drop_rows']:,:]
        
        if "amount_map" in json_config:
            df = combine_debit_credit(df, json_config['amount_map'], json_config['mapping'])

        df = prepare_data(df, 
                              json_config['mapping'], 
                              dayfirst=json_config['dayfirst'], 
                              currency=json_config['currency'], 
                              name=name, 
                              cent_delimiter=json_config['cent_delimiter'], 
                              at_total=at_total)
        return df
        


# -

t = Transaction()
t.add_transactions(dkb_path, dkb_name, dkb_at_total, dkb_config)

# +
dkb_path = "../data/raw/dkb.csv"
dkb_name = "dkb"
dkb_at_total = ('2021-11-21', 554.26)
dkb_config = 'dkb'

dkb_credit_path = "../data/raw/dkb-credit.csv"
dkb_credit_name = "dkb-credit"
dkb_credit_at_total = ('2021-12-02', -479.03)
dkb_credit_config = 'dkb-credit'

n26_sebastian_path = "../data/raw/n26-sebastian.csv"
n26_sebastian_name = 'n26-sebastian'
n26_sebastian_at_total = ('2021-11-21', 23.02)
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
barclays_at_total = ('2021-11-17', -5746.52)
barclays_config = 'barclays'

capital_one_path = "../data/raw/capital-one.csv"
capital_one_name = 'capital-one'
capital_one_at_total = ('2021-11-28', -617.63)
capital_one_config = 'capital-one'
# -

transactions = Transaction()
transactions.add_transactions(f_path=dkb_path,
name=dkb_name,
at_total=dkb_at_total,
config=dkb_config)

transactions = Transaction()
transactions.add_transactions(f_path=dkb_credit_path,
name=dkb_credit_name,
at_total=dkb_credit_at_total,
config=dkb_credit_config)

transactions = Transaction()
transactions.add_transactions(f_path=n26_sebastian_path,
name=n26_sebastian_name,
at_total=n26_sebastian_at_total,
config=n26_sebastian_config)

transactions = Transaction()
transactions.add_transactions(f_path=n26_brett_path,
name=n26_brett_name,
at_total=n26_brett_at_total,
config=n26_brett_config)

transactions = Transaction()
transactions.add_transactions(f_path=bofa_sebastian_path,
name=bofa_sebastian_name,
at_total=bofa_sebastian_at_total,
config=bofa_sebastian_config)

transactions = Transaction()
transactions.add_transactions(f_path=bofa_brett_path,
name=bofa_brett_name,
at_total=bofa_brett_at_total,
config=bofa_brett_config)

transactions = Transaction()
transactions.add_transactions(f_path=barclays_path,
name=barclays_name,
at_total=barclays_at_total,
config=barclays_config)

transactions = Transaction()
transactions.add_transactions(f_path=capital_one_path,
name=capital_one_name,
at_total=capital_one_at_total,
config=capital_one_config)


