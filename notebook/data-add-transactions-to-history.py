#!/usr/bin/env python
# coding: utf-8
# %%
from budget.functions import add_transaction_data, read_transaction_data

# %%
# add_transaction_data('../data/cln/bofa-sebastian.csv', 'bofa-sebastian')
add_transaction_data('../data/cln/bofa-brett.csv', 'bofa-brett')
add_transaction_data('../data/cln/barclays.xlsx', 'barclays')
add_transaction_data('../data/cln/dkb-credit.csv', 'dkb-credit')
add_transaction_data('../data/cln/dkb.csv', 'dkb')
add_transaction_data('../data/cln/n26-sebastian.csv', 'n26-sebastian')
add_transaction_data('../data/cln/n26-brett.csv', 'n26-brett')
# add_transaction_data('../data/cln/postbank.csv', 'postbank')
add_transaction_data('../data/cln/capital-one.csv', 'capital-one')


# %%
# label_data('bofa-brett')
# label_data('barclays')
# label_data('dkb-credit')
# label_data('dkb')
# label_data('n26-sebastian')
# label_data('n26-brett')
# label_data('postbank')
# label_data('capital-one')

