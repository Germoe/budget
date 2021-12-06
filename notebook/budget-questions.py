#!/usr/bin/env python
# coding: utf-8

# In[7]:


import numpy as np
import pandas as pd
from ipywidgets import interact, widgets
import glob
import os
import re
import datetime
from forex_python.converter import CurrencyRates

pd.options.plotting.backend = "plotly"
 
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

def show_last_month_cat(cat):
    df = df_last_month.reset_index()
    return df.loc[(df['cat'] == cat),:]

def filter_last_month(lower_bound=None, upper_bound=None):
    df = df_last_month.reset_index()
    if (lower_bound is not None) and (upper_bound is not None):
        return df.loc[(df['amount'] > lower_bound) & (df['amount'] < upper_bound),:]
    elif lower_bound is not None and upper_bound is None:
        return df.loc[(df['amount'] > lower_bound),:]
    elif lower_bound is None and upper_bound is not None:
        return df.loc[(df['amount'] < upper_bound),:]
    else:
        return df

def show_last_month_cat_budget(cat):
    df = budget_last_month.reset_index()
    return df.loc[(df['cat'] == cat),:]


# In[8]:


today = datetime.date.today()
first = today.replace(day=1)
last_month = (first - datetime.timedelta(days=1)).replace(day=1)
last_month_str = last_month.strftime("%Y-%m-%d")


# In[3]:


# Did we spent our money the way we planned?


# In[9]:


# Budget Plan
budget = pd.read_csv('../data/budget/budget_cln.csv', parse_dates=['budget_month'])
budget, cats = add_categories(budget, return_cats = True)
budget_last_month = budget.loc[budget['budget_month'] == last_month_str,:].groupby(['budget_month','type','cat','label']).sum()
budget_last_month_cat = budget.loc[budget['budget_month'] == last_month_str,:].groupby(['budget_month','type','cat']).sum()

# Actuals
names = ['bofa-sebastian','bofa-brett','barclays','dkb-credit','dkb','n26-sebastian','n26-brett','capital-one']
df_raw = pd.concat([read_transaction_data(name) for name in names]).set_index('transaction_date')
df_raw = df_raw.loc[df_raw.index >= '2021-09-01',:]
df_raw = add_categories(df_raw)

## Remove Transactions to ignore
df_raw = df_raw.loc[df_raw['cat'] != 'ignore', :]
df_raw['budget_month'] = df_raw.index.to_numpy().astype('datetime64[M]')

## Last Month Actuals
df_last_month = df_raw[df_raw['budget_month'] == last_month_str].sort_index()
df_last_month_cat = df_last_month.groupby(['budget_month','cat']).sum()['amount']

df_last_month_cat = budget_last_month.join(df_last_month_cat).reset_index()
df_last_month_cat['diff'] = df_last_month_cat['amount'] - df_last_month_cat['budget_value']
diff_last_month_pivot = df_last_month_cat.pivot_table(index=['budget_month','cat'], columns=['type'], values=['amount','budget_value','diff'])
diff_last_month_pivot


# In[10]:


# Show Budget Category Breakdowns 
interact(show_last_month_cat_budget, cat=list(cats.keys()));


# In[11]:


# Show Actual Category Breakdowns 
interact(show_last_month_cat, cat=list(cats.keys()));


# In[12]:


# Filter Actuals by Amount
interact(filter_last_month, 
         lower_bound=widgets.IntSlider(min=df_last_month['amount'].min(), max=df_last_month['amount'].max(), step=1, value=df_last_month['amount'].min()), 
         upper_bound=widgets.IntSlider(min=df_last_month['amount'].min(), max=df_last_month['amount'].max(), step=1, value=df_last_month['amount'].max()));


# In[13]:


# How much money do we have left every month?


# In[14]:


last_month_total = diff_last_month_pivot.loc[:,('amount',slice(None))].droplevel(0, axis=1).fillna(0)
last_month_total['savings/debt'] = last_month_total['income'] + last_month_total['expense']
last_month_total.sum()


# In[15]:


# Average Net Worth


# In[16]:


roll_avg = df_raw.reset_index().groupby('transaction_date').agg({'total': np.average})
roll_avg['rolling_mean'] = roll_avg['total'].rolling(window=28).mean()
roll_avg.plot()


# In[ ]:




