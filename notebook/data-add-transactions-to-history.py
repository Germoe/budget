#!/usr/bin/env python
# coding: utf-8

# In[128]:

from budget.functions import add_transaction_data, read_transaction_data

# In[131]:


# add_transaction_data('../data/cln/bofa-sebastian.csv', 'bofa-sebastian')
add_transaction_data('../data/cln/bofa-brett.csv', 'bofa-brett')
add_transaction_data('../data/cln/barclays.xlsx', 'barclays')
add_transaction_data('../data/cln/dkb-credit.csv', 'dkb-credit')
add_transaction_data('../data/cln/dkb.csv', 'dkb')
add_transaction_data('../data/cln/n26-sebastian.csv', 'n26-sebastian')
add_transaction_data('../data/cln/n26-brett.csv', 'n26-brett')
# add_transaction_data('../data/cln/postbank.csv', 'postbank')
add_transaction_data('../data/cln/capital-one.csv', 'capital-one')


# In[156]:


# label_data('bofa-brett')
# label_data('barclays')
# label_data('dkb-credit')
# label_data('dkb')
# label_data('n26-sebastian')
# label_data('n26-brett')
# label_data('postbank')
# label_data('capital-one')


# In[157]:


df = read_transaction_data('dkb-credit')
# df.loc[df['label'].isna(),:]


# In[9]:


# for idx, row in targets.iterrows():
#     cond = (targets['transaction_date'] == row['transaction_date']) &\
#                (targets['amount'] == row['amount']) & \
#                (targets['description'] == row['description']) & \
#                (targets['name'] == row['name'])
#     relabel(targets.loc[cond,:],'fun')


# In[10]:


# df_cln = read_transaction_data('n26-brett')
# at_total = ('2021-11-17', 158.58)
# end_bal = df_cln.loc[df_cln['transaction_date'] > at_total[0],['transaction_date','amount']].sort_values('transaction_date', ascending=True)
# end_bal['total'] = at_total[1] + end_bal['amount'].shift(0).cumsum()
# end_bal = end_bal.iat[-1, 2]
# # end_bal

# df_cln['total'] = end_bal - df_cln['amount'].shift(1).cumsum()
# df_cln['total'].iat[0] = end_bal


# In[11]:


# df_cln


# In[ ]:





# %%
