import os
import datetime
import urllib.parse

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output

from app import app, cache, cache_timeout


print(os.path.basename(__file__))

@cache_timeout
@cache.memoize()
def query_data(dataset):
    from app import con
    with con() as con:
        if dataset == 'df_ind':
            sql = 'SELECT * FROM li_stat_submittalvolumes_tl'
            df = (pd.read_sql_query(sql=sql, con=con, parse_dates=['ISSUEDATE'])
                .sort_values(by='ISSUEDATE'))
        elif dataset == 'last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_SUBMITTALVOLUMES_TL'"
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def get_last_ddl_time():
    last_ddl_time = dataframe('last_ddl_time')
    return last_ddl_time['LAST_DDL_TIME'].iloc[0]

def get_df_ind():
    df_ind = dataframe('df_ind')
    df_ind['ISSUEDATE'] = pd.to_datetime(df_ind['ISSUEDATE'])
    return df_ind

def get_df_chart_createdby_type(df_ind):
    df_chart_createdbytype = (df_ind.groupby(['ISSUEDATE', 'CREATEDBYTYPE'])['LICENSENUMBERCOUNT']
                                    .sum()
                                    .reset_index()
                                    .sort_values(by='ISSUEDATE')
                                    .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b-%Y')))
    return df_chart_createdbytype

def get_df_chart_createdbytype_all(df_ind):
    df_chart_createdbytype_all = (df_ind.groupby(['ISSUEDATE'])['LICENSENUMBERCOUNT']
                                        .sum()
                                        .reset_index()
                                        .sort_values(by='ISSUEDATE')
                                        .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b-%Y')))
    return df_chart_createdbytype_all

def get_df_chart_jobtype(df_ind):
    df_chart_jobtype = (df_ind.groupby(['ISSUEDATE', 'JOBTYPE'])['LICENSENUMBERCOUNT']
                              .sum()
                              .reset_index()
                              .sort_values(by='ISSUEDATE')
                              .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b-%Y')))
    return df_chart_jobtype


def get_df_chart_jobtype_all(df_ind):
    df_chart_jobtype_all = (df_ind.groupby(['ISSUEDATE'])['LICENSENUMBERCOUNT']
                                  .sum()
                                  .reset_index()
                                  .sort_values(by='ISSUEDATE')
                                  .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b-%Y')))
    return df_chart_jobtype_all

def get_df_created_by_type(df_ind):
    df_created_by_type = (df_ind.loc[df_ind['ISSUEDATE'] >= '2018-01-01']
                                .groupby(['CREATEDBYTYPE'])['LICENSENUMBERCOUNT']
                                .sum())
    return df_created_by_type

def get_df_job_type(df_ind):
    df_job_type = (df_ind.loc[df_ind['ISSUEDATE'] >= '2018-01-01']
                        .groupby(['JOBTYPE'])['LICENSENUMBERCOUNT']
                        .sum())
    return df_job_type

def get_df_table(df_ind):
    df_table = (df_ind.groupby(['ISSUEDATE', 'LICENSETYPE', 'CREATEDBYTYPE'])['LICENSENUMBERCOUNT']
                    .sum()
                    .reset_index()
                    .sort_values(by='ISSUEDATE')
                    .assign(ISSUEDATE=lambda x: x['ISSUEDATE'].dt.strftime('%b-%Y'))
                    .rename(columns={'ISSUEDATE': 'Issue Date', 'LICENSETYPE': 'License Type', 'CREATEDBYTYPE': 'Submittal Type', 'LICENSENUMBERCOUNT': 'Licenses Issued'}))
    return df_table

def get_licenses_by_type(df_ind, licensetype):
    licenses_by_type = df_ind.loc[(df_ind['LICENSETYPE'].str.contains(licensetype)) & (df_ind['CREATEDBYTYPE'] == 'Online') & (df_ind['ISSUEDATE'] >= '2018-01-01')] 
    return licenses_by_type

def percent_renewals(df):
    '''Helper function for get_df_table_2.'''
    count_new = df.loc[df['JOBTYPE'] == 'Application']['LICENSENUMBERCOUNT'].sum()
    count_renewals = df.loc[df['JOBTYPE'] == 'Renewal']['LICENSENUMBERCOUNT'].sum()
    return round(count_renewals / (count_new + count_renewals) * 100, 1)

def get_df_table_2(df_ind):
    all_licenses = df_ind
    contractors = get_licenses_by_type(df_ind, 'Contractor')
    plumbing = get_licenses_by_type(df_ind, 'Plumber')
    electrical = get_licenses_by_type(df_ind, 'Electrical')

    df_table_2 = pd.DataFrame(data={
        'License Type': ['All Licenses', 'Contractor', 'Plumbing', 'Electrical'],
        '% Online Renewals': [percent_renewals(license_type) for license_type in [all_licenses, contractors, plumbing, electrical]]
    })
    return df_table_2

def get_license_count_by_year(df_ind, year):
    license_count_by_year = df_ind.loc[(df_ind['ISSUEDATE'] >= f'{year}-01-01') & (df_ind['ISSUEDATE'] < f'{year}-08-01')]['LICENSENUMBERCOUNT'].sum()
    return license_count_by_year

def get_df_table_3(df_ind):
    count_2017 = get_license_count_by_year(df_ind, 2017)
    count_2018 = get_license_count_by_year(df_ind, 2018)
    count_all = count_2017 + count_2018
    df_table_3 = pd.DataFrame(data={
        '2017': [count_2017],
        '2018': [count_2018],
        'All': [count_all]
    })
    return df_table_3

def update_layout():
    last_ddl_time = get_last_ddl_time()
    df_ind = get_df_ind()
    df_chart_createdbytype = get_df_chart_createdby_type(df_ind)
    df_chart_createdbytype_all = get_df_chart_createdbytype_all(df_ind)
    df_chart_jobtype = get_df_chart_jobtype(df_ind)
    df_chart_jobtype_all = get_df_chart_jobtype_all(df_ind)
    df_created_by_type = get_df_created_by_type(df_ind)
    df_job_type = get_df_job_type(df_ind)
    df_table = get_df_table(df_ind)
    df_table_2 = get_df_table_2(df_ind)
    df_table_3 = get_df_table_3(df_ind)

    return html.Div([
        html.H1('Submittal Type', style={'text-align': 'center'}),
        html.H2('(Trade Licenses)', style={'text-align': 'center', 'margin-bottom': '20px'}),
        html.P(f"Data last updated {last_ddl_time}", style = {'text-align': 'center', 'margin-bottom': '50px'}),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='slide4TL-createdbytype-chart',
                    config={
                        'displayModeBar': False
                    },
                    figure=go.Figure(
                        data=[
                            go.Scatter(
                                x=df_chart_createdbytype_all['ISSUEDATE'],
                                y=df_chart_createdbytype_all['LICENSENUMBERCOUNT'],
                                name='All',
                                mode='lines',
                                text=df_chart_createdbytype_all['DateText'],
                                hoverinfo='y',
                                line=dict(
                                    shape='spline',
                                    color='#000000'
                                )
                            ),
                            go.Scatter(
                                x=df_chart_createdbytype.loc[df_chart_createdbytype['CREATEDBYTYPE'] == 'Online']['ISSUEDATE'],
                                y=df_chart_createdbytype.loc[df_chart_createdbytype['CREATEDBYTYPE'] == 'Online']['LICENSENUMBERCOUNT'],
                                name='Online',
                                mode='lines',
                                text=df_chart_createdbytype.loc[df_chart_createdbytype['CREATEDBYTYPE'] == 'Online']['DateText'],
                                hoverinfo='y',
                                line=dict(
                                    shape='spline',
                                    color='#399327'
                                )
                            ),
                            go.Scatter(
                                x=df_chart_createdbytype.loc[df_chart_createdbytype['CREATEDBYTYPE'] == 'Staff']['ISSUEDATE'],
                                y=df_chart_createdbytype.loc[df_chart_createdbytype['CREATEDBYTYPE'] == 'Staff']['LICENSENUMBERCOUNT'],
                                name='Staff',
                                mode='lines',
                                text=df_chart_createdbytype.loc[df_chart_createdbytype['CREATEDBYTYPE'] == 'Staff']['DateText'],
                                hoverinfo='text+y',
                                line=dict(
                                    shape='spline',
                                    color='#642692'
                                )
                            )
                        ],
                        layout=go.Layout(
                            title=('Licenses Issued by Submittal Type'),
                            yaxis=dict(title='Licenses Issued')
                        )
                    )
                ),
            ], className='eight columns'),
            html.Div([
                dcc.Graph(id='slide4TL-createdbytype-piechart',
                    figure=go.Figure(
                        data=[
                            go.Pie(
                                labels=df_created_by_type.index,
                                values=df_created_by_type.values,
                                hoverinfo='label+value+percent', 
                                hole=0.4,
                                textfont=dict(color='#FFFFFF'),
                                marker=dict(colors=['#399327', '#642692'], 
                                line=dict(color='#000000', width=2)),
                            )
                        ],
                        layout=go.Layout(title=('2018 Submittal Type Breakdown'))
                    )
                )
            ], className='four columns') 
        ], className='dashrow'),
        html.Div([
            html.Div([
                dcc.Graph(id='slide4TL-jobtype-chart',
                    figure=go.Figure(
                        data=[
                            go.Scatter(
                                x=df_chart_jobtype_all['ISSUEDATE'],
                                y=df_chart_jobtype_all['LICENSENUMBERCOUNT'],
                                name='All',
                                mode='lines',
                                text=df_chart_jobtype_all['DateText'],
                                hoverinfo='y',
                                line=dict(
                                    shape='spline',
                                    color='#000000'
                                )
                            ),
                            go.Scatter(
                                x=df_chart_jobtype.loc[df_chart_jobtype['JOBTYPE'] == 'Renewal']['ISSUEDATE'],
                                y=df_chart_jobtype.loc[df_chart_jobtype['JOBTYPE'] == 'Renewal']['LICENSENUMBERCOUNT'],
                                name='Renewal',
                                mode='lines',
                                text=df_chart_jobtype.loc[df_chart_jobtype['JOBTYPE'] == 'Renewal']['DateText'],
                                hoverinfo='y',
                                line=dict(
                                    shape='spline',
                                    color='#4153f4'
                                )
                            ),
                            go.Scatter(
                                x=df_chart_jobtype.loc[df_chart_jobtype['JOBTYPE'] == 'Application']['ISSUEDATE'],
                                y=df_chart_jobtype.loc[df_chart_jobtype['JOBTYPE'] == 'Application']['LICENSENUMBERCOUNT'],
                                name='Application',
                                mode='lines',
                                text=df_chart_jobtype.loc[df_chart_jobtype['JOBTYPE'] == 'Application']['DateText'],
                                hoverinfo='text+y',
                                line=dict(
                                    shape='spline',
                                    color='#f4424b'
                                )
                            )
                        ],
                        layout=go.Layout(
                            title=('Licenses Issued by Job Type'),
                            yaxis=dict(title='Licenses Issued')
                        )
                    )
                )
            ], className='eight columns'),
            html.Div([
                dcc.Graph(id='slide4TL-jobtype-piechart',
                    figure=go.Figure(
                        data=[
                            go.Pie(
                                labels=df_job_type.index,
                                values=df_job_type.values,
                                hoverinfo='label+value+percent',
                                hole=0.4, 
                                textfont=dict(color='#FFFFFF'),
                                marker=dict(colors=['#f4424b', '#4153f4'], 
                                    line=dict(color='#000000', width=2))
                            )
                        ],
                        layout=go.Layout(title=('2018 Job Type Breakdown'))
                    )
                )
            ], className='four columns')
        ], className='dashrow'),
        html.Div([
            html.H3('Licenses Issued from January to July', style={'text-align': 'center'}),
            html.Div([
                dt.DataTable(
                    rows=df_table_3.to_dict('records'),
                    columns=df_table_3.columns,
                    editable=False,
                    id='slide4-BL-table-3'
                )
            ], style={'text-align': 'center'})
        ], style={'width': '25%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'}),
        html.Div([
            html.H3('Percent of Online Transactions Which Were Renewals (2018)', style={'text-align': 'center'}),
            html.Div([
                dt.DataTable(
                    rows=df_table_2.to_dict('records'),
                    columns=df_table_2.columns,
                    editable=False,
                    id='slide4-TL-table-2'
                )
            ], style={'text-align': 'center'})
        ], style={'width': '40%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'}),
        html.Div([
            html.H3('Licenses Issued by Month, License Type, and Submittal Type', style={'text-align': 'center'}),
            html.Div([
                html.Div([
                    dt.DataTable(
                        rows=df_table.to_dict('records'),
                        columns=df_table.columns,
                        filterable=True,
                        sortable=True,
                        editable=False,
                        id='slide4-TL-table-1'
                    )
                ], style={'text-align': 'center'})
            ]),
            html.Div([
                html.A(
                    'Download Data',
                    id='Slide4TL-download-link',
                    download='Slide4TL.csv',
                    href='',
                    target='_blank',
                )
            ], style={'text-align': 'right'}),
        ], style={'width': '65%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'}),
        html.Details([
            html.Summary('Query Description'),
            html.Div([
                html.P(
                    'Approved trade licenses issued since 2016 and how their amend/renew and application jobs were submitted (online, '
                    'revenue, or staff).'),
                html.P(
                    'We determine how a job was submitted (online, revenue, or staff) based on the username who created it:'),
                html.Ul(children=[
                    html.Li('Online: If the username contains a number or equals "PPG User"'),
                    html.Li('Revenue: If the username equals "POSSE system power user"'),
                    html.Li('Staff: If the username doesn\'t meet one of the other two conditions')
                ])
            ])
        ])
    ])

layout = update_layout