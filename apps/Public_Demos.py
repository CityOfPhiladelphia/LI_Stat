import os
from datetime import datetime, date
import urllib.parse

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
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
            sql = 'SELECT * FROM li_stat_publicdemos'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['DEMODATE'])
        elif dataset == 'last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_PUBLICDEMOS'"
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def get_last_ddl_time():
    last_ddl_time = dataframe('last_ddl_time')
    return last_ddl_time['LAST_DDL_TIME'].iloc[0]

def get_df_ind():
    df_ind = dataframe('df_ind')
    df_ind['DEMODATE'] = pd.to_datetime(df_ind['DEMODATE'])
    df_ind = (df_ind.rename(columns={'DEMODATE': 'Demo Date', 'COUNTDEMOS': 'Count of Demos'})
        .assign(DateText=lambda x: x['Demo Date'].dt.strftime('%b %Y')))
    df_ind['Demo Date'] = df_ind['Demo Date'].map(lambda dt: dt.date())
    return df_ind

def get_issue_dates(df_ind):
    issue_dates = df_ind['Demo Date'].unique()
    return issue_dates

def get_total_demos(df_ind):
    return '{:,.0f}'.format(df_ind['Count of Demos'].sum())

def update_total_public_demos(selected_start, selected_end):
    df_selected = get_df_ind()

    start_date = datetime.strptime(selected_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(selected_end, "%Y-%m-%d").date()

    df_selected = df_selected.loc[(df_selected['Demo Date'] >= start_date)&(df_selected['Demo Date'] <= end_date)]
    total_demos = df_selected['Count of Demos'].sum()
    return '{:,.0f}'.format(total_demos)

def update_counts_graph_data(selected_start, selected_end):
    df_selected = get_df_ind()
    issue_dates = get_issue_dates(df_selected)

    start_date = datetime.strptime(selected_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(selected_end, "%Y-%m-%d").date()

    selected_issue_dates = issue_dates[(issue_dates >= start_date) & (issue_dates <= end_date)]

    df_selected = (df_selected.loc[(df_selected['Demo Date'] >= start_date) & (df_selected['Demo Date'] <= end_date)]
                              .groupby(by=['Demo Date', 'DateText'])['Count of Demos']
                              .sum()
                              .reset_index())
    for month in selected_issue_dates:
        if month not in df_selected['Demo Date'].values:
            df_missing_month = pd.DataFrame([[month, month.strftime('%b %Y'), 0]], columns=['Demo Date', 'DateText', 'Count of Demos'])
            df_selected = df_selected.append(df_missing_month, ignore_index=True)
    df_selected['Demo Date'] = pd.Categorical(df_selected['Demo Date'], issue_dates)
    return df_selected.sort_values(by='Demo Date')

def update_counts_graph_data_compare(selected_start, selected_end, compare_date_start, compare_date_end):
    df_selected1 = get_df_ind()
    issue_dates = get_issue_dates(df_selected1)
    start_date = datetime.strptime(selected_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(selected_end, "%Y-%m-%d").date()
    selected_issue_dates = issue_dates[(issue_dates >= start_date) & (issue_dates <= end_date)]
    
    df_selected1 = (df_selected1.loc[(df_selected1['Demo Date'] >= start_date) & (df_selected1['Demo Date'] <= end_date)]
                              .groupby(by=['Demo Date', 'DateText'])['Count of Demos']
                              .sum()
                              .reset_index())
    for month in selected_issue_dates:
        if month not in df_selected1['Demo Date'].values:
            df_missing_month = pd.DataFrame([[month, month.strftime('%b %Y'), 0]], columns=['Demo Date', 'DateText', 'Count of Demos'])
            df_selected1 = df_selected1.append(df_missing_month, ignore_index=True)
    df_selected1['Demo Date'] = pd.Categorical(df_selected1['Demo Date'], issue_dates)
    df_selected1.sort_values(by='Demo Date', inplace=True)

    compare_start_date = datetime.strptime(compare_date_start, "%Y-%m-%d").date()
    compare_end_date = datetime.strptime(compare_date_end, "%Y-%m-%d").date()
    compare_selected_issue_dates = issue_dates[(issue_dates >= compare_start_date) & (issue_dates <= compare_end_date)]
    df_selected2 = get_df_ind()
    df_selected2 = (df_selected2.loc[(df_selected2['Demo Date'] >= compare_start_date) & (df_selected2['Demo Date'] <= compare_end_date)]
                              .groupby(by=['Demo Date', 'DateText'])['Count of Demos']
                              .sum()
                              .reset_index())
    for month in compare_selected_issue_dates:
        if month not in df_selected2['Demo Date'].values:
            df_missing_month = pd.DataFrame([[month, month.strftime('%b %Y'), 0]],
                                            columns=['Demo Date', 'DateText', 'Count of Demos'])
            df_selected2 = df_selected2.append(df_missing_month, ignore_index=True)
    df_selected2['Demo Date'] = pd.Categorical(df_selected2['Demo Date'], issue_dates)
    df_selected2.sort_values(by='Demo Date', inplace=True)

    return (df_selected1, df_selected2)

def update_layout():
    last_ddl_time = get_last_ddl_time()
    df_ind = get_df_ind()
    issue_dates = get_issue_dates(df_ind)
    total_demos = get_total_demos(df_ind)

    return html.Div(children=[
                html.H1('Public Demolitions', style={'text-align': 'center', 'margin-bottom': '20px'}),
                html.P(f"Data last updated {last_ddl_time}", style = {'text-align': 'center'}),
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
                        dcc.Graph(
                            id='public-demos-graph',
                            config={
                                'displayModeBar': False
                            },
                            figure=go.Figure(
                                data=[
                                    go.Scatter(
                                        x=df_ind['Demo Date'],
                                        y=df_ind['Count of Demos'],
                                        mode='lines',
                                        text=df_ind['DateText'],
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

layout = update_layout

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



