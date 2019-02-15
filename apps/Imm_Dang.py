import os
from datetime import datetime
import urllib.parse

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
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
            sql = 'SELECT * FROM li_stat_immdang_ind'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['VIOLATIONDATE'])
            df.sort_values(by='VIOLATIONDATE', inplace=True)
        elif dataset == 'df_counts':
            sql = 'SELECT * FROM li_stat_immdang_counts'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['VIOLATIONDATE'])
            df = df.assign(DateText=lambda x: x['VIOLATIONDATE'].dt.strftime('%b %Y'))
            df.sort_values(by='VIOLATIONDATE', inplace=True)
        elif dataset == 'ind_last_ddl_time':
            sql = 'SELECT SCN_TO_TIMESTAMP(MAX(ora_rowscn)) last_ddl_time FROM LI_STAT_IMMDANG_IND'
            df = pd.read_sql_query(sql=sql, con=con)
        elif dataset == 'counts_last_ddl_time':
            sql = 'SELECT SCN_TO_TIMESTAMP(MAX(ora_rowscn)) last_ddl_time FROM LI_STAT_IMMDANG_COUNTS'
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def get_df_ind():
    df_ind = dataframe('df_ind')
    df_ind['VIOLATIONDATE'] = pd.to_datetime(df_ind['VIOLATIONDATE'])
    return df_ind

def get_df_counts():
    df_counts = dataframe('df_counts')
    df_counts['VIOLATIONDATE'] = pd.to_datetime(df_counts['VIOLATIONDATE'])
    df_counts.rename(columns=
                {'VIOLATIONDATE': 'Violation Month', 
                'NUMBEROFVIOLATIONS': 'Number of Violations'}, 
            inplace=True)
    df_counts = df_counts.assign(DateText=lambda x: x['Violation Month'].dt.strftime('%b %Y'))
    return df_counts

def get_ind_last_ddl_time():
    ind_last_ddl_time = dataframe('ind_last_ddl_time')
    return ind_last_ddl_time['LAST_DDL_TIME'].iloc[0]

def get_counts_last_ddl_time():
    counts_last_ddl_time = dataframe('counts_last_ddl_time')
    return counts_last_ddl_time['LAST_DDL_TIME'].iloc[0]

def update_counts_data(start_date, end_date):
    df_counts = dataframe('df_counts')
    df_results = df_counts.loc[(df_counts['VIOLATIONDATE'] >= start_date) & (df_counts['VIOLATIONDATE'] <= end_date)]\
                          .sort_values(by=['VIOLATIONDATE'])
    return df_results

def update_ind_data(start_date, end_date):
    df_ind = dataframe('df_ind')
    df_results = df_ind.loc[(df_ind['VIOLATIONDATE'] >= start_date) & (df_ind['VIOLATIONDATE'] <= end_date)]\
                       .sort_values(by=['VIOLATIONDATE'])
    return df_results

def update_layout():
    df_ind = get_df_ind()
    df_counts = get_df_counts()
    ind_last_ddl_time = get_ind_last_ddl_time()
    counts_last_ddl_time = get_counts_last_ddl_time()

    return html.Div(children=[
                    html.H1('Immenently Dangerous Violations', style={'text-align': 'center'}),
                    html.Div([
                        html.Div([
                            html.P('Filter by Violation Date'),
                            dcc.DatePickerRange(
                                display_format='MMM Y',
                                id='imm-dang-date-picker-range',
                                start_date=datetime(2016, 1, 1),
                                end_date=datetime.now()
                            ),
                        ], className='six columns')
                    ], className='dashrow filters'),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='imm-dang-graph',
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
                                            name='Number of ID Violations'
                                        )
                                    ],
                                    layout=go.Layout(
                                        title='Number of ID Violations',
                                        yaxis=dict(
                                            title='Number of ID Violations'
                                        )
                                    )
                                )
                            )
                        ], className='twelve columns'),
                    ], className='dashrow'),
                    html.P(f"Data last updated {counts_last_ddl_time}", className = 'timestamp', style = {'text-align': 'center'}),
                    html.Div([
                        html.Div([
                            dcc.Graph(id='imm-dang-map',
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
                                                'Status: '+ df_ind['STATUS'].map(str) +
                                                '<br>' +
                                                'Case Status: ' + df_ind['CASESTATUS'].map(str) +
                                                '<br>' +
                                                'Violation Date: '+ df_ind['VIOLATIONDATE'].dt.date.map(str),
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
                            html.H3('Number of ID Violations by Month', style={'text-align': 'center'}),
                            html.Div([
                                dt.DataTable(
                                    rows=[{}],
                                    editable=False,
                                    sortable=True,
                                    filterable=False,
                                    id='imm-dang-table'
                                ),
                            ], style={'text-align': 'center'},
                            id='imm-dang-table-div'
                            ),
                            html.Div([
                                html.A(
                                    'Download Data',
                                    id='imm-dang-table-download-link',
                                    download='imm-dangs.csv',
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
                                'Imminently Dangerous violations since 1/1/2016.')
                        ])
                    ])
                ])

layout = update_layout

@app.callback(
    Output('imm-dang-graph', 'figure'),
    [Input('imm-dang-date-picker-range', 'start_date'),
     Input('imm-dang-date-picker-range', 'end_date')])
def update_graph(start_date, end_date):
    df_results = update_counts_data(start_date, end_date)
    df_results['VIOLATIONDATE'] = pd.to_datetime(df_results['VIOLATIONDATE'])
    df_results = df_results.assign(DateText=lambda x: x['VIOLATIONDATE'].dt.strftime('%b %Y'))
    return {
        'data': [
            go.Scatter(
                x=df_results['VIOLATIONDATE'],
                y=df_results['NUMBEROFVIOLATIONS'],
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                ),
                name='Number of ID Violations'
            )
        ],
        'layout': go.Layout(
                title='Number of ID Violations',
                yaxis=dict(
                    title='Number of ID Violations',
                    range=[0, df_results['NUMBEROFVIOLATIONS'].max() + (df_results['NUMBEROFVIOLATIONS'].max() / 50)]
                )
        )
    }

@app.callback(
    Output('imm-dang-map', 'figure'),
    [Input('imm-dang-date-picker-range', 'start_date'),
     Input('imm-dang-date-picker-range', 'end_date')])
def update_map(start_date, end_date):
    df_results = update_ind_data(start_date, end_date)
    df_results['VIOLATIONDATE'] = pd.to_datetime(df_results['VIOLATIONDATE'])
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
    Output('imm-dang-table', 'rows'),
    [Input('imm-dang-date-picker-range', 'start_date'),
     Input('imm-dang-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    df_results = update_counts_data(start_date, end_date)[['DateText', 'NUMBEROFVIOLATIONS']]
    df_results.rename(columns={'DateText': 'Violation Month',
                               'NUMBEROFVIOLATIONS': 'Number of ID Violations'}, inplace=True)
    return df_results.to_dict('records')

@app.callback(
    Output('imm-dang-table-download-link', 'href'),
    [Input('imm-dang-date-picker-range', 'start_date'),
     Input('imm-dang-date-picker-range', 'end_date')])
def update_download_link(start_date, end_date):
    df_results = update_counts_data(start_date, end_date)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string