import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import numpy as np
import urllib.parse

from app import app, con
    

testing_mode = True
print('slide2Permits.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('test_data/Slide1Permits.csv', parse_dates=['ISSUEDATE'])

else:
    with con() as con:
        with open(r'queries/permits/Slide1_MonthlyPermitsSubmittedwithPaidFees.sql') as sql:
            df = pd.read_sql_query(sql=sql.read(), con=con, parse_dates=['ISSUEDATE'])

df['PERMITDESCRIPTION'] = df['PERMITDESCRIPTION'].map(lambda x: x.replace(" PERMIT", ""))
df['PERMITDESCRIPTION'] = df['PERMITDESCRIPTION'].str.lower()
df['PERMITDESCRIPTION'] = df['PERMITDESCRIPTION'].str.title()

# Select only Jun-Nov 2016 and 2017, then group them by year and permit type
permits = (df.loc[(df['ISSUEDATE'] >= '2016-06-01')
                 & (df['ISSUEDATE'] < '2016-12-01')]
              .append(df.loc[(df['ISSUEDATE'] >= '2017-06-01')
                           & (df['ISSUEDATE'] < '2017-12-01')])
              .assign(ISSUEDATE=lambda x: x['ISSUEDATE'].dt.strftime('%Y')))

permit_volumes = permits.groupby(['ISSUEDATE', 'PERMITDESCRIPTION'], as_index=False)['COUNTPERMITS'].sum()

# Split the data into renewal_volumes and applications_volumes and pivot it into a logical state,
# calculate the percent change from 2016-2017 and rename the columns to be easier to read
def clean_and_pivot_data(permit_volumes, values):
    permit_volumes = (permit_volumes.pivot(index='PERMITDESCRIPTION', columns='ISSUEDATE', values=values)
                                    .reset_index()
                                    .assign(PercentChange=lambda x: round((x['2017'] - x['2016']) /  x['2016'] * 100, 1))
                                    .sort_values(by='PercentChange'))
    return permit_volumes
    
def select_top_ten_absolute_changes(permit_volumes, filteramount):
    permit_volumes = (permit_volumes.loc[(permit_volumes['2016'] > filteramount)
                                         | (permit_volumes['2017'] > filteramount)]
                                      .assign(AbsolutePercentChange=lambda x: abs(x['PercentChange']))
                                      .sort_values(by='2017', ascending=False)
                                      .dropna().head(10)
                                      .sort_values(by='AbsolutePercentChange', ascending=False)
                                      .drop(columns=['AbsolutePercentChange']))
    return permit_volumes

# Create column names dictionaries for easy renaming later on.
# These make the tables a lot easier to read and understand.
permit_column_names = {'PERMITDESCRIPTION': 'Permit Type',
                        '2016': '2016 Permits Issued',
                        '2017': '2017 Permits Issued',
                        'PercentChange': '% Change'}

payment_column_names = {'PERMITDESCRIPTION': 'Permit Type',
                        '2016': '2016 Fees Paid ($)',
                        '2017': '2017 Fees Paid ($)',
                        'PercentChange': '% Change'}

permit_percent_changes = clean_and_pivot_data(permit_volumes, values='COUNTPERMITS')

top_ten_volumes = (select_top_ten_absolute_changes(permit_percent_changes, 100)
                          .rename(columns=permit_column_names))

permit_payments = permits.groupby(['ISSUEDATE', 'PERMITDESCRIPTION'], as_index=False)['TOTALFEESPAID'].sum()

permit_payments_pivoted = clean_and_pivot_data(permit_payments, values='TOTALFEESPAID')
                                

# Helper functions for rounding payments up the the nearest dollar
rounding_functions = {'2016': lambda x: round(x['2016']),
                      '2017': lambda x: round(x['2017'])}

top_ten_payments = (select_top_ten_absolute_changes(permit_payments_pivoted, 10000)
                           .assign(**rounding_functions)
                           .rename(columns=payment_column_names))

top_ten_volumes['2016 Permits Issued'] = top_ten_volumes['2016 Permits Issued'].map('{:,.0f}'.format)
top_ten_volumes['2017 Permits Issued'] = top_ten_volumes['2017 Permits Issued'].map('{:,.0f}'.format)
top_ten_volumes['% Change'] = top_ten_volumes['% Change'].map('{:,.1f}'.format)

top_ten_payments['2016 Fees Paid ($)'] = top_ten_payments['2016 Fees Paid ($)'].map('{:,.0f}'.format)
top_ten_payments['2017 Fees Paid ($)'] = top_ten_payments['2017 Fees Paid ($)'].map('{:,.0f}'.format)
top_ten_payments['% Change'] = top_ten_payments['% Change'].map('{:,.1f}'.format)

layout = html.Div([
                html.H1('Permit Trends', style={'text-align': 'center'}),
                html.H2('June - November', style={'text-align': 'center'}),
                html.Div([
                    html.H3('Top Significant Changes in Permits Issued [1]'),
                    table.DataTable(
                        rows=top_ten_volumes.to_dict('records'),
                        columns=top_ten_volumes.columns,
                        sortable=True,
                        editable=False,
                        id='slide3BL-table1'
                    )
                ], style={'text-align': 'center', 'width': '65%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'},
                   id='slide2permits_volume_changes_table'),
                html.Div([
                    html.H3('Top Significant Changes in Permit Payments [2]'),
                    table.DataTable(
                        rows=top_ten_payments.to_dict('records'),
                        columns=top_ten_payments.columns,
                        sortable=True,
                        editable=False,
                        id='slide3BL-table3'
                    )
                ], style={'text-align': 'center', 'width': '65%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'},
                   id='slide2permits_payment_changes_table'),
                html.P('[1] Permit Types with less than 100 permits issued in a year were not included.', style={'text-align': 'center'}),
                html.P('[2] Permit Types generating less than $10,000 in a year were not included.', style={'text-align': 'center'})
            ])