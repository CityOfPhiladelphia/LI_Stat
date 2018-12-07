import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
import urllib.parse
import datetime

from app import app, con

print('slide4_BL.py')

with con() as con:
    sql = 'SELECT * FROM li_stat_submittalvolumes_bl'
    df = (pd.read_sql_query(sql=sql, con=con, parse_dates=['ISSUEDATE'])
          .sort_values(by='ISSUEDATE'))

df_chart_createdbytype = (df.copy(deep=True)
                            .groupby(['ISSUEDATE', 'CREATEDBYTYPE'])['JOBNUMBERCOUNT']
                            .sum()
                            .reset_index()
                            .sort_values(by='ISSUEDATE')
                            .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b %Y')))

df_chart_createdbytype_all = (df.copy(deep=True)
                                .groupby(['ISSUEDATE'])['JOBNUMBERCOUNT']
                                .sum()
                                .reset_index()
                                .sort_values(by='ISSUEDATE')
                                .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b %Y')))

df_chart_jobtype = (df.copy(deep=True)
                      .groupby(['ISSUEDATE', 'JOBTYPE'])['JOBNUMBERCOUNT']
                      .sum()
                      .reset_index()
                      .sort_values(by='ISSUEDATE')
                      .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b %Y')))

df_chart_jobtype_all = (df.copy(deep=True)
                          .groupby(['ISSUEDATE'])['JOBNUMBERCOUNT']
                          .sum()
                          .reset_index()
                          .sort_values(by='ISSUEDATE')
                          .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b %Y')))

df_created_by_type = (df.copy(deep=True)
                        .loc[df['ISSUEDATE'] >= '2018-01-01']
                        .groupby(['CREATEDBYTYPE'])['JOBNUMBERCOUNT']
                        .sum())

df_job_type = (df.copy(deep=True)
                 .loc[df['ISSUEDATE'] >= '2018-01-01']
                 .groupby(['JOBTYPE'])['JOBNUMBERCOUNT']
                 .sum())

df_table = (df.copy(deep=True)
              .groupby(['ISSUEDATE', 'LICENSETYPE', 'CREATEDBYTYPE'])['JOBNUMBERCOUNT']
              .sum()
              .reset_index()
              .sort_values(by='ISSUEDATE')
              .assign(ISSUEDATE=lambda x: x['ISSUEDATE'].dt.strftime('%b %Y'))
              .rename(columns={'ISSUEDATE': 'Issue Date', 'LICENSETYPE': 'License Type', 'CREATEDBYTYPE': 'Submittal Type', 'JOBNUMBERCOUNT': 'Jobs Completed'}))

all_licenses = df.copy(deep=True)
rentals = df.loc[(df['LICENSETYPE'] == 'Rental') & (df['CREATEDBYTYPE'] == 'Online') & (df['ISSUEDATE'] >= '2018-01-01')] 
vacant_properties = df.loc[(df['LICENSETYPE'].str.contains('Vacant')) & (df['CREATEDBYTYPE'] == 'Online') & (df['ISSUEDATE'] >= '2018-01-01')]
food = df.loc[(df['LICENSETYPE'].str.contains('Food')) & (df['CREATEDBYTYPE'] == 'Online') & (df['ISSUEDATE'] >= '2018-01-01')]
cals = df.loc[(df['LICENSETYPE'].str.contains('Activity')) & (df['CREATEDBYTYPE'] == 'Online') & (df['ISSUEDATE'] >= '2018-01-01')]

def percent_renewals(df):
    count_new = df.loc[df['JOBTYPE'] == 'Application']['JOBNUMBERCOUNT'].sum()
    count_renewals = df.loc[df['JOBTYPE'] == 'Renewal']['JOBNUMBERCOUNT'].sum()
    return round(count_renewals / (count_new + count_renewals) * 100, 1)

df_table_2 = pd.DataFrame(data={
    'License Type': ['All Licenses', 'Rentals', 'Vacant Properties', 'Food'],
    '% Online Renewals': [percent_renewals(license_type) for license_type in [all_licenses, rentals, vacant_properties, food]]
})

count_2016 = df.loc[(df['ISSUEDATE'] >= '2016-01-01') & (df['ISSUEDATE'] < '2016-08-01')]['JOBNUMBERCOUNT'].sum()
count_2017 = df.loc[(df['ISSUEDATE'] >= '2017-01-01') & (df['ISSUEDATE'] < '2017-08-01')]['JOBNUMBERCOUNT'].sum()
count_2018 = df.loc[(df['ISSUEDATE'] >= '2018-01-01')  & (df['ISSUEDATE'] < '2018-08-01')]['JOBNUMBERCOUNT'].sum()
count_all = count_2016 + count_2017 + count_2018

df_table_3 = pd.DataFrame(data={
    '2016': [count_2016],
    '2017': [count_2017],
    '2018': [count_2018],
    'All': [count_all]
})

layout = html.Div([
    html.H1('Submittal Type', style={'text-align': 'center'}),
    html.H2('(Business Licenses)', style={'text-align': 'center', 'margin-bottom': '20px'}
    ),
    html.Div([
        html.Div([
            dcc.Graph(id='slide4BL-createdbytype-chart',
                figure=go.Figure(
                    data=[
                        go.Scatter(
                            x=df_chart_createdbytype_all['ISSUEDATE'],
                            y=df_chart_createdbytype_all['JOBNUMBERCOUNT'],
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
                            y=df_chart_createdbytype.loc[df_chart_createdbytype['CREATEDBYTYPE'] == 'Online']['JOBNUMBERCOUNT'],
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
                            y=df_chart_createdbytype.loc[df_chart_createdbytype['CREATEDBYTYPE'] == 'Staff']['JOBNUMBERCOUNT'],
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
                        title=('Jobs Completed by Submittal Type'),
                        yaxis=dict(title='Jobs Completed')
                    )
                )
            ),
        ], className='eight columns'),
        html.Div([
            dcc.Graph(id='slide4BL-createdbytype-piechart',
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
            dcc.Graph(id='slide4BL-jobtype-chart',
                figure=go.Figure(
                    data=[
                        go.Scatter(
                            x=df_chart_jobtype_all['ISSUEDATE'],
                            y=df_chart_jobtype_all['JOBNUMBERCOUNT'],
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
                            y=df_chart_jobtype.loc[df_chart_jobtype['JOBTYPE'] == 'Renewal']['JOBNUMBERCOUNT'],
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
                            y=df_chart_jobtype.loc[df_chart_jobtype['JOBTYPE'] == 'Application']['JOBNUMBERCOUNT'],
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
                        title=('Jobs Completed by Job Type'),
                        yaxis=dict(title='Jobs Completed')
                    )
                )
            )
        ], className='eight columns'),
        html.Div([
            dcc.Graph(id='slide4BL-jobtype-piechart',
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
        html.H3('Jobs Completed from January to July', style={'text-align': 'center'}),
        html.Div([
            dt.DataTable(
                rows=df_table_3.to_dict('records'),
                columns=df_table_3.columns,
                editable=False,
                id='slide4-BL-table-3'
            )
        ], style={'text-align': 'center'})
    ], style={'width': '40%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'}),
    html.Div([
        html.H3('Percent of Online Transactions Which Were Renewals (2018)', style={'text-align': 'center'}),
        html.Div([
            dt.DataTable(
                rows=df_table_2.to_dict('records'),
                columns=df_table_2.columns,
                editable=False,
                id='slide4-BL-table-2'
            )
        ], style={'text-align': 'center'})
    ], style={'width': '40%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'}),
    html.Div([
        html.H3('Jobs Completed by Month, License Type, and Submittal Type', style={'text-align': 'center'}),
        html.Div([
            html.Div([
                dt.DataTable(
                    rows=df_table.to_dict('records'),
                    columns=df_table.columns,
                    filterable=True,
                    sortable=True,
                    editable=False,
                    id='slide4-BL-table-1'
                )
            ], style={'text-align': 'center'})
        ]),
        html.Div([
            html.A(
                'Download Data',
                id='Slide4BL-download-link',
                download='Slide4BL.csv',
                href='',
                target='_blank',
            )
        ], style={'text-align': 'right'}),
    ], style={'width': '65%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'})
])