import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import urllib.parse
import os

from datetime import datetime
from dash.dependencies import Input, Output

from app import app, con

def update_data(start_date, end_date):
    df_results = df.loc[(df['Violation Month'] >= start_date) & (df['Violation Month'] <= end_date)]\
                   .sort_values(by=['Violation Month'])
    return df_results

print(os.path.basename(__file__))

with con() as con:
    sql = 'SELECT * FROM li_stat_unsafes'
    df = pd.read_sql_query(sql=sql, con=con, parse_dates=['VIOLATIONDATE'])
    sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_UNSAFES'"
    last_ddl_time = pd.read_sql_query(sql=sql, con=con)

# Rename the columns to be more readable
df.rename(columns=
            {'VIOLATIONDATE': 'Violation Month', 
             'NUMBEROFVIOLATIONS': 'Number of Violations'}, 
          inplace=True)

# Make a DateText Column to display on the graph
df = df.assign(DateText=lambda x: x['Violation Month'].dt.strftime('%b %Y'))

layout = html.Div(children=[
                html.H1('Unsafe Violations', style={'text-align': 'center'}),
                html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
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
                                        x=df['Violation Month'],
                                        y=df['Number of Violations'],
                                        mode='lines',
                                        text=df['DateText'],
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
                html.Details([
                    html.Summary('Query Description'),
                    html.Div([
                        html.P(
                            'Unsafe violations since 1/1/2016.')
                    ])
                ])
            ])

@app.callback(
    Output('unsafes-graph', 'figure'),
    [Input('unsafes-date-picker-range', 'start_date'),
     Input('unsafes-date-picker-range', 'end_date')])
def update_graph(start_date, end_date):
    df_results = update_data(start_date, end_date)
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
    Output('unsafes-table', 'rows'),
    [Input('unsafes-date-picker-range', 'start_date'),
     Input('unsafes-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    df_results = update_data(start_date, end_date)[['DateText', 'Number of Violations']]
    df_results.rename(columns={'DateText': 'Violation Month',
                               'Number of Violations': 'Number of Unsafe Violations'}, inplace=True)
    return df_results.to_dict('records')

@app.callback(
    Output('unsafes-table-download-link', 'href'),
    [Input('unsafes-date-picker-range', 'start_date'),
     Input('unsafes-date-picker-range', 'end_date')])
def update_download_link(start_date, end_date):
    df_results = update_data(start_date, end_date)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string