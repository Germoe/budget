#!/usr/bin/env python
# coding: utf-8

# In[128]:


import pandas as pd
import re
from budget.functions import print_file, combine_debit_credit, prepare_data


# In[129]:


# TODOs:
# Deal with Currency Encodings
# Deal with Excel Sheets
# Deal with Different Currencies


# In[130]:


# In[131]:


# Read in DKB Konto
f_path = "../data/raw/dkb.csv"
skiprows = 6
delimiter = ';'
name = 'DKB'
currency = 'EUR'
cent_delimiter = ','
dayfirst = True
at_total = ('2021-11-21', 554.26)
mapping = {
    'transaction_date': 'Buchungstag',
    'beneficiary': 'Auftraggeber / Begünstigter',
    'amount': 'Betrag (EUR)',
    'description': 'Verwendungszweck'
}


# In[132]:


print_file(f_path)


# In[133]:


df = pd.read_csv(f_path, delimiter=delimiter, skiprows=skiprows, encoding= 'unicode_escape')
df.head()


# In[134]:


df_cln = prepare_data(df, mapping, dayfirst=dayfirst, currency=currency, name=name, cent_delimiter=cent_delimiter, at_total=at_total)
df_cln.dtypes


# In[135]:


df_cln.head()


# In[136]:


df_cln.to_csv(f_path.replace('raw','cln'), index=False)


# In[179]:


# Read in DKB Kreditkarte
f_path = "../data/raw/dkb-credit.csv"
skiprows = 6
delimiter = ';'
name = 'DKB Credit'
currency = 'EUR'
dayfirst = True
at_total = ('2021-12-02', -479.03)
cent_delimiter = ','
mapping = {
    'transaction_date': 'Belegdatum',
    'amount': 'Betrag (EUR)',
    'description': 'Beschreibung'
}


# In[180]:


print_file(f_path)


# In[181]:


df = pd.read_csv(f_path, delimiter=delimiter, skiprows=skiprows, encoding= 'unicode_escape')
df.head()


# In[182]:


df_cln = prepare_data(df, mapping, dayfirst=dayfirst, currency=currency, name=name, cent_delimiter=cent_delimiter, at_total=at_total)
df_cln.dtypes


# In[183]:


df_cln.head()


# In[184]:


df_cln.to_csv(f_path.replace('raw','cln'), index=False)


# In[148]:


# Read in N26
f_path = "../data/raw/n26-sebastian.csv"
skiprows = 0
delimiter = ','
name = 'N26 Sebastian'
currency = 'EUR'
dayfirst = False
at_total = ('2021-11-21', 23.02)
cent_delimiter = '.'
mapping = {
    'transaction_date': 'Date',
    'beneficiary': 'Payee',
    'amount': 'Amount (EUR)',
    'description': 'Payment reference'
}


# In[149]:


print_file(f_path)


# In[150]:


df = pd.read_csv(f_path, delimiter=delimiter, skiprows=skiprows, encoding= 'unicode_escape')
df.tail()


# In[151]:


df_cln = prepare_data(df, mapping, dayfirst=dayfirst, currency=currency, name=name, cent_delimiter=cent_delimiter, at_total=at_total)
df_cln.dtypes


# In[152]:


df_cln.head()


# In[153]:


df_cln.to_csv(f_path.replace('raw','cln'), index=False)


# In[154]:


# Read in N26
f_path = "../data/raw/n26-brett.csv"
skiprows = 0
delimiter = ','
name = 'N26 Brett'
currency = 'EUR'
dayfirst = False
cent_delimiter = '.'
at_total = ('2021-11-21', 128.50)
mapping = {
    'transaction_date': 'Date',
    'beneficiary': 'Payee',
    'amount': 'Amount (EUR)',
    'description': 'Payment reference'
}


# In[155]:


print_file(f_path)


# In[156]:


df = pd.read_csv(f_path, delimiter=delimiter, skiprows=skiprows, encoding= 'unicode_escape')
df.tail(50)


# In[157]:


df_cln = prepare_data(df, mapping, dayfirst=dayfirst, currency=currency, name=name, cent_delimiter=cent_delimiter, at_total=at_total)
df_cln.dtypes


# In[158]:


df_cln.head()


# In[159]:


df_cln.to_csv(f_path.replace('raw','cln'), index=False)


# In[29]:


# Read in Postbank
f_path = "../data/raw/postbank.csv"
skiprows = 9
delimiter = ';'
name = 'Postbank'
currency = 'EUR'
cent_delimiter = ','
dayfirst = True
at_total = ('2021-11-21', 20064.39)
mapping = {
    'transaction_date': 'Buchungsdatum',
    'beneficiary': 'Empf',
    'amount': 'Betrag',
    'description': 'Buchungsdetails'
}


# In[30]:


print_file(f_path, show=15)


# In[31]:


df = pd.read_csv(f_path, delimiter=delimiter, skiprows=skiprows, encoding='unicode_escape')
df.columns = [re.match(r'(([A-Z]|[a-z])+)',col).group() for col in df.columns]
df.head()


# In[32]:


df_cln = prepare_data(df, mapping, dayfirst=dayfirst, currency=currency, name=name, cent_delimiter=cent_delimiter, at_total=at_total)
df_cln.dtypes


# In[33]:


df_cln.to_csv(f_path.replace('raw','cln'), index=False)


# In[34]:


# Read in Bank Of America
f_path = "../data/raw/bofa-sebastian.csv"
skiprows = 6
delimiter = ','
name = 'BofA Sebastian'
currency = 'USD'
cent_delimiter = '.'
dayfirst = False
at_total = ('11-21-2021', 1581.70)
mapping = {
    'transaction_date': 'Date',
    'amount': 'Amount',
    'description': 'Description'
}


# In[35]:


print_file(f_path)


# In[36]:


df = pd.read_csv(f_path, delimiter=delimiter, skiprows=skiprows, encoding= 'unicode_escape')
df.head()


# In[417]:


df = df.iloc[1:,:]


# In[418]:


df_cln = prepare_data(df, mapping, dayfirst=dayfirst, currency=currency, name=name, cent_delimiter=cent_delimiter, at_total=at_total)
df_cln.dtypes


# In[419]:


df_cln.to_csv(f_path.replace('raw','cln'), index=False)


# In[160]:


# Read in Bank Of America
f_path = "../data/raw/bofa-brett.csv"
skiprows = 6
delimiter = ','
name = 'BofA Brett'
currency = 'USD'
cent_delimiter = '.'
dayfirst = False
at_total = ('11-21-2021', 118.77)
mapping = {
    'transaction_date': 'Date',
    'amount': 'Amount',
    'description': 'Description'
}


# In[161]:


print_file(f_path)


# In[162]:


df = pd.read_csv(f_path, delimiter=delimiter, skiprows=skiprows, encoding= 'unicode_escape')
df.head()


# In[163]:


df = df.iloc[1:,:]


# In[164]:


df_cln = prepare_data(df, mapping, dayfirst=dayfirst, currency=currency, name=name, cent_delimiter=cent_delimiter, at_total=at_total)
df_cln.dtypes


# In[165]:


df_cln.head()


# In[166]:


df_cln.to_csv(f_path.replace('raw','cln'), index=False)


# In[167]:


# Read in Barclays
f_path = "../data/raw/barclays.xlsx"
sheet_name = 0
name = 'Barclays'
currency = 'EUR'
cent_delimiter = ','
dayfirst = True
at_total = ('2021-11-17', -5746.52)
mapping = {
    'transaction_date': 'Buchungsdatum',
    'amount': 'Betrag',
    'description': 'Beschreibung'
}


# In[168]:


df = pd.read_excel(f_path, sheet_name=sheet_name, skiprows=12, engine="openpyxl")
df.head()


# In[169]:


df_cln = prepare_data(df, mapping, dayfirst=dayfirst, currency=currency, name=name, cent_delimiter=cent_delimiter, at_total=at_total)
df_cln.dtypes


# In[170]:


df_cln.head()


# In[171]:


df_cln.to_csv(f_path.replace('raw','cln'), index=False)


# In[172]:


# Read in Capital One Konto
f_path = "../data/raw/capital-one.csv"
skiprows = 0
delimiter = ','
name = 'capital-one'
currency = 'USD'
cent_delimiter = '.'
dayfirst = False
at_total = ('2021-11-28', -617.63)
mapping = {
    'transaction_date': 'Transaction Date',
    'description': 'Description'
}
use_cols = [col for col in mapping.values()]
use_names = [name for name in mapping.keys()]

amount_map = {
    '+': 'Credit',
    '-': 'Debit'
}
if len(amount_map) > 0:
    use_cols = use_cols + ['amount']
    use_names = use_names + ['amount']


# In[173]:


print_file(f_path)


# In[174]:


df = pd.read_csv(f_path, delimiter=delimiter, skiprows=skiprows, encoding= 'unicode_escape')
df.head()


# In[175]:


if len(amount_map) > 0:
    df = combine_debit_credit(df, amount_map, mapping)


# In[176]:


df_cln = prepare_data(df, mapping, dayfirst=dayfirst, currency=currency, name=name, cent_delimiter=cent_delimiter, at_total=at_total)
df_cln.dtypes


# In[177]:


df_cln.head()


# In[178]:


df_cln.to_csv(f_path.replace('raw','cln'), index=False)


# In[ ]:





# %%
