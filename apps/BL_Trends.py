import os
from datetime import datetime
import urllib.parse

import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
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
            sql = 'SELECT * FROM li_stat_licensetrends_bl'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['ISSUEDATE'])
        elif dataset == 'last_ddl_time':
            sql = 'SELECT SCN_TO_TIMESTAMP(MAX(ora_rowscn)) last_ddl_time FROM LI_STAT_LICENSETRENDS_BL'
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def get_last_ddl_time():
    last_ddl_time = dataframe('last_ddl_time')
    return last_ddl_time['LAST_DDL_TIME'].iloc[0]

def get_licenses():
    df_ind = dataframe('df_ind')
    df_ind['ISSUEDATE'] = pd.to_datetime(df_ind['ISSUEDATE'])
    # Select only Jan-June 2017 and 2018, then group them by year, job and licensetype
    licenses = (df_ind.loc[(df_ind['ISSUEDATE'] >= '2017-01-01') 
                         & (df_ind['ISSUEDATE'] < '2017-07-01')]
                      .append(df_ind.loc[(df_ind['ISSUEDATE'] >= '2018-01-01') 
                           & (df_ind['ISSUEDATE'] < '2018-07-01')])
                      .assign(ISSUEDATE=lambda x: x['ISSUEDATE'].dt.strftime('%Y')))
    return licenses

def get_license_volumes(licenses):
    license_volumes = licenses.groupby(['ISSUEDATE', 'JOBTYPE', 'LICENSETYPE'], as_index=False)['COUNTJOBS'].sum()
    return license_volumes

def get_license_payments(licenses):
    license_payments = licenses.groupby(['ISSUEDATE', 'JOBTYPE', 'LICENSETYPE'], as_index=False)['TOTALAMOUNT'].sum()
    return license_payments

def clean_and_pivot_data(license_volumes, jobtype, values):
    '''Split the data into renewal_volumes and applications_volumes and pivot it into a logical state,
       calculate the percent change from 2017-2018 and rename the columns to be easier to read'''
    license_volumes = (license_volumes.loc[license_volumes['JOBTYPE'] == jobtype]
                                      .pivot(index='LICENSETYPE', columns='ISSUEDATE', values=values)
                                      .reset_index()
                                      .assign(PercentChange=lambda x:round((x['2018'] - x['2017']) /  x['2017'] * 100, 1))
                                      .sort_values(by='PercentChange'))
    return license_volumes
    
def select_top_ten_absolute_changes(license_volumes, filteramount):
    license_volumes = (license_volumes.loc[(license_volumes['2017'] > filteramount) 
                                         | (license_volumes['2018'] > filteramount)]
                                      .assign(AbsolutePercentChange=lambda x:abs(x['PercentChange']))
                                      .sort_values(by='2018', ascending=False)
                                      .dropna().head(10)
                                      .sort_values(by='AbsolutePercentChange', ascending=False)
                                      .drop(columns=['AbsolutePercentChange']))
    return license_volumes
    
def get_top_ten_volumes_by_job_type(license_volumes, jobtype):
    volumes = clean_and_pivot_data(license_volumes, jobtype=jobtype, values='COUNTJOBS')
    license_column_names = {'LICENSETYPE': 'License Type', 
                            '2017': '2017 License Volume', 
                            '2018': '2018 License Volume', 
                            'PercentChange': '% Change'}
    top_ten_volumes = (select_top_ten_absolute_changes(volumes, 100)
                            .rename(columns=license_column_names))
    return top_ten_volumes

def get_top_ten_payments_by_job_type(license_payments, jobtype):
    payments = clean_and_pivot_data(license_payments, jobtype=jobtype, values='TOTALAMOUNT')
    payment_column_names = {'LICENSETYPE': 'License Type', 
                            '2017': '2017 License Payments', 
                            '2018': '2018 License Payments', 
                            'PercentChange': '% Change'}
    # Helper functions for rounding payments up the the nearest dollar
    rounding_functions = {'2017': lambda x: round(x['2017']),
                          '2018': lambda x: round(x['2018'])}
    top_ten_payments = (select_top_ten_absolute_changes(payments, 10000)
                            .assign(**rounding_functions)
                            .rename(columns=payment_column_names))
    return top_ten_payments

def update_layout():
    last_ddl_time = get_last_ddl_time()
    licenses = get_licenses()
    license_volumes = get_license_volumes(licenses)
    license_payments = get_license_payments(licenses)
    top_ten_renewal_volumes = get_top_ten_volumes_by_job_type(license_volumes, 'Renewal')
    top_ten_applications_volumes = get_top_ten_volumes_by_job_type(license_volumes, 'Application')
    top_ten_renewal_payments = get_top_ten_payments_by_job_type(license_payments, 'Renewal')
    top_ten_applications_payments = get_top_ten_payments_by_job_type(license_payments, 'Application')

    return html.Div([
                    html.H1('Business License Trends', style={'text-align': 'center'}),
                    html.H2('From January - July', style={'text-align': 'center'}),
                    html.P(f"Data last updated {last_ddl_time}", style = {'text-align': 'center', 'margin-bottom': '75px'}),
                    html.Div([
                        html.H3('Top Significant Changes in Application Volumes [1]'),
                        table.DataTable(
                            rows=top_ten_applications_volumes.to_dict('records'),
                            columns=top_ten_applications_volumes.columns,
                            sortable=True,
                            editable=False,
                            id='slide3BL-table1'
                        )
                    ], style={'text-align': 'center', 'width': '70%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'}),
                    html.Div([
                    html.H3('Top Significant Changes in Renewal Volumes [1]'),
                        table.DataTable(
                            rows=top_ten_renewal_volumes.to_dict('records'),
                            columns=top_ten_renewal_volumes.columns,
                            sortable=True,
                            editable=False,
                            id='slide3BL-table2'
                        )
                    ], style={'text-align': 'center', 'width': '70%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'}),
                    html.Div([
                        html.H3('Top Significant Changes in Application Payments [2]'),
                        table.DataTable(
                            rows=top_ten_applications_payments.to_dict('records'),
                            columns=top_ten_applications_payments.columns,
                            sortable=True,
                            editable=False,
                            id='slide3BL-table3'
                        )
                    ], style={'text-align': 'center', 'width': '70%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'}),
                    html.Div([
                    html.H3('Top Significant Changes in Renewal Payments [2]'),
                        table.DataTable(
                            rows=top_ten_renewal_payments.to_dict('records'),
                            columns=top_ten_renewal_payments.columns,
                            sortable=True,
                            editable=False,
                            id='slide3BL-table4'
                        )
                    ], style={'text-align': 'center', 'width': '70%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'}),
                    html.P('[1] License Types with less than 100 licenses issued in a year were not included.', style={'text-align': 'center'}),
                    html.P('[2] License Types generating less than $10000 in a year were not included.', style={'text-align': 'center'}),
                    html.Details([
                        html.Summary('Query Description'),
                        html.Div([
                            html.P(
                                'Approved business licenses issued Jan-July 2018 vs Jan-July 2017. Grouped by job type '
                                '(application or renewal) and license type.'
                                'Filtered to only include the 10 with the largest % change.'),
                            html.P(
                                '[1] License Types with less than 100 licenses issued in a year were not included.'),
                            html.P(
                                'Fees paid (aka revenue collected) from all business licenses issued Jan-July 2018 vs '
                                'Jan-July 2017. Grouped by job type (application or renewal) and license type. '
                                'Filtered to only include the 10 with the largest % change.'),
                            html.P(
                                '[2] License Types generating less than $10000 in a year were not included.')
                        ])
                    ])
                ])

layout = update_layout
