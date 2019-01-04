import os
from datetime import datetime
import urllib.parse

import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import numpy as np
from dash.dependencies import Input, Output

from app import app, cache, cache_timeout
from config import MAPBOX_ACCESS_TOKEN


print(os.path.basename(__file__))

@cache_timeout
@cache.memoize()
def query_data(dataset):
    from app import con
    with con() as con:
        if dataset == 'df_ind':
            sql = 'SELECT * FROM li_stat_unsafes_ind'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['VIOLATIONDATE'])
        elif dataset == 'df_counts':
            sql = 'SELECT * FROM li_stat_unsafes_counts'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['VIOLATIONDATE'])
            df.rename(columns=
                {'VIOLATIONDATE': 'Violation Month', 
                 'NUMBEROFVIOLATIONS': 'Number of Violations'}, 
            inplace=True)
            df = df.assign(DateText=lambda x: x['Violation Month'].dt.strftime('%b %Y'))
        elif dataset == 'ind_last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_UNSAFES_IND'"
            df = pd.read_sql_query(sql=sql, con=con)
        elif dataset == 'counts_last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_UNSAFES_COUNTS'"
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def get_df_ind():
    df_ind = dataframe('df_ind')
    df_ind['VIOLATIONDATE'] = pd.to_datetime(df_ind['VIOLATIONDATE'])
    return df_ind

def get_ind_last_ddl_time():
    ind_last_ddl_time = dataframe('ind_last_ddl_time')
    return ind_last_ddl_time['LAST_DDL_TIME'].iloc[0]

def get_df_counts():
    df_counts = dataframe('df_counts')
    df_counts['Violation Month'] = pd.to_datetime(df_counts['Violation Month'])
    return df_counts

def get_counts_last_ddl_time():
    counts_last_ddl_time = dataframe('counts_last_ddl_time')
    return counts_last_ddl_time['LAST_DDL_TIME'].iloc[0]

def update_counts_data(start_date, end_date):
    df_counts = get_df_counts()
    df_results = df_counts.loc[(df_counts['Violation Month'] >= start_date) & (df_counts['Violation Month'] <= end_date)]\
                          .sort_values(by=['Violation Month'])
    return df_results

def update_ind_data(start_date, end_date):
    df_ind = get_df_ind()
    df_results = df_ind.loc[(df_ind['VIOLATIONDATE'] >= start_date) & (df_ind['VIOLATIONDATE'] <= end_date)]\
                       .sort_values(by=['VIOLATIONDATE'])
    return df_results

def update_layout():
    ind_last_ddl_time = get_ind_last_ddl_time()
    counts_last_ddl_time = get_counts_last_ddl_time()
    df_ind = get_df_ind()
    df_counts = get_df_counts()

    return html.Div(children=[
                html.H1('Unsafe Violations', style={'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Violation Date'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='unsafes-date-picker-range',
                            start_date=datetime(2016, 1, 1),
                            end_date=datetime.now()
                        ),
                    ], className='six columns')
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='unsafes-graph',
                            config={
                                'displayModeBar': False
                            },
                            figure=go.Figure(
                                data=[
                                    go.Scatter(
                                        x=df_counts['Violation Month'],
                                        y=df_counts['Number of Violations'],
                                        mode='lines',
                                        text=df_counts['DateText'],
                                        hoverinfo='text+y',
                                        line=dict(
                                            shape='spline',
                                            color='rgb(26, 118, 255)'
                                        ),
                                        name='Number of Unsafe Violations'
                                    )
                                ],
                                layout=go.Layout(
                                    title='Number of Unsafe Violations',
                                    yaxis=dict(
                                        title='Number of Unsafe Violations'
                                    )
                                )
                            )
                        )
                    ], className='twelve columns'),
                ], className='dashrow'),
                html.P(f"Data last updated {counts_last_ddl_time}", className = 'timestamp', style = {'text-align': 'center'}),
                html.Div([
                    html.Div([
                        dcc.Graph(id='unsafes-map',
                          figure=go.Figure(
                              data=[
                                  go.Scattermapbox(
                                      lon=df_ind['LON'],
                                      lat=df_ind['LAT'],
                                      mode='markers',
                                      marker=dict(
                                          size=14
                                      ),
                                      text='Address: ' + df_ind['ADDRESS'].map(str) +
                                           '<br>' +
                                           'Status: ' + df_ind['STATUS'].map(str) +
                                           '<br>' +
                                           'Case Status: ' + df_ind['CASESTATUS'].map(str) +
                                           '<br>' +
                                           'Violation Date: ' + df_ind['VIOLATIONDATE'].dt.date.map(str),
                                      hoverinfo='text'
                                  )
                              ],
                              layout=go.Layout(
                                  autosize=True,
                                  hovermode='closest',
                                  mapbox=dict(
                                      accesstoken=MAPBOX_ACCESS_TOKEN,
                                      bearing=0,
                                      center=dict(
                                          lon=-75.1652,
                                          lat=39.9526
                                      ),
                                      pitch=0,
                                      zoom=10
                                  ),
                              )
                          )
                          , style={'height': '700px'})
                    ], className='twelve columns')
                ], className='dashrow'),
                html.P(f"Data last updated {ind_last_ddl_time}", className = 'timestamp', style = {'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.H3('Number of Unsafe Violations by Month', style={'text-align': 'center'}),
                        html.Div([
                            dt.DataTable(
                                rows=[{}],
                                editable=False,
                                sortable=True,
                                filterable=False,
                                id='unsafes-table'
                            ),
                        ], style={'text-align': 'center'},
                           id='unsafes-table-div'
                        ),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='unsafes-table-download-link',
                                download='unsafes.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'width': '50%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow'),
                html.P(f"Data last updated {counts_last_ddl_time}", className = 'timestamp', style = {'text-align': 'center'}),
                html.Details([
                    html.Summary('Query Description'),
                    html.Div([
                        html.P(
                            'Unsafe violations since 1/1/2016.')
                    ])
                ])
            ])

layout = update_layout

@app.callback(
    Output('unsafes-graph', 'figure'),
    [Input('unsafes-date-picker-range', 'start_date'),
     Input('unsafes-date-picker-range', 'end_date')])
def update_graph(start_date, end_date):
    df_results = update_counts_data(start_date, end_date)
    return {
        'data': [
            go.Scatter(
                x=df_results['Violation Month'],
                y=df_results['Number of Violations'],
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                ),
                name='Number of Unsafe Violations'
            )
        ],
        'layout': go.Layout(
                title='Number of Unsafe Violations',
                yaxis=dict(
                    title='Number of Unsafe Violations',
                    range=[0, df_results['Number of Violations'].max() + (df_results['Number of Violations'].max() / 50)]
                )
        )
    }

@app.callback(
    Output('unsafes-map', 'figure'),
    [Input('unsafes-date-picker-range', 'start_date'),
     Input('unsafes-date-picker-range', 'end_date')])
def update_map(start_date, end_date):
    df_results = update_ind_data(start_date, end_date)
    return {
        'data': [
            go.Scattermapbox(
                lon=df_results['LON'],
                lat=df_results['LAT'],
                mode='markers',
                marker=dict(
                    size=14
                ),
                text='Address: ' + df_results['ADDRESS'].map(str) +
                     '<br>' +
                     'Status: ' + df_results['STATUS'].map(str) +
                     '<br>' +
                     'Case Status: ' + df_results['CASESTATUS'].map(str) +
                     '<br>' +
                     'Violation Date: ' + df_results['VIOLATIONDATE'].dt.date.map(str),
                hoverinfo='text'
            )
        ],
        'layout': go.Layout(
                    autosize=True,
                    hovermode='closest',
                    mapbox=dict(
                        accesstoken=MAPBOX_ACCESS_TOKEN,
                        bearing=0,
                        center=dict(
                            lon=-75.1652,
                            lat=39.9526
                        ),
                        pitch=0,
                        zoom=10
                    ),
        )
    }

@app.callback(
    Output('unsafes-table', 'rows'),
    [Input('unsafes-date-picker-range', 'start_date'),
     Input('unsafes-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    df_results = update_counts_data(start_date, end_date)[['DateText', 'Number of Violations']]
    df_results.rename(columns={'DateText': 'Violation Month',
                               'Number of Violations': 'Number of Unsafe Violations'}, inplace=True)
    return df_results.to_dict('records')

@app.callback(
    Output('unsafes-table-download-link', 'href'),
    [Input('unsafes-date-picker-range', 'start_date'),
     Input('unsafes-date-picker-range', 'end_date')])
def update_download_link(start_date, end_date):
    df_results = update_counts_data(start_date, end_date)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string