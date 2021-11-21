#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd

def print_file(path, show=10):
    with open(path, "r", encoding='utf-8', errors="ignore") as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if i >= show:
                break
            print(i + 1, line)


# In[2]:


f_path = '../data/budget/budget.csv'


# In[3]:


print_file(f_path)


# In[6]:


df = pd.read_csv(f_path, skiprows=7)
df.columns = [col.lower() for col in df.columns]

df['type'] = df['type'].str.lower()

df = df.loc[df['type'].isin(['income','expense'])]
df = df.melt(id_vars=['type','name','label'], var_name='budget_month', value_name='budget_value')

df['budget_value'] = pd.to_numeric(df['budget_value'].str.replace(',',''), downcast='float')
df['budget_month'] = pd.to_datetime(df['budget_month'], format="%b %Y")

df.loc[(df['type'] == 'expense') & (df['budget_value'] > 0),'budget_value'] = -df.loc[(df['type'] == 'expense') & (df['budget_value'] > 0),'budget_value']
df.to_csv('../data/budget/budget_cln.csv', index=False)

