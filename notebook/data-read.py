#!/usr/bin/env python
# coding: utf-8

# In[30]:


import numpy as np
import pandas as pd
from ipywidgets import interact
import glob
import os
import re
import datetime
from forex_python.converter import CurrencyRates


# In[83]:


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

def show_cat(cat, month, year):
    return df.loc[(df['cat'] == cat) & (df['budget_month'].dt.month == month) & (df['budget_month'].dt.year == year),:]


# In[84]:


# Load Data


# In[85]:


budget = pd.read_csv('../data/budget/budget_cln.csv', parse_dates=['budget_month'])
budget, cats = add_categories(budget, return_cats = True)

budget_grouped = budget.groupby([pd.Grouper(key='budget_month', freq='M')]).sum().reset_index()


# In[86]:


names = ['bofa-sebastian','bofa-brett','barclays','dkb-credit','dkb','n26-sebastian','n26-brett','capital-one']
df_raw = pd.concat([read_transaction_data(name) for name in names]).set_index('transaction_date')
df_raw = add_categories(df_raw)

# Remove Transactions to ignore
df_raw = df_raw.loc[df_raw['cat'] != 'ignore', :]

# Limit to 2 years
df = df_raw[df_raw.index >= '2021-09-01'].sort_index()

df.loc[df['cat'].isna(),:].head()


# In[87]:


# Monthly Expenses


# In[88]:


# df.loc[df['description'].str.contains('Lohn'),'budget_month'] = df.loc[df['description'].str.contains('Lohn'),:].index + datetime.timedelta(weeks=4)
# df = df.reset_index().sort_values(['transaction_date', 'amount'],ascending=[True, False]).set_index('transaction_date')
# df['budget_month'] = df['budget_month'].ffill()

df['budget_month'] = df.index + pd.offsets.MonthEnd()


# In[89]:


# Unassigned Categories


# In[90]:


df_raw.loc[(df_raw['cat'].isna()) & (~df_raw['label'].isna()),'label'].unique()


# In[91]:


# Overview


# In[92]:


df.reset_index().groupby('budget_month').agg({'transaction_date': [np.max,np.min]})


# In[93]:


# df_grouped = df.groupby([pd.Grouper(key='budget_month', freq='M')]).sum().reset_index()
# budget_diff = df_grouped.merge(budget_grouped, on=['budget_month'])
# budget_diff['diff'] = budget_diff['amount'] - budget_diff['budget_value']
# budget_diff.plot(x='budget_month', y=['diff'], kind='bar')


# In[94]:


budget_exp = budget.loc[budget['type'] == 'expense',:].groupby([pd.Grouper(key='budget_month', freq='M')]).sum().reset_index()
df_exp = df.loc[~(df['description'].str.contains('Lohn') | df['description'].str.contains('LOHN')),:].groupby([pd.Grouper(key='budget_month', freq='M')]).sum().reset_index()
budget_exp_diff = df_exp.merge(budget_exp, on=['budget_month'], how='outer')
budget_exp_diff.plot(x='budget_month',y=['budget_value','amount'])


# In[95]:


# Only Expense 
budget_exp_diff['diff'] = budget_exp_diff['amount'] - budget_exp_diff['budget_value']
budget_exp_diff.plot(x='budget_month', y=['diff'], kind='bar')


# In[96]:


# # Current Accounts Values
# df_grouped = df.groupby([pd.Grouper(key='budget_month', freq='M')]).sum().reset_index()
# df_grouped.plot(x='budget_month', y='amount', kind='bar')


# In[97]:


# # Split by Sources
# df_grouped = df.groupby([pd.Grouper(key='budget_month', freq='M'),'name']).sum().reset_index()
# df_grouped.plot(x='budget_month', y='amount', kind='bar', color='name')


# In[98]:


# Actuals vs. Budget
    
def breakdown(month,year):
    actual_vs_budget = budget.merge(df,on=['budget_month','cat'],how='outer')
    actual_vs_budget_by_cat = actual_vs_budget.groupby([pd.Grouper(key='budget_month', freq='M'),'cat'], dropna=False).agg({'budget_value': np.sum, 'amount': np.sum}).reset_index()
    actual_vs_budget_by_cat['diff'] = actual_vs_budget_by_cat['amount'] - actual_vs_budget_by_cat['budget_value']
    return actual_vs_budget_by_cat.loc[(actual_vs_budget_by_cat['budget_month'].dt.month == month) & (actual_vs_budget_by_cat['budget_month'].dt.year == year),:]


# In[100]:


_ = interact(breakdown, month=budget['budget_month'].dt.month.unique(), year=budget['budget_month'].dt.year.unique())


# In[101]:


interact(show_cat, cat=list(cats.keys()), month=budget['budget_month'].dt.month.unique(), year=budget['budget_month'].dt.year.unique());


# In[102]:


df_d_by_name = df.groupby(['transaction_date','name']).sum().reset_index().pivot_table(index=['transaction_date'],columns=['name'],values=['amount']).fillna(0)
df_d_by_name.columns = [col[1] for col in df_d_by_name.columns]

# Reindex 
dti = pd.date_range(start=df_d_by_name.index.min(), end=df_d_by_name.index.max(), freq="D")
df_d_by_name = df_d_by_name.reindex(dti).fillna(0)

df_d_by_name.plot()


# In[103]:


df_total = df_raw.pivot_table(index=['transaction_date'],columns=['name'],aggfunc={'total': np.mean}).ffill()
df_total.sum(axis=1).plot()


# In[104]:


df_total


# In[106]:


df_total.droplevel(0,axis=1).plot()


# In[ ]:





# In[ ]:




