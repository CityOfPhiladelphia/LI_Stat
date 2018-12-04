import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import numpy as np
import urllib.parse

from app import app, con_DataBridge

testing_mode = False
print('PublicDemos.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('test_data/PublicDemos.csv', parse_dates=['DEMODATE'])

else:
    with con_DataBridge() as con_DataBridge:
        with open(r'queries/PublicDemos.sql') as sql:
            df = pd.read_sql_query(sql=sql.read(), con=con_DataBridge, parse_dates=['DEMODATE'])

# Rename the columns to be more readable
# Make a DateText Column to display on the graph
df = (df.rename(columns={'DEMODATE': 'Demo Date', 'COUNTDEMOS': 'Count of Demos'})
        .assign(DateText=lambda x: x['Demo Date'].dt.strftime('%b %Y')))

total_demos = '{:,.0f}'.format(df['Count of Demos'].sum())


def update_total_public_demos(selected_start, selected_end):
    df_selected = df.copy(deep=True)

    df_selected = df_selected.loc[(df['Demo Date'] >= selected_start)&(df_selected['Demo Date'] <= selected_end)]
    total_demos = df_selected['Count of Demos'].sum()
    return '{:,.0f}'.format(total_demos)


def update_counts_graph_data(selected_start, selected_end):
    df_selected = df.copy(deep=True)

    df_selected = (df_selected.loc[(df['Demo Date'] >= selected_start) & (df_selected['Demo Date'] <= selected_end)]
                              .groupby(by=['Demo Date', 'DateText'])['Count of Demos']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Demo Date']))
    return df_selected


layout = html.Div(children=[
                html.H1('Public Demolitions', style={'text-align': 'center', 'margin-bottom': '20px'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Demolition Date'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='public-demos-date-picker-range',
                            start_date=datetime(2008, 1, 1),
                            end_date=datetime.now()
                        ),
                    ], className='seven columns'),
                    html.Div([
                        html.H2('', id='public-demos-indicator', style={'font-size': '30pt'}),
                        html.H3('Completed Public Demos', style={'font-size': '25pt'})
                    ], className='five columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '0px 0'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        dcc.Graph(id='public-demos-graph',
                            figure=go.Figure(
                                data=[
                                    go.Scatter(
                                        x=df['Demo Date'],
                                        y=df['Count of Demos'],
                                        mode='lines',
                                        text=df['DateText'],
                                        hoverinfo='text+y',
                                        line=dict(
                                            shape='spline',
                                            color='rgb(26, 118, 255)'
                                        ),
                                        name='Public Demos Completed'
                                    )
                                ],
                                layout=go.Layout(
                                    xaxis=dict(
                                        title='Demolition Date'
                                    ),
                                    yaxis=dict(
                                        title='Completed Public Demos'
                                    )
                                )
                            )
                        )
                    ], className='twelve columns'),
                ], className='dashrow'),
            ])

@app.callback(
    Output('public-demos-graph', 'figure'),
    [Input('public-demos-date-picker-range', 'start_date'),
     Input('public-demos-date-picker-range', 'end_date')])
def update_graph(start_date, end_date):
    df_results = update_counts_graph_data(start_date, end_date)
    return {
        'data': [
            go.Scatter(
                x=df_results['Demo Date'],
                y=df_results['Count of Demos'],
                mode='lines',
                text=df_results['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                ),
                name='Public Demos Completed'
            )
        ],
        'layout': go.Layout(
            xaxis=dict(
                title='Demolition Date'
            ),
            yaxis=dict(
                title='Completed Public Demos',
                range=[0, df_results['Count of Demos'].max() + (df_results['Count of Demos'].max() / 50)]
            )
        )
    }

@app.callback(
    Output('public-demos-indicator', 'children'),
    [Input('public-demos-date-picker-range', 'start_date'),
     Input('public-demos-date-picker-range', 'end_date')])
def update_public_demos(start_date, end_date):
    total_public_demos = update_total_public_demos(start_date, end_date)
    return str(total_public_demos)


