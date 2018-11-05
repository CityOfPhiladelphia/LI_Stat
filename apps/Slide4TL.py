import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
import urllib.parse
import datetime

from app import app, con


testing_mode = True
print('slide4_TL.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('test_data/Slide4_TL.csv', parse_dates=['ISSUEDATE'])
    
else:
    with con() as con:
        with open(r'queries/licenses/slide4_submittal_volumes_TL.sql') as sql:
            df = (pd.read_sql(sql=sql.read(), con=con, parse_dates=['ISSUEDATE'])
                    .sort_values(by='ISSUEDATE'))

df_chart_createdbytype = (df.copy(deep=True)
                            .groupby(['ISSUEDATE', 'CREATEDBYTYPE'])['LICENSENUMBERCOUNT']
                            .sum()
                            .reset_index()
                            .sort_values(by='ISSUEDATE')
                            .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b-%Y')))

df_chart_createdbytype_all = (df.copy(deep=True)
                                .groupby(['ISSUEDATE'])['LICENSENUMBERCOUNT']
                                .sum()
                                .reset_index()
                                .sort_values(by='ISSUEDATE')
                                .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b-%Y')))

df_chart_jobtype = (df.copy(deep=True)
                      .groupby(['ISSUEDATE', 'JOBTYPE'])['LICENSENUMBERCOUNT']
                      .sum()
                      .reset_index()
                      .sort_values(by='ISSUEDATE')
                      .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b-%Y')))

df_chart_jobtype_all = (df.copy(deep=True)
                          .groupby(['ISSUEDATE'])['LICENSENUMBERCOUNT']
                          .sum()
                          .reset_index()
                          .sort_values(by='ISSUEDATE')
                          .assign(DateText=lambda x: x['ISSUEDATE'].dt.strftime('%b-%Y')))

df_created_by_type = (df.copy(deep=True)
                        .loc[df['ISSUEDATE'] >= '2018-01-01']
                        .groupby(['CREATEDBYTYPE'])['LICENSENUMBERCOUNT']
                        .sum())

df_job_type = (df.copy(deep=True)
                 .loc[df['ISSUEDATE'] >= '2018-01-01']
                 .groupby(['JOBTYPE'])['LICENSENUMBERCOUNT']
                 .sum())

df_table = (df.copy(deep=True)
              .groupby(['ISSUEDATE', 'LICENSETYPE', 'CREATEDBYTYPE'])['LICENSENUMBERCOUNT']
              .sum()
              .reset_index()
              .sort_values(by='ISSUEDATE')
              .assign(ISSUEDATE=lambda x: x['ISSUEDATE'].dt.strftime('%b-%Y'))
              .rename(columns={'ISSUEDATE': 'Issue Date', 'LICENSETYPE': 'License Type', 'CREATEDBYTYPE': 'Submittal Type', 'LICENSENUMBERCOUNT': 'Number of Licenses Issued'}))

all_licenses = df.copy(deep=True)
contractors = df.loc[(df['LICENSETYPE'] == 'Contractor') & (df['CREATEDBYTYPE'] == 'Online') & (df['ISSUEDATE'] >= '2018-01-01')] 
plumbing = df.loc[(df['LICENSETYPE'].str.contains('Plumber')) & (df['CREATEDBYTYPE'] == 'Online') & (df['ISSUEDATE'] >= '2018-01-01')]
electrical = df.loc[(df['LICENSETYPE'].str.contains('Electrical')) & (df['CREATEDBYTYPE'] == 'Online') & (df['ISSUEDATE'] >= '2018-01-01')]

def percent_renewals(df):
    count_new = df.loc[df['JOBTYPE'] == 'Application']['LICENSENUMBERCOUNT'].sum()
    count_renewals = df.loc[df['JOBTYPE'] == 'Renewal']['LICENSENUMBERCOUNT'].sum()
    return round(count_renewals / (count_new + count_renewals) * 100, 1)

df_table_2 = pd.DataFrame(data={
    'License Type': ['All Licenses', 'Contractor', 'Plumbing', 'Electrical'],
    '% Online Renewals': [percent_renewals(license_type) for license_type in [all_licenses, contractors, plumbing, electrical]]
})

count_2017 = df.loc[(df['ISSUEDATE'] >= '2017-01-01') & (df['ISSUEDATE'] < '2018-01-01')]['LICENSENUMBERCOUNT'].sum()
count_2018 = df.loc[(df['ISSUEDATE'] >= '2018-01-01')]['LICENSENUMBERCOUNT'].sum()
count_all = df['LICENSENUMBERCOUNT'].sum()

df_table_3 = pd.DataFrame(data={
    '2017': [count_2017],
    '2018': [count_2018],
    'All': [count_all]
})

layout = html.Div([
    html.H1('Trade Licenses Mode of Submittal', style={'text-align': 'center'}),
    html.Div([
        html.Div([
            dcc.Graph(id='slide4TL-createdbytype-chart',
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
                        title=('Submittal Type Activity By Month'),
                        yaxis=dict(title='Number of Licenses Issued')
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
                        title=('Application and Renewal Activity By Month'),
                        yaxis=dict(title='Number of Licenses Issued')
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
        html.H3('Volume of Licenses Issued from January to July', style={'text-align': 'center'}),
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
        html.H3('No. of Monthly Online and Staff Transactions Per License Type', style={'text-align': 'center'}),
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
    ], style={'width': '55%', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-top': '45px', 'margin-bottom': '45px'})
])

# @app.callback(
#     Output('Slide4TL-download-link', 'href'),
#     [Input('field-dropdown', 'value')])
# def update_download_link(user_selection):
#     df = get_data_object(user_selection)
#     csv_string = df.to_csv(index=False, encoding='utf-8')
#     csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
#     return csv_string

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=5001)