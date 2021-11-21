#!/usr/bin/env python
# coding: utf-8

# In[900]:


import numpy as np
import pandas as pd
from ipywidgets import interact
import glob
import os
import re
import datetime


# In[901]:


pd.options.plotting.backend = "plotly"


def add_categories(df, src_col='label', trgt_col='cat'):
    cats = {
        'income': ['income'],
        'shopping': ['fashion','shopping'],
        'groceries': ['groceries'],
        'home': ['home','rent', 'utilities','electricity','heat','water','gas','gez','cell','dsl','internet'],
        'subscription': ['subscription','amazon prime','prime','medium','medium subscription','patreon','spotify','skype'],
        'work': ['work','office','aws','google storage','domain','class','classes'],
        'debt': ['debt','kfw','bildungsfond'],
        'travel': ['travel','lodging','vacation rental','flight'],
        'transport': ['transport','bvg','swapfiets'],
        'savings': ['savings','crypto'],
        'fitness': ['fitness','fitx','gym'],
        'fun': ['fun','drinks','food','lunch','coffee'],
        'health+beauty': ['haircut','pharmacy','drugstore'],
        'gift': ['gift'],
        'other': ['other','fee','cash'],
        'transfer': ['transfer']
    }

    categories = {val: key for key, vals in cats.items() for val in vals}
    df[trgt_col] = df[src_col].str.lower().map(categories)
    return df


# In[902]:


budget = pd.read_csv('../data/budget/budget_cln.csv', parse_dates=['budget_month'])
budget = add_categories(budget)

budget_grouped = budget.groupby([pd.Grouper(key='budget_month', freq='M')]).sum().reset_index()

budget_grouped.plot(x='budget_month',y='budget_value')


# In[903]:


names = ['bofa-sebastian','bofa-brett','barclays','dkb-credit','dkb','n26-sebastian','n26-brett']
df_raw = pd.concat([read_transaction_data(name) for name in names]).set_index('transaction_date')
df_raw = add_categories(df_raw)

# Remove Transactions to ignore
df_raw = df_raw.loc[df_raw['label'] != 'ignore', :]

# Limit to 2 years
df = df_raw[df_raw.index >= '2021-09-01'].sort_index()

df.loc[df['cat'].isna(),:].head()


# In[904]:


df.loc[df['description'].str.contains('Lohn'),'budget_month'] = df.loc[df['description'].str.contains('Lohn'),:].index + datetime.timedelta(weeks=4)
df = df.reset_index().sort_values(['transaction_date', 'amount'],ascending=[True, False]).set_index('transaction_date')
df['budget_month'] = df['budget_month'].ffill()


# In[905]:


# Overview


# In[906]:


df.reset_index().groupby('budget_month').agg({'transaction_date': [np.max,np.min]})


# In[907]:


df_grouped = df.groupby([pd.Grouper(key='budget_month', freq='M')]).sum().reset_index()
budget_diff = df_grouped.merge(budget_grouped, on=['budget_month'])
budget_diff['diff'] = budget_diff['amount'] - budget_diff['budget_value']
budget_diff.plot(x='budget_month', y=['diff'], kind='bar')


# In[908]:


# Current Accounts Values
df_grouped = df.groupby([pd.Grouper(key='budget_month', freq='M')]).sum().reset_index()
df_grouped.plot(x='budget_month', y='amount', kind='bar')


# In[909]:


# Split by Sources
df_grouped = df.groupby([pd.Grouper(key='budget_month', freq='M'),'name']).sum().reset_index()
df_grouped.plot(x='budget_month', y='amount', kind='bar', color='name')


# In[910]:


# Actuals vs. Budget
    
def breakdown(month,year):
    actual_vs_budget = budget.merge(df,on=['budget_month','cat'],how='outer')
    actual_vs_budget_by_cat = actual_vs_budget.groupby([pd.Grouper(key='budget_month', freq='M'),'cat']).sum().reset_index()
    return actual_vs_budget_by_cat.loc[(actual_vs_budget_by_cat['budget_month'].dt.month == month) & (actual_vs_budget_by_cat['budget_month'].dt.year == year),:]


# In[911]:


_ = interact(breakdown, month=budget['budget_month'].dt.month.unique(), year=budget['budget_month'].dt.year.unique())


# In[912]:


def show_cat(cat, month, year):
    return df.loc[(df['cat'] == cat) & (df['budget_month'].dt.month == month) & (df['budget_month'].dt.year == year),:]


# In[913]:


interact(show_cat, cat=list(cats.keys()), month=budget['budget_month'].dt.month.unique(), year=budget['budget_month'].dt.year.unique());


# In[914]:


transfers = df.loc[(df['cat'] == 'transfer') & (df['budget_month'].dt.month == 10) & (df['budget_month'].dt.year == 2021),:]
transfers.iloc[2:,:]


# In[915]:


df.loc[df.index > '2021-10-17',:]


# In[916]:


df_d_by_name = df.groupby(['transaction_date','name']).sum().reset_index().pivot_table(index=['transaction_date'],columns=['name'],values=['amount']).fillna(0)
df_d_by_name.columns = [col[1] for col in df_d_by_name.columns]

# Reindex 
dti = pd.date_range(start=df_d_by_name.index.min(), end=df_d_by_name.index.max(), freq="D")
df_d_by_name = df_d_by_name.reindex(dti).fillna(0)

df_d_by_name.plot()


# In[917]:


df_total = df_raw.pivot_table(index=['transaction_date'],columns=['name'])['total'].ffill()
df_total.sum(axis=1).plot()

