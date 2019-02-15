import os
import urllib.parse
from datetime import datetime

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
import numpy as np

from app import app, cache, cache_timeout


print(os.path.basename(__file__))

@cache_timeout
@cache.memoize()
def query_data(dataset):
    from app import con
    with con() as con:
        if dataset == 'df_ind':
            sql = 'SELECT * FROM li_stat_permitsfees'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['ISSUEDATE'])
            df['PERMITDESCRIPTION'] = df['PERMITDESCRIPTION'].map(lambda x: x.replace(" PERMIT", ""))
            df['PERMITDESCRIPTION'] = df['PERMITDESCRIPTION'].str.lower()
            df['PERMITDESCRIPTION'] = df['PERMITDESCRIPTION'].str.title()
        elif dataset == 'last_ddl_time':
            sql = 'SELECT SCN_TO_TIMESTAMP(MAX(ora_rowscn)) last_ddl_time FROM LI_STAT_PERMITSFEES'
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def get_last_ddl_time():
    last_ddl_time = dataframe('last_ddl_time')
    return last_ddl_time['LAST_DDL_TIME'].iloc[0]

def get_permits():
    df_ind = dataframe('df_ind')
    df_ind['ISSUEDATE'] = pd.to_datetime(df_ind['ISSUEDATE'])
    # Select only Jun-Nov 2016 and 2017
    permits = (df_ind.loc[(df_ind['ISSUEDATE'] >= datetime(2016, 6, 1))
                        & (df_ind['ISSUEDATE'] < datetime(2016, 12, 1))]
                .append(df_ind.loc[(df_ind['ISSUEDATE'] >= datetime(2017, 6, 1))
                     & (df_ind['ISSUEDATE'] < datetime(2017, 12, 1))])
                .assign(ISSUEDATE=lambda x: x['ISSUEDATE'].dt.strftime('%Y')))
    return permits

def get_permit_volumes(permits):
    permit_volumes = permits.groupby(['ISSUEDATE', 'PERMITDESCRIPTION'], as_index=False)['COUNTPERMITS'].sum()
    return permit_volumes

def get_permit_payments(permits):
    permit_payments = permits.groupby(['ISSUEDATE', 'PERMITDESCRIPTION'], as_index=False)['TOTALFEESPAID'].sum()
    return permit_payments

def clean_and_pivot_data(permit_volumes, values):
    ''' Split the data into renewal_volumes and applications_volumes and pivot it into a logical state,
        calculate the percent change from 2016-2017 and rename the columns to be easier to read'''
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

def get_top_ten_volumes(permit_volumes):
    permit_percent_changes = clean_and_pivot_data(permit_volumes, values='COUNTPERMITS')
    permit_column_names = {'PERMITDESCRIPTION': 'Permit Type',
                        '2016': '2016 Permits Issued',
                        '2017': '2017 Permits Issued',
                        'PercentChange': '% Change'}
    top_ten_volumes = (select_top_ten_absolute_changes(permit_percent_changes, 100)
                          .rename(columns=permit_column_names))
    top_ten_volumes['2016 Permits Issued'] = top_ten_volumes['2016 Permits Issued'].map('{:,.0f}'.format)
    top_ten_volumes['2017 Permits Issued'] = top_ten_volumes['2017 Permits Issued'].map('{:,.0f}'.format)
    top_ten_volumes['% Change'] = top_ten_volumes['% Change'].map('{:,.1f}'.format)
    return top_ten_volumes

def get_top_ten_payments(permit_payments):
    permit_payments_pivoted = clean_and_pivot_data(permit_payments, values='TOTALFEESPAID')
    payment_column_names = {'PERMITDESCRIPTION': 'Permit Type',
                            '2016': '2016 Fees Paid ($)',
                            '2017': '2017 Fees Paid ($)',
                            'PercentChange': '% Change'}
    # Helper functions for rounding payments up the the nearest dollar
    rounding_functions = {'2016': lambda x: round(x['2016']),
                          '2017': lambda x: round(x['2017'])}
    top_ten_payments = (select_top_ten_absolute_changes(permit_payments_pivoted, 10000)
                           .assign(**rounding_functions)
                           .rename(columns=payment_column_names))
    top_ten_payments['2016 Fees Paid ($)'] = top_ten_payments['2016 Fees Paid ($)'].map('{:,.0f}'.format)
    top_ten_payments['2017 Fees Paid ($)'] = top_ten_payments['2017 Fees Paid ($)'].map('{:,.0f}'.format)
    top_ten_payments['% Change'] = top_ten_payments['% Change'].map('{:,.1f}'.format)
    return top_ten_payments

def update_layout():
    last_ddl_time = get_last_ddl_time()
    permits = get_permits()
    permit_volumes = get_permit_volumes(permits)
    permit_payments = get_permit_payments(permits)
    top_ten_volumes = get_top_ten_volumes(permit_volumes)
    top_ten_payments = get_top_ten_payments(permit_payments)

    return html.Div([
                html.H1('Permit Trends', style={'text-align': 'center'}),
                html.H2('June - November', style={'text-align': 'center'}),
                html.P(f"Data last updated {last_ddl_time}", style = {'text-align': 'center', 'margin-bottom': '75px'}),
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
                html.P('[2] Permit Types generating less than $10,000 in a year were not included.', style={'text-align': 'center'}),
                html.Details([
                    html.Summary('Query Description'),
                    html.Div([
                        html.P(
                            'Permits (with paid fees) issued Jun-Nov 2017 vs Jun-Nov 2016. Grouped by Permit Type.'
                            'Filtered to only include the 10 with the largest % change.'),
                        html.P(
                            '[1] Permit Types with less than 100 permits issued in a year were not included.'),
                        html.P(
                            'Fees paid from all permits issued Jun-Nov 2017 vs Jun-Nov 2016. Grouped by Permit Type. '
                            'Filtered to only include the 10 with the largest % change.'),
                        html.P(
                            '[2] Permit Types generating less than $10,000 in a year were not included.')
                    ])
                ])
            ])

layout = update_layout
