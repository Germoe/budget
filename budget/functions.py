import glob, re
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