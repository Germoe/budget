import os
import numpy as np
import pandas as pd
import glob, datetime, re

# +
class Budget():
    budget = None
    schema = ['budget_amount']
    
    def __init__(self, path, budget_dict=None):
        """
        Initialize Budget Object.
        """
        self.path = path
        
        try:
            budget = pd.read_csv(self.path, index_col=0)
        except:
            if os.path.exists(self.path) == True:
                raise ValueError('Attempted to create new budget but file already exists at this location.')
            budget = self.create_budget(budget_dict=budget_dict)
            self.budget.to_csv(self.path)
        
        self.budget = budget

    def create_budget(self, budget_dict=None):
        if budget_dict is None:
            budget_dict = {
                'budget_amount': {
                    'income': int(input("What is your total monthly income? >")),
                },
             }

            running_total = 0

            while input('Add another Expense Category (y/n) >') == 'y':
                key = input('Name of Expense: ')
                val = int(input(f'Amount (Current Total Expenses: {running_total}): '))
                budget_dict['budget_amount'][key] = -val

                running_total += val
            
        return pd.DataFrame(budget_dict)
            
    def update_budget(self, key):
        self.budget['budget_amount'][key] = -int(input(f'Amount: '))
        self.budget.to_csv(self.path)
        
class Transaction():
    latest_historic_file = None
    base_path='../data/transactions/'
    source = None
    transactions=None
    
    def __init__(self, source):
        self.source = source
        self.transactions = self.read_transaction_data()
        pass
    
    def add_transactions(self, f_path, name, at_total, config):
        if config not in bank_configs:
            raise ValueError(f'Not Existing Configuration: {config}')
            
        df = self._prepare_transactions(f_path, name, at_total, bank_configs[config])
        self.transactions = self.merge_with_existing_data(df, name, at_total)
        if self.transactions is None:
            print(f'Reading in from: {name}')
            self.transactions = self.read_transaction_data(name)
            
    def read_transaction_data(self):
        source = self.source
        historic_files = glob.glob(self.base_path + f'{source}-20*.csv')

        if len(historic_files) == 0:
            raise ValueError(f"No Transaction Data Available for {source}")

        historic_files_max_idx = np.argmax([ re.search(r'(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})',f).group() for f in historic_files])
        self.latest_historic_file = historic_files[historic_files_max_idx]
        print(f'Reading in from: {self.latest_historic_file}')
        latest_df = pd.read_csv(self.latest_historic_file, parse_dates=['transaction_date'], dtype={
                                'amount':np.float32,
                                'description': object,
                                'beneficiary': object,
                                'currency': object,
                                'name': object,
                                'total': np.float32,
                                'label': object
                            }).sort_values(['transaction_date','description','beneficiary','amount'],ascending=False)
        
        latest_df = latest_df.drop('total',axis=1)
        total_df = self.calc_total(latest_df)
        latest_df = latest_df.merge(total_df[['transaction_date','total']], on='transaction_date', how='left')
        
        return latest_df
    
    def calc_total(self, df):
        df_daily_total = df.groupby(['transaction_date'], as_index=False).agg({'amount': np.sum}).sort_values(['transaction_date'], ascending=False)
        ref_bal = df[['ref_bal','ref_bal_date']].drop_duplicates().dropna()
        end_bal = df_daily_total.loc[df_daily_total['transaction_date'] > ref_bal['ref_bal_date'].values[0],'amount'].sum() + ref_bal['ref_bal']
        df_daily_total.loc[:,'total'] = end_bal.values[0]
        df_daily_total.loc[:,'total'] = (df_daily_total.loc[:,'total'] - df_daily_total['amount'].shift(1).cumsum()).fillna(end_bal.values[0])
        return df_daily_total

    def merge_with_existing_data(self, df, source, at_total):
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
            df = df.loc[df['transaction_date'] < latest_transaction,:].copy(deep=True)
            new = new.loc[new['transaction_date'] >= latest_transaction,:]
            df_new = pd.concat([new, df])
            
            df_new['ref_bal'] = at_total[1]
            df_new['ref_bal_date'] = at_total[0]
            
            if df_new.equals(df):
                print(f'Warning: No new transactions added. No Output written for {source}.')
                return None
            elif len(df_new) <= len(df):
                print(f'Warning: Data has changed but new output is shorter or of equal length. No Output written for {source}.')
                return None

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
    
    
    def update_total(self,at_total):
        # Add total_at
        upload_datetime = datetime.datetime.strftime(datetime.datetime.utcnow(),'%Y-%m-%d-%H-%M')
        
        # Calculate Beginning Balance
        df_cln = self.transactions
        
        if (df_cln['transaction_date'] > at_total[0]).sum() > 0:
            end_bal = df_cln.loc[df_cln['transaction_date'] > at_total[0],['transaction_date','amount']].sort_values('transaction_date', ascending=True)
            end_bal['total'] = at_total[1] + end_bal['amount'].shift(0).cumsum()
            end_bal = end_bal.iat[-1, 2]
        else:
            end_bal = at_total[1]

        df_cln['total'] = end_bal - df_cln['amount'].shift(1).cumsum()
        df_cln['total'].iat[0] = end_bal
        
        self.transactions = df_cln
        self.transactions.to_csv(self.base_path + f'{self.source}-{upload_datetime}.csv', index=False)

