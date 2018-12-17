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
    
print('slide3BL.py')

with con() as con:
    sql = 'SELECT * FROM li_stat_licensetrends_bl'
    df = pd.read_sql_query(sql=sql, con=con, parse_dates=['ISSUEDATE'])
    sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_LICENSETRENDS_BL'"
    last_ddl_time = pd.read_sql_query(sql=sql, con=con)

# Select only Jan-June 2017 and 2018, then group them by year, job and licensetype
licenses = (df.loc[(df['ISSUEDATE'] >= '2017-01-01') 
                 & (df['ISSUEDATE'] < '2017-07-01')]
              .append(df.loc[(df['ISSUEDATE'] >= '2018-01-01') 
                           & (df['ISSUEDATE'] < '2018-07-01')])
              .assign(ISSUEDATE=lambda x: x['ISSUEDATE'].dt.strftime('%Y')))

license_volumes = licenses.groupby(['ISSUEDATE', 'JOBTYPE', 'LICENSETYPE'], as_index=False)['COUNTJOBS'].sum()

# Split the data into renewal_volumes and applications_volumes and pivot it into a logical state,
# calculate the percent change from 2017-2018 and rename the columns to be easier to read
def clean_and_pivot_data(license_volumes, jobtype, values):
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

# Create column names dictionaries for easy renaming later on.
# These make the tables a lot easier to read and understand.
license_column_names = {'LICENSETYPE': 'License Type', 
                        '2017': '2017 License Volume', 
                        '2018': '2018 License Volume', 
                        'PercentChange': '% Change'}

payment_column_names = {'LICENSETYPE': 'License Type', 
                        '2017': '2017 License Payments', 
                        '2018': '2018 License Payments', 
                        'PercentChange': '% Change'}

renewal_volumes = clean_and_pivot_data(license_volumes, jobtype='Renewal', values='COUNTJOBS')
                                
applications_volumes = clean_and_pivot_data(license_volumes, jobtype='Application', values='COUNTJOBS')

top_ten_renewal_volumes = (select_top_ten_absolute_changes(renewal_volumes, 100)
                          .rename(columns=license_column_names))

top_ten_applications_volumes = (select_top_ten_absolute_changes(applications_volumes, 100)
                               .rename(columns=license_column_names))

license_payments = licenses.groupby(['ISSUEDATE', 'JOBTYPE', 'LICENSETYPE'], as_index=False)['TOTALAMOUNT'].sum()

renewal_payments = clean_and_pivot_data(license_payments, jobtype='Renewal', values='TOTALAMOUNT')
                                
applications_payments = clean_and_pivot_data(license_payments, jobtype='Application', values='TOTALAMOUNT')

# Helper functions for rounding payments up the the nearest dollar
rounding_functions = {'2017': lambda x: round(x['2017']),
                      '2018': lambda x: round(x['2018'])}

top_ten_renewal_payments = (select_top_ten_absolute_changes(renewal_payments, 10000)
                           .assign(**rounding_functions)
                           .rename(columns=payment_column_names))

top_ten_applications_payments = (select_top_ten_absolute_changes(applications_payments, 10000)
                                .assign(**rounding_functions)
                                .rename(columns=payment_column_names))

layout = html.Div([
                html.H1('Business License Trends', style={'text-align': 'center'}),
                html.H2('From January - July', style={'text-align': 'center'}),
                html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center', 'margin-bottom': '75px'}),
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