import os
from datetime import datetime, date
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
            sql = 'SELECT * FROM li_stat_licensevolumes_bl'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['ISSUEDATE'])
            df.sort_values(by='ISSUEDATE', inplace=True)
            df = (df.rename(columns={'ISSUEDATE': 'Issue Date', 'LICENSETYPE': 'License Type', 'COUNTJOBS': 'Number of Licenses Issued'})
            .assign(DateText=lambda x: x['Issue Date'].dt.strftime('%b %Y')))
        elif dataset == 'last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_LICENSEVOLUMES_BL'"
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def update_total_license_volume(selected_start, selected_end, selected_jobtype, selected_licensetype):
    df_selected = dataframe('df_ind')
    df_selected['Issue Date'] = pd.to_datetime(df_selected['Issue Date']).map(lambda dt: dt.date())

    start_date = datetime.strptime(selected_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(selected_end, "%Y-%m-%d").date()

    if selected_jobtype != "All":
        df_selected = df_selected[(df_selected['JOBTYPE']==selected_jobtype)]
    if selected_licensetype != "All":
        df_selected = df_selected[(df_selected['License Type']==selected_licensetype)]

    df_selected = df_selected.loc[(df_selected['Issue Date']>=start_date)&(df_selected['Issue Date']<=end_date)]
    total_license_volume = df_selected['Number of Licenses Issued'].sum()
    return '{:,.0f}'.format(total_license_volume)

def update_counts_graph_data(selected_start, selected_end, selected_jobtype, selected_licensetype):
    df_selected = dataframe('df_ind')
    df_selected['Issue Date'] = pd.to_datetime(df_selected['Issue Date']).map(lambda dt: dt.date())

    start_date = datetime.strptime(selected_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(selected_end, "%Y-%m-%d").date()

    issue_dates = df_selected['Issue Date'].unique()
    print(issue_dates.dtype)
    selected_issue_dates = issue_dates[(issue_dates >= start_date) & (issue_dates <= end_date)]

    if selected_jobtype != "All":
        df_selected = df_selected[(df_selected['JOBTYPE']==selected_jobtype)]
    if selected_licensetype != "All":
        df_selected = df_selected[(df_selected['License Type']==selected_licensetype)]

    df_selected = (df_selected.loc[(df_selected['Issue Date']>=start_date)&(df_selected['Issue Date']<=end_date)]
                              .groupby(by=['Issue Date', 'DateText'])['Number of Licenses Issued']
                              .sum()
                              .reset_index())
    for month in selected_issue_dates:
        if month not in df_selected['Issue Date'].values:
            df_missing_month = pd.DataFrame([[month, month.strftime('%b %Y'), 0]], columns=['Issue Date', 'DateText', 'Number of Licenses Issued'])
            df_selected = df_selected.append(df_missing_month, ignore_index=True)
    df_selected['Issue Date'] = pd.Categorical(df_selected['Issue Date'], issue_dates)
    return df_selected.sort_values(by='Issue Date')

def update_counts_table_data(selected_start, selected_end, selected_jobtype, selected_licensetype):
    df_selected = dataframe('df_ind')
    df_selected['Issue Date'] = pd.to_datetime(df_selected['Issue Date']).map(lambda dt: dt.date())

    start_date = datetime.strptime(selected_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(selected_end, "%Y-%m-%d").date()

    if selected_jobtype != "All":
        df_selected = df_selected[(df_selected['JOBTYPE']==selected_jobtype)]
    if selected_licensetype != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_licensetype)]

    df_selected = (df_selected.loc[(df_selected['Issue Date']>=start_date)&(df_selected['Issue Date']<=end_date)]
                              .groupby(by=['Issue Date', 'License Type'])['Number of Licenses Issued']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Issue Date','License Type']))
    df_selected['Issue Date'] = df_selected['Issue Date'].apply(lambda x: datetime.strftime(x, '%b %Y'))
    return df_selected

def update_layout():
    df = dataframe('df_ind')
    df['Issue Date'] = pd.to_datetime(df['Issue Date']).map(lambda dt: dt.date())
    last_ddl_time = dataframe('last_ddl_time')
    # Rename the columns to be more readable
    # Make a DateText Column to display on the graph

    issue_dates = df['Issue Date'].unique()
    issue_dates.sort()

    unique_licensetypes = df['License Type'].unique()
    unique_licensetypes.sort()
    unique_licensetypes = np.append(['All'], unique_licensetypes)

    total_license_volume = '{:,.0f}'.format(df['Number of Licenses Issued'].sum())

    return html.Div(children=[
                    html.H1('Business License Volumes', style={'text-align': 'center'}),
                    html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
                    html.Div([
                        html.Div([
                            html.P('Filter by Issue Date'),
                            dcc.DatePickerRange(
                                display_format='MMM Y',
                                id='slide1-BL-my-date-picker-range',
                                start_date=datetime(2016, 1, 1),
                                end_date=date.today()
                            ),
                        ], className='four columns'),
                        html.Div([
                            html.P('Filter by Job Type'),
                            dcc.Dropdown(
                                id='slide1-BL-jobtype-dropdown',
                                options=[
                                    {'label': 'All', 'value': 'All'},
                                    {'label': 'Application', 'value': 'BL_Application'},
                                    {'label': 'Renewal', 'value': 'BL_Renewal'}
                                ],
                                value='All'
                            ),
                        ], className='four columns'),
                        html.Div([
                            html.P('Filter by License Type'),
                            dcc.Dropdown(
                                    id='slide1-BL-licensetype-dropdown',
                                    options=[{'label': k, 'value': k} for k in unique_licensetypes],
                                    value='All'
                            ),
                        ], className='four columns'),
                    ], className='dashrow filters'),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='slide1-BL-my-graph',
                                config={
                                    'displayModeBar': False
                                },
                                figure=go.Figure(
                                    data=[
                                        go.Scatter(
                                            x=df['Issue Date'],
                                            y=df['Number of Licenses Issued'],
                                            mode='lines',
                                            text=df['DateText'],
                                            hoverinfo='text+y',
                                            line=dict(
                                                shape='spline',
                                                color='rgb(26, 118, 255)'
                                            )
                                        )
                                    ],
                                ),
                            ),
                        ], className='nine columns'),
                        html.Div([
                            html.H1('', id='slide1-BL-indicator', style={'font-size': '45pt'}),
                            html.H2('Licenses Issued', style={'font-size': '40pt'})
                        ], className='three columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '75px 0'})
                    ], className='dashrow'),
                    html.Div([
                        html.Div([
                            html.H3('License Volumes By License Type and Month', style={'text-align': 'center'}),
                            html.Div([
                                table.DataTable(
                                    rows=[{}],
                                    #columns=['Issue Date', 'LICENSETYPE', 'COUNTJOBS'],
                                    columns=['Issue Date', 'License Type', 'Number of Licenses Issued'],
                                    editable=False,
                                    sortable=True,
                                    id='slide1-BL-count-table'
                                ),
                            ], style={'text-align': 'center'}),
                            html.Div([
                                html.A(
                                    'Download Data',
                                    id='slide1-BL-count-table-download-link',
                                    download='slide1_BL_license_volumes_counts.csv',
                                    href='',
                                    target='_blank',
                                )
                            ], style={'text-align': 'right'})
                        ], style={'width': '55%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '45px', 'margin-bottom': '45px'})
                    ], className='dashrow'),
                    html.Details([
                        html.Summary('Query Description'),
                        html.Div([
                            html.P(
                                'Approved business licenses (inc. activity licenses) issued between 1/1/16 and today.')
                        ])
                    ])
                ])

layout = update_layout

@app.callback(
    Output('slide1-BL-my-graph', 'figure'),
    [Input('slide1-BL-my-date-picker-range', 'start_date'),
     Input('slide1-BL-my-date-picker-range', 'end_date'),
     Input('slide1-BL-jobtype-dropdown', 'value'),
     Input('slide1-BL-licensetype-dropdown', 'value')])
def update_graph(start_date, end_date, jobtype, licensetype):
    df_results = update_counts_graph_data(start_date, end_date, jobtype, licensetype)
    return {
        'data': [
             go.Scatter(
                 x=df_results['Issue Date'],
                 y=df_results['Number of Licenses Issued'],
                 mode='lines',
                 text=df_results['DateText'],
                 hoverinfo='text+y',
                 line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                 )
             )
         ],
        'layout': go.Layout(
            title='Number of Licenses Issued By Month',
            yaxis=dict(
                title='Number of Business Licenses Issued',
                range=[0, df_results['Number of Licenses Issued'].max() + (df_results['Number of Licenses Issued'].max() / 50)]
            )
        )
    }

@app.callback(
    Output('slide1-BL-indicator', 'children'),
    [Input('slide1-BL-my-date-picker-range', 'start_date'),
     Input('slide1-BL-my-date-picker-range', 'end_date'),
     Input('slide1-BL-jobtype-dropdown', 'value'),
     Input('slide1-BL-licensetype-dropdown', 'value')])
def update_total_license_volume_indicator(start_date, end_date, jobtype, licensetype):
    total_license_volume_updated = update_total_license_volume(start_date, end_date, jobtype, licensetype)
    return str(total_license_volume_updated)

@app.callback(
    Output('slide1-BL-count-table', 'rows'),
    [Input('slide1-BL-my-date-picker-range', 'start_date'),
     Input('slide1-BL-my-date-picker-range', 'end_date'),
     Input('slide1-BL-jobtype-dropdown', 'value'),
     Input('slide1-BL-licensetype-dropdown', 'value')])
def update_count_table(start_date, end_date, jobtype, licensetype):
    df_counts = update_counts_table_data(start_date, end_date, jobtype, licensetype)
    return df_counts.to_dict('records')

@app.callback(
    Output('slide1-BL-count-table-download-link', 'href'),
    [Input('slide1-BL-my-date-picker-range', 'start_date'),
     Input('slide1-BL-my-date-picker-range', 'end_date'),
     Input('slide1-BL-jobtype-dropdown', 'value'),
     Input('slide1-BL-licensetype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, jobtype, licensetype):
    df_counts = update_counts_table_data(start_date, end_date, jobtype, licensetype)
    csv_string = df_counts.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string