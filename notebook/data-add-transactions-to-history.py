#!/usr/bin/env python
# coding: utf-8

# In[97]:


import glob
import numpy as np
import pandas as pd
import datetime
import re
from forex_python.converter import CurrencyRates


# In[98]:


# Classifier
from textblob.classifiers import NaiveBayesClassifier
from colorama import init, Fore, Style
from tabulate import tabulate
import re, os
import numpy as np
import pandas as pd
import glob

class BankClassify():

    def __init__(self, names=['bofa-sebastian','barclays','dkb-credit','dkb','n26-sebastian','postbank']):
        """Load in the previous data (by default from `data`) and initialise the classifier"""

        self.prev_data = pd.concat([read_transaction_data(name) for name in names]).dropna(subset=['label'])

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


# In[136]:


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
                            'total': np.object,
                            'label': np.object
                        })
    
    latest_df['source'] = source
    latest_df['fx_rate'] = add_fx_rate(latest_df)
    
    if return_name == True:
        return latest_df, latest_historic_file
    return latest_df

def add_transaction_data(file, source, base_path='../data/transactions/'):
    historic_files = glob.glob(base_path + f'{source}*.csv')
    new = pd.read_csv(file, parse_dates=['transaction_date'])
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
        df = pd.concat([df, new])
    
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
                update_label_data(df, source)

                # Update classifier
                bc.classifier.update([(input_text, category)])
                
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


# In[178]:


add_transaction_data('../data/cln/bofa-sebastian.csv', 'bofa-sebastian')
add_transaction_data('../data/cln/bofa-brett.csv', 'bofa-brett')
add_transaction_data('../data/cln/barclays.xlsx', 'barclays')
add_transaction_data('../data/cln/dkb-credit.csv', 'dkb-credit')
add_transaction_data('../data/cln/dkb.csv', 'dkb')
add_transaction_data('../data/cln/n26-csv-sebastian.csv', 'n26-sebastian')
add_transaction_data('../data/cln/n26-csv-brett.csv', 'n26-brett')
add_transaction_data('../data/cln/postbank.csv', 'postbank')


# In[179]:


# df, name = read_transaction_data('n26-brett', return_name=True)
# df.drop('total',axis=1).to_csv(name,index=False)


# In[70]:


paths = ['../data/cln/bofa-sebastian-historic-data.csv', '../data/cln/barclays-historic-data.xlsx', '../data/cln/dkb-credit-historic-data.csv', '../data/cln/dkb-historic-data.csv', '../data/cln/n26-csv-sebastian.csv', '../data/cln/n26-csv-brett.csv', '../data/cln/postbank-data.csv']
tables = ['bofa-sebastian','barclays','dkb-credit','dkb','n26-sebastian','n26-brett','postbank']
for name, path in zip(tables,paths):
    new = pd.read_csv(path, parse_dates=['transaction_date'])
    add_column(new, name, col='total')


# In[148]:


df = read_transaction_data('n26-brett')
targets = df.loc[(df['beneficiary'].str.contains('Laura Crimmons')) & (df['amount'] == 20),:]
targets


# In[149]:


for idx, row in targets.iterrows():
    cond = (targets['transaction_date'] == row['transaction_date']) &               (targets['amount'] == row['amount']) &                (targets['description'] == row['description']) &                (targets['name'] == row['name'])
    relabel(targets.loc[cond,:],'fun')


# In[154]:





# In[175]:


df_cln = read_transaction_data('n26-brett')
at_total = ('2021-11-17', 158.58)
end_bal = df_cln.loc[df_cln['transaction_date'] > at_total[0],['transaction_date','amount']].sort_values('transaction_date', ascending=True)
end_bal['total'] = at_total[1] + end_bal['amount'].shift(0).cumsum()
end_bal = end_bal.iat[-1, 2]
# end_bal

df_cln['total'] = end_bal - df_cln['amount'].shift(1).cumsum()
df_cln['total'].iat[0] = end_bal


# In[176]:


df_cln


# In[ ]:




