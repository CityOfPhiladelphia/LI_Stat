import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime, date
import numpy as np
import urllib.parse

from app import app, con

print('PublicDemos.py')

with con() as con:
    sql = 'SELECT * FROM li_stat_publicdemos'
    df = pd.read_sql_query(sql=sql, con=con, parse_dates=['DEMODATE'])
    sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_PUBLICDEMOS'"
    last_ddl_time = pd.read_sql_query(sql=sql, con=con)

# Rename the columns to be more readable
# Make a DateText Column to display on the graph
df = (df.rename(columns={'DEMODATE': 'Demo Date', 'COUNTDEMOS': 'Count of Demos'})
        .assign(DateText=lambda x: x['Demo Date'].dt.strftime('%b %Y')))

total_demos = '{:,.0f}'.format(df['Count of Demos'].sum())


def update_total_public_demos(selected_start, selected_end):
    df_selected = df.copy(deep=True)

    df_selected = df_selected.loc[(df_selected['Demo Date'] >= selected_start)&(df_selected['Demo Date'] <= selected_end)]
    total_demos = df_selected['Count of Demos'].sum()
    return '{:,.0f}'.format(total_demos)


def update_counts_graph_data(selected_start, selected_end):
    df_selected = df.copy(deep=True)

    df_selected = (df_selected.loc[(df_selected['Demo Date'] >= selected_start) & (df_selected['Demo Date'] <= selected_end)]
                              .groupby(by=['Demo Date', 'DateText'])['Count of Demos']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Demo Date']))
    return df_selected

def update_counts_graph_data_compare(selected_start, selected_end, compare_date_start, compare_date_end):
    df_selected1 = df.copy(deep=True)
    df_selected1 = (df_selected1.loc[(df_selected1['Demo Date'] >= selected_start) & (df_selected1['Demo Date'] <= selected_end)]
                              .groupby(by=['Demo Date', 'DateText'])['Count of Demos']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Demo Date']))

    df_selected2 = df.copy(deep=True)
    df_selected2 = (df_selected2.loc[(df_selected2['Demo Date'] >= compare_date_start) & (df_selected2['Demo Date'] <= compare_date_end)]
                              .groupby(by=['Demo Date', 'DateText'])['Count of Demos']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Demo Date']))
    return (df_selected1, df_selected2)

layout = html.Div(children=[
                html.H1('Public Demolitions', style={'text-align': 'center', 'margin-bottom': '20px'}),
                html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Demolition Date'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='public-demos-date-picker-range',
                            start_date=datetime(2018, 1, 1),
                            end_date=date.today()
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.Button('Compare Date Ranges',
                                    id='public-demos-date-comparison-button',
                                    style={'background-color': '#444', 'color': 'white', 'padding': '15px'})
                    ], className='columns', style={'width': '33%', 'text-align': 'center', 'transform': 'translateY(92%)'}),
                    html.Div(id='comparison-date-range-div', children=[
                        html.P('Comparison Date Range'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='public-demos-comparison-date-picker-range',
                            start_date=datetime(2017, 1, 1),
                            end_date=datetime(2017, 12, 31),
                        )
                    ], className='four columns', style={'display': 'none'}),
                ], className='dashrow', style={'margin-top': '75px', 'margin-bottom': '100px'}),
                html.Div([
                    html.Div([
                        html.H2('', id='public-demos-indicator1', style={'font-size': '30pt', 'float': 'left'})
                    ], className='columns', style={'width': '15%'}),
                    html.Div([
                        html.H2('Completed Public Demos', style={'font-size': '25pt'})
                    ], className='columns', style={'width': '69%', 'margin-left': 'auto', 'margin-right': 'auto', 'text-align': 'center'}),
                    html.Div(id='public-demos-indicator2-div', children=[
                        html.H2('', id='public-demos-indicator2', style={'font-size': '30pt'})
                    ], className='columns', style={'width': '15%', 'display': 'none'}),
                ], style={'display': 'table', 'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto'}),
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
                html.Details([
                    html.Summary('Query Description'),
                    html.Div([
                        html.P(
                            'Public Demolitions since Jan 2008. Demo Date is the demo completion date.')
                    ])
                ])
])


@app.callback(
    Output('public-demos-indicator1', 'children'),
    [Input('public-demos-date-picker-range', 'start_date'),
     Input('public-demos-date-picker-range', 'end_date')])
def update_public_demos(start_date, end_date):
    total_public_demos = update_total_public_demos(start_date, end_date)
    return str(total_public_demos)


@app.callback(
    Output('public-demos-indicator2', 'children'),
    [Input('public-demos-comparison-date-picker-range', 'start_date'),
     Input('public-demos-comparison-date-picker-range', 'end_date')])
def update_public_demos(start_date, end_date):
    total_public_demos = update_total_public_demos(start_date, end_date)
    return str(total_public_demos)


@app.callback(
    Output('public-demos-indicator2-div', 'style'),
    [Input('public-demos-date-comparison-button', 'n_clicks')])
def show_indicator2(n_clicks):
    if n_clicks is None or (n_clicks % 2) == 0:
        return {'display': 'none'}
    else:
        return {'width': '15%', 'display': 'block'}


@app.callback(
    Output('comparison-date-range-div', 'style'),
    [Input('public-demos-date-comparison-button', 'n_clicks')])
def show_comparison_date_range_picker(n_clicks):
    if n_clicks is None or (n_clicks % 2) == 0:
        return {'display': 'none'}
    else:
        return {'display': 'block'}

@app.callback(
    Output('public-demos-graph', 'figure'),
    [Input('public-demos-date-picker-range', 'start_date'),
     Input('public-demos-date-picker-range', 'end_date'),
     Input('public-demos-date-comparison-button', 'n_clicks'),
     Input('public-demos-comparison-date-picker-range', 'start_date'),
     Input('public-demos-comparison-date-picker-range', 'end_date')])
def update_graph(start_date1, end_date1, n_clicks, start_date2, end_date2):
    if n_clicks is None or (n_clicks % 2) == 0:
        df_results = update_counts_graph_data(start_date1, end_date1)
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
                    title='Month of Demolition'
                ),
                yaxis=dict(
                    title='Completed Public Demos',
                    range=[0, df_results['Count of Demos'].max() + (df_results['Count of Demos'].max() / 25)]
                )
            )
        }
    else:
        results = update_counts_graph_data_compare(start_date1, end_date1, start_date2, end_date2)
        df_results1 = results[0]
        df_results2 = results[1]
        x_min = df_results1.index.min() if df_results1.index.min() < df_results2.index.min() else df_results2.index.min()
        x_max = df_results1.index.max() if df_results1.index.max() > df_results2.index.max() else df_results2.index.max()
        y_max = df_results1['Count of Demos'].max() if df_results1['Count of Demos'].max() > df_results2['Count of Demos'].max() else df_results2['Count of Demos'].max()

        return {
            'data': [
                go.Scatter(
                    x=df_results1.index,
                    y=df_results1['Count of Demos'],
                    mode='lines',
                    text=df_results1['DateText'],
                    hoverinfo='text+y',
                    line=dict(
                        shape='spline',
                        color='rgb(26, 118, 255)'
                    ),
                    name=datetime.strptime(start_date1, '%Y-%m-%d').strftime("%b %Y") + ' - ' + datetime.strptime(end_date1, '%Y-%m-%d').strftime("%b %Y")
                ),
                go.Scatter(
                    x=df_results2.index,
                    y=df_results2['Count of Demos'],
                    mode='lines',
                    text=df_results2['DateText'],
                    hoverinfo='text+y',
                    line=dict(
                        shape='spline',
                        color='#ff7f0e'
                    ),
                    name=datetime.strptime(start_date2, '%Y-%m-%d').strftime("%b %Y") + ' - ' + datetime.strptime(end_date2, '%Y-%m-%d').strftime("%b %Y"),
                    yaxis='y2'
                )
            ],
            'layout': go.Layout(
                xaxis=dict(
                    title='Month of Demolition',
                    range=[x_min, x_max]
                ),
                yaxis=dict(
                    title='Completed Public Demos',
                    range=[0, y_max + (y_max / 25)]
                ),
                yaxis2=dict(
                    range=[0, y_max + (y_max / 25)],
                    overlaying='y'
                )
            )
        }



