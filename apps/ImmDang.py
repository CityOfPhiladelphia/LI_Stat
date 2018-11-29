import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import urllib.parse

from datetime import datetime
from dash.dependencies import Input, Output

from app import app, con_GISLNI


def update_data(start_date, end_date):
    df_results = df.loc[(df['Violation Month'] >= start_date) & (df['Violation Month'] <= end_date)]\
                   .sort_values(by=['Violation Month'])
    return df_results

print('ImmDang.py')

with con_GISLNI() as con:
    with open(r'queries/ImmDang.sql') as sql:
        df = pd.read_sql_query(sql=sql.read(), con=con, parse_dates=['VIOLATIONDATE'])

# Rename the columns to be more readable
df.rename(columns=
            {'VIOLATIONDATE': 'Violation Month', 
             'NUMBEROFVIOLATIONS': 'Number of Violations'}, 
          inplace=True)

# Make a DateText Column to display on the graph
df = df.assign(DateText=lambda x: x['Violation Month'].dt.strftime('%b %Y'))

layout = html.Div(children=[
                html.H1('Immenently Dangerous Buildings', style={'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Date Range'),
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
                        dcc.Graph(id='imm-dang-graph',
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
            ])

@app.callback(
    Output('imm-dang-graph', 'figure'),
    [Input('imm-dang-date-picker-range', 'start_date'),
     Input('imm-dang-date-picker-range', 'end_date')])
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
                name='Number of ID Violations'
            )
        ],
        'layout': go.Layout(
                title='Number of ID Violations',
                yaxis=dict(
                    title='Number of ID Violations',
                    range=[0, df_results['Number of Violations'].max() + (df_results['Number of Violations'].max() / 50)]
                )
        )
    }

@app.callback(
    Output('imm-dang-table', 'rows'),
    [Input('imm-dang-date-picker-range', 'start_date'),
     Input('imm-dang-date-picker-range', 'end_date')])
def update_table(start_date, end_date):
    df_results = update_data(start_date, end_date)[['DateText', 'Number of Violations']]
    df_results.rename(columns={'DateText': 'Violation Month',
                               'Number of Violations': 'Number of ID Violations'}, inplace=True)
    return df_results.to_dict('records')

@app.callback(
    Output('imm-dang-table-download-link', 'href'),
    [Input('imm-dang-date-picker-range', 'start_date'),
     Input('imm-dang-date-picker-range', 'end_date')])
def update_download_link(start_date, end_date):
    df_results = update_data(start_date, end_date)
    csv_string = df_results.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string