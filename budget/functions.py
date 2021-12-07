import glob, re, datetime
import numpy as np
import pandas as pd
from forex_python.converter import CurrencyRates

def add_fx_rate(df,t='EUR'):
    c = CurrencyRates()
    unique_fx_rates = {curr: c.get_rate(curr, 'EUR') for curr in df['currency'].unique()}
    return df['currency'].map(unique_fx_rates)

def read_transaction_data(source, base_path='../data/transactions/', return_name=False):
    historic_files = glob.glob(base_path + f'{source}-20*.csv')

    if len(historic_files) == 0:
        raise ValueError(f"No Transaction Data Available for {source}")

    historic_files_max_idx = np.argmax([ re.search(r'(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})',f).group() for f in historic_files])
    latest_historic_file = historic_files[historic_files_max_idx]
    latest_df = pd.read_csv(latest_historic_file, parse_dates=['transaction_date'], dtype={
                            'amount':np.float32,
                            'description': np.object,
                            'beneficiary': np.object,
                            'currency': np.object,
                            'name': np.object,
                            'total': np.float32,
                            'label': np.object
                        }).sort_values(['transaction_date','description','beneficiary','amount'],ascending=False)
    
    latest_df['source'] = source
    latest_df['fx_rate'] = add_fx_rate(latest_df)
    
    if return_name == True:
        return latest_df, latest_historic_file
    return latest_df

def add_categories(df, src_col='label', trgt_col='cat', return_cats=False):
    cats = {
        'income': ['income'],
        'shopping': ['fashion','shopping'],
        'groceries': ['groceries'],
        'home': ['home','rent', 'utilities','electricity','heat','water','gas','gez','cell','dsl','internet','insurance'],
        'subscription': ['subscription','amazon prime','apple','prime','medium','medium subscription','patreon','spotify','skype'],
        'work': ['work','office','aws','google storage','domain','class','classes'],
        'debt': ['debt','kfw','bildungsfond'],
        'travel': ['travel','lodging','vacation rental','flight','car rental'],
        'transport': ['transport','bvg','swapfiets','parking','toll'],
        'savings': ['savings','crypto'],
        'fitness': ['fitness','fitx','gym'],
        'fun': ['fun','drinks','drink','concert','food','lunch','coffee','breakfast','movies'],
        'health+beauty': ['hair','pharmacy','drugstore','doctor'],
        'gift': ['gift'],
        'other': ['other','fee','feee','cash','haircut'],
        'transfer': ['transfer','refund'],
        'ignore': ['ignore','none']
    }

    categories = {val: key for key, vals in cats.items() for val in vals}
    df[trgt_col] = df[src_col].str.lower().map(categories)
    if return_cats == True:
        return df, cats
    return df

def print_file(path, show=10):
    with open(path, "r", encoding='utf-8', errors="ignore") as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if i >= show:
                break
            print(i + 1, line)

def combine_debit_credit(df, amount_map, mapping):
    plus_vals = df.loc[~df[amount_map['+']].isna(),[mapping['transaction_date'], mapping['description']]]
    minus_vals = df.loc[~df[amount_map['-']].isna(),[mapping['transaction_date'], mapping['description']]]
    df[amount_map['-']] = -df[amount_map['-']]
    if len(plus_vals.index.intersection(minus_vals.index)) == 0:
        df['amount'] = df[amount_map['+']].combine_first(df[amount_map['-']])
    return df
            
def prepare_data(df, mapping, dayfirst, currency, name, cent_delimiter, at_total=None):
    use_cols = [col for col in mapping.values()]
    use_names = [name for name in mapping.keys()]
    
    df_cln = df.loc[:,use_cols]
    df_cln.columns = use_names    

    # Define mandatory cols
    mandatory_cols = ['transaction_date','beneficiary','amount','description']
    for man_col in mandatory_cols:
        if man_col not in df_cln.columns:
            df_cln[man_col] = ''
    
    # Add Known Information
    df_cln['currency'] = currency
    df_cln['name'] = name

    # Date Column
    df_cln['transaction_date'] = pd.to_datetime(df_cln['transaction_date'], dayfirst=dayfirst)
            
    # Sort Values
    df_cln = df_cln.sort_values('transaction_date', ascending=False)

    # Value Column
    if df_cln['amount'].dtype == 'O':
        df_cln['amount'] = df_cln['amount'].str.extract(r'((\d|\.|,|-)+)')[0]
        if cent_delimiter == ',':
            df_cln['amount'] = pd.to_numeric(df_cln['amount'].str.replace('.','').str.replace(',','.'), downcast='float')
        else:
            df_cln['amount'] = pd.to_numeric(df_cln['amount'].str.replace(',',''), downcast='float')

    # Fill NaN Values 
    df_cln['description'] = df_cln['description'].fillna('other')
    
    # Add total_at
    if at_total is not None:
        # Calculate Beginning Balance
        if (df_cln['transaction_date'] > at_total[0]).sum() > 0:
            end_bal = df_cln.loc[df_cln['transaction_date'] > at_total[0],['transaction_date','amount']].sort_values('transaction_date', ascending=True)
            end_bal['total'] = at_total[1] + end_bal['amount'].shift(0).cumsum()
            end_bal = end_bal.iat[-1, 2]
        else:
            end_bal = at_total[1]
        
        df_cln['total'] = end_bal - df_cln['amount'].shift(1).cumsum()
        df_cln['total'].iat[0] = end_bal

    return df_cln


# Classifier
from textblob.classifiers import NaiveBayesClassifier
from colorama import init, Fore, Style
from tabulate import tabulate
import re, os
import numpy as np
import pandas as pd
import glob

class BankClassify():

    def __init__(self, names=['bofa-sebastian','bofa-brett','barclays','dkb-credit','dkb','n26-sebastian','postbank','capital-one']):
        """Load in the previous data (by default from `data`) and initialise the classifier"""

        self.prev_data = pd.concat([read_transaction_data(name) for name in names]).dropna(subset=['label']).reset_index(drop=True)

        self.classifier = NaiveBayesClassifier(self._get_training(self.prev_data), self._extractor)
        
    def _get_training(self, df):
        """Get training data for the classifier, consisting of tuples of
        (text, category)"""
        train = []
        subset = df[df['label'] != '']
        for i in subset.index:
            row = subset.iloc[i]
            train.append( (str(row['description']) + ' ' + str(row['beneficiary']), row['label']) )

        return train

    def _extractor(self, doc):
        """Extract tokens from a given string"""
        # TODO: Extend to extract words within words
        # For example, MUSICROOM should give MUSIC and ROOM
        doc = re.sub(r'\d+', '', doc) # Strip Numbers
        tokens = self._split_by_multiple_delims(doc, [' ', '/'])

        features = {}

        for token in tokens:
            if token == "":
                continue
            features[token] = True

        return features
            
    def _split_by_multiple_delims(self, string, delims):
        """Split the given string by the list of delimiters given"""
        regexp = "|".join(delims)
        
        return re.split(regexp, string)

def read_transaction_data(source, base_path='../data/transactions/', return_name=False):
    historic_files = glob.glob(base_path + f'{source}-20*.csv')
    
    if len(historic_files) == 0:
        raise ValueError(f"No Transaction Data Available for {source}")
    
    historic_files_max_idx = np.argmax([ re.search(r'(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})',f).group() for f in historic_files])
    latest_historic_file = historic_files[historic_files_max_idx]
    latest_df = pd.read_csv(latest_historic_file, parse_dates=['transaction_date'], dtype={
                            'amount':np.float32,
                            'description': np.object,
                            'beneficiary': np.object,
                            'currency': np.object,
                            'name': np.object,
                            'total': np.float32,
                            'label': np.object
                        }).sort_values(['transaction_date','description','beneficiary','amount'],ascending=False)
    
    latest_df['source'] = source
    latest_df['fx_rate'] = add_fx_rate(latest_df)
    
    if return_name == True:
        return latest_df, latest_historic_file
    return latest_df

def add_transaction_data(file, source, base_path='../data/transactions/'):
    historic_files = glob.glob(base_path + f'{source}*.csv')
    new = pd.read_csv(file, parse_dates=['transaction_date']).sort_values(['transaction_date','description','beneficiary','amount'],ascending=False)
    new['label'] = ''
    upload_datetime = datetime.datetime.strftime(datetime.datetime.utcnow(),'%Y-%m-%d-%H-%M')
    
    if len(historic_files) == 0:
        df = new
    else:
        df = read_transaction_data(source)
        latest_transaction = df['transaction_date'].max()
        new = new.loc[new['transaction_date'] > latest_transaction,:]
        if len(new) == 0:
            print(f'Warning: No New Transactions. No Output written for {source}.')
            return 
        df = pd.concat([new, df])
    
    df.to_csv(base_path + f'{source}-{upload_datetime}.csv', index=False)
    
def add_column(new, source, col, base_path='../data/transactions/', force=False):
    df = read_transaction_data(source)
    
    upload_datetime = datetime.datetime.strftime(datetime.datetime.utcnow(),'%Y-%m-%d-%H-%M')
    
    if (col in df.columns) and force == False:
        print(f'Warning: {col} already in output. No Output written for {source}.')
        return
    
    if col not in new.columns:
        print(f'Warning: New column {col} does not exist. No Output written for {source}.')
        return
    
    new_cols = [new_col for new_col in new.columns if new_col not in df.columns]
    for new_col in new_cols:
        df[new_col] = new[new_col]
        
    df.to_csv(base_path + f'{source}-{upload_datetime}.csv', index=False)
    
def label_data(source):
    df = read_transaction_data(source)
    no_label = df.loc[df['label'].isna(),:]
    
    bc = BankClassify()
    for index, row in no_label.iterrows():
            # Guess Category
            input_text = str(row['description']) + ' ' + str(row['beneficiary'])
            extracted = " ".join(bc._extractor(input_text))
            guess = bc.classifier.classify(input_text)
        
            # Print list of categories
            print(chr(27) + "[2J")
            print("\n\n")
            # Print classification
            print(f"Is it: {guess}")
            print(f"Based on: {extracted}")
            # Print transaction
            print("On: %s\t %.2f\n%s\n%s" % (row['transaction_date'], row['amount'], row['description'], row['beneficiary']))

            input_value = input("> ")
            
            if input_value == 'skip':
                print('skipped')
                continue
            else:
                if input_value == '':
                    category = guess
                else:
                    category = input_value
                
                df.at[index, 'label'] = category
                update_label(df, source)

                # Update classifier
                bc.classifier.update([(input_text, category)])
                
def update_label(df, source, base_path='../data/transactions/'):
    df_og = read_transaction_data(source)
    if df.drop('label', axis=1).equals(df_og.drop('label', axis=1)) == True:
        upload_datetime = datetime.datetime.strftime(datetime.datetime.utcnow(),'%Y-%m-%d-%H-%M')
        df.to_csv(base_path + f'{source}-{upload_datetime}.csv', index=False)
    else:
        raise ValueError('Updating Label Failed! Source and New DataFrame are not comparable.')
                
def relabel(row, label, base_path='../data/transactions/', multi=False):
    row = row.reset_index()
    transaction_date, amount, description, name, source = row[['transaction_date', 'amount', 'description', 'name','source']].values[0]
    df_new, name_new= read_transaction_data(source, return_name=True)
    cond = (df_new['transaction_date'] == transaction_date) &               (df_new['amount'] == amount) &                (df_new['description'] == description) &                (df_new['name'] == name)
    if (cond.sum() > 1) & (multi==False):
        raise ValueError('More than one row selected')
    df_new.loc[cond,'label'] = label
    upload_datetime = datetime.datetime.strftime(datetime.datetime.utcnow(),'%Y-%m-%d-%H-%M')
    
    df_new.to_csv(base_path + f'{source}-{upload_datetime}.csv', index=False)
    
def add_fx_rate(df,t='EUR'):
    c = CurrencyRates()
    unique_fx_rates = {curr: c.get_rate(curr, 'EUR') for curr in df['currency'].unique()}
    return df['currency'].map(unique_fx_rates)