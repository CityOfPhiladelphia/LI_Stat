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
print('slide3BL.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('Slide3_BL.csv', parse_dates=['ISSUEDATE'])

else:
    with con() as con:
        with open(r'queries/licenses/FinalQueries_SQL/slide3_license_trends_BL.sql') as sql:
            df = pd.read_sql_query(sql=sql.read(), con=con, parse_dates=['ISSUEDATE'])

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
                                      .sort_values(by='AbsolutePercentChange', ascending=False)
                                      .drop(columns=['AbsolutePercentChange'])
                                      .dropna().head(10))
    return license_volumes

renewal_volumes = clean_and_pivot_data(license_volumes, jobtype='Renewal', values='COUNTJOBS')
                                
applications_volumes = clean_and_pivot_data(license_volumes, jobtype='Application', values='COUNTJOBS')

top_ten_renewal_volumes = (select_top_ten_absolute_changes(renewal_volumes, 100)
                   .rename(columns={'LICENSETYPE': 'License Type', 
                                    '2017': '2017 License Volume', 
                                    '2018': '2018 License Volume', 
                                    'PercentChange': '% Change'}))

top_ten_applications_volumes = (select_top_ten_absolute_changes(applications_volumes, 100)
                       .rename(columns={'LICENSETYPE': 'License Type', 
                                        '2017': '2017 License Volume', 
                                        '2018': '2018 License Volume', 
                                        'PercentChange': '% Change'}))

license_payments = licenses.groupby(['ISSUEDATE', 'JOBTYPE', 'LICENSETYPE'], as_index=False)['TOTALAMOUNT'].sum()

renewal_payments = clean_and_pivot_data(license_payments, jobtype='Renewal', values='TOTALAMOUNT')
                                
applications_payments = clean_and_pivot_data(license_payments, jobtype='Application', values='TOTALAMOUNT')

top_ten_renewal_payments = (select_top_ten_absolute_changes(renewal_payments, 10000)
                   .rename(columns={'LICENSETYPE': 'License Type', 
                                    '2017': '2017 License Payments', 
                                    '2018': '2018 License Payments', 
                                    'PercentChange': '% Change'}))

top_ten_applications_payments = (select_top_ten_absolute_changes(applications_payments, 10000)
                       .rename(columns={'LICENSETYPE': 'License Type', 
                                        '2017': '2017 License Payments', 
                                        '2018': '2018 License Payments', 
                                        'PercentChange': '% Change'}))

layout = html.Div([
                html.H1('License Trends', style={'text-align': 'center'}),
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
                html.P('[2] License Types generating less than $10000 in a year were not included.', style={'text-align': 'center'})
            ])