import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
import datetime
import numpy as np
import urllib.parse
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

from app import app, con_GISLNI

testing_mode = False
print('UninspectedServiceRequests.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('test_data/UninspectedServiceRequests.csv', parse_dates=['Call Date'])

else:
    with con_GISLNI() as con_GISLNI:
        with open(r'queries/UninspectedServiceRequests.sql') as sql:
            df = pd.read_sql_query(sql=sql.read(), con=con_GISLNI, parse_dates=['Call Date'])

#Determine which service requests are within SLA and how long they've been outstanding
df['Call Date (no time)'] = df['Call Date'].dt.date
today = datetime.date.today()
us_bd = CustomBusinessDay(calendar=USFederalHolidayCalendar())
def calc_bus_days(row):
    row['Bus. Days Outstanding'] = pd.DatetimeIndex(start=row['Call Date (no time)'], end=today, freq=us_bd).shape[0] - 1
    return row['Bus. Days Outstanding']
df['Bus. Days Outstanding'] = df[df['Call Date (no time)'].notnull()].apply(calc_bus_days, axis=1)
df['Within SLA'] = np.where(df['Bus. Days Outstanding'] > df['SLA'], 'No', 'Yes')
df['Bus. Days Overdue'] = np.where(df['Within SLA'] == 'No', df['Bus. Days Outstanding'] - df['SLA'], 'N/A')

unique_problems = df['Problem Description'].unique()
unique_problems = np.append(['All'], unique_problems)

unique_units = df['Unit'].unique()
unique_units = np.append(['All'], unique_units)

unique_districts = df['District'].unique()
unique_districts = np.append(['All'], unique_districts)

def update_sr_volume(selected_start, selected_end, selected_problem, selected_unit, selected_district):
    df_selected = df.copy(deep=True)

    if selected_problem != "All":
        df_selected = df_selected[(df_selected['Problem Description'] == selected_problem)]
    if selected_unit != "All":
        df_selected = df_selected[(df_selected['Unit'] == selected_unit)]
    if selected_district != "All":
        df_selected = df_selected[(df_selected['District'] == selected_district)]

    df_selected = df_selected.loc[(df['Call Date'] >= selected_start) & (df_selected['Call Date'] <= selected_end)]
    total_sr_volume = df_selected['Service Request Num'].count()
    return '{:,.0f}'.format(total_sr_volume)


def update_within_sla(selected_start, selected_end, selected_problem, selected_unit, selected_district):
    df_selected = df.copy(deep=True)

    if selected_problem != "All":
        df_selected = df_selected[(df_selected['Problem Description'] == selected_problem)]
    if selected_unit != "All":
        df_selected = df_selected[(df_selected['Unit'] == selected_unit)]
    if selected_district != "All":
        df_selected = df_selected[(df_selected['District'] == selected_district)]

    df_selected = df_selected.loc[(df['Call Date'] >= selected_start) & (df_selected['Call Date'] <= selected_end)]
    within_sla = len(df_selected[df_selected['Within SLA'] == 'Yes']) / len(df_selected) * 100
    return '{:,.0f}%'.format(within_sla)


def update_avg_days_out(selected_start, selected_end, selected_problem, selected_unit, selected_district):
    df_selected = df.copy(deep=True)

    if selected_problem != "All":
        df_selected = df_selected[(df_selected['Problem Description'] == selected_problem)]
    if selected_unit != "All":
        df_selected = df_selected[(df_selected['Unit'] == selected_unit)]
    if selected_district != "All":
        df_selected = df_selected[(df_selected['District'] == selected_district)]

    df_selected = df_selected.loc[(df['Call Date'] >= selected_start) & (df_selected['Call Date'] <= selected_end)]
    avg_days_out = df_selected['Bus. Days Outstanding'].mean()
    return '{:,.0f}'.format(avg_days_out)

def update_summary_table_data(selected_start, selected_end, selected_problem, selected_unit, selected_district):
    df_selected = df.copy(deep=True)

    if selected_problem != "All":
        df_selected = df_selected[(df_selected['Problem Description'] == selected_problem)].drop(['Problem Description'], axis=1)
    if selected_unit != "All":
        df_selected = df_selected[(df_selected['Unit'] == selected_unit)].drop(['Unit'], axis=1)
    if selected_district != "All":
        df_selected = df_selected[(df_selected['District'] == selected_district)].drop(['District'], axis=1)

    possible_groupby_cols = ['Problem Description', 'Unit', 'District']
    col_list = list(df_selected.columns.values)
    groupby_cols = []
    for col in possible_groupby_cols:
        if col in col_list:
            groupby_cols.append(col)

    df_grouped = (df_selected.loc[(df['Call Date'] >= selected_start) & (df_selected['Call Date'] <= selected_end)]
                   .groupby(groupby_cols)
                   .agg({'Service Request Num': 'count',
                         'Within SLA': lambda x: df_selected.loc[x.index, 'Within SLA'][x=='Yes'].count(),
                         'Bus. Days Outstanding': 'mean'})
                   .reset_index()
                   .rename(columns={'Service Request Num': 'Service Requests', 'Within SLA': '# Within SLA',
                                    'Bus. Days Outstanding': 'Avg. Bus. Days Outstanding'}))
    df_grouped['% Within SLA'] = df_grouped['# Within SLA'] / df_grouped['Service Requests'] * 100
    df_grouped['% Within SLA'] = df_grouped['% Within SLA'].round(0).map('{:,.0f}%'.format)
    df_grouped['Avg. Bus. Days Outstanding'] = df_grouped['Avg. Bus. Days Outstanding'].map('{:,.0f}'.format)
    return df_grouped.drop('# Within SLA', axis=1)

def update_table_data(selected_start, selected_end, selected_problem, selected_unit, selected_district):
    df_selected = df.copy(deep=True)

    if selected_problem != "All":
        df_selected = df_selected[(df_selected['Problem Description'] == selected_problem)]
    if selected_unit != "All":
        df_selected = df_selected[(df_selected['Unit'] == selected_unit)]
    if selected_district != "All":
        df_selected = df_selected[(df_selected['District'] == selected_district)]

    df_selected = df_selected.loc[(df['Call Date'] >= selected_start) & (df_selected['Call Date'] <= selected_end)]
    return df_selected.drop(['Call Date (no time)', 'SLA'], axis=1)

layout = html.Div(children=[
                html.H1('Uninspected Service Requests', style={'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Call Date'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='uninspected-sr-call-date-picker-range',
                            start_date=datetime.datetime(2016, 1, 1),
                            end_date=datetime.datetime.now()
                        ),
                    ], className='six columns'),
                    html.Div([
                        html.P('Problem'),
                        dcc.Dropdown(
                            id='problem-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_problems],
                            value='All'
                        ),
                    ], className='six columns')
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        html.P('Unit'),
                        dcc.Dropdown(
                            id='unit-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_units],
                            value='All'
                        ),
                    ], className='five columns'),
                    html.Div([
                        html.P('District'),
                        dcc.Dropdown(
                            id='district-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_districts],
                            value='All'
                        ),
                    ], className='five columns'),
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        html.H2('', id='uninspected-sr-indicator', style={'font-size': '25pt'}),
                        html.H3('Uninspected Service Requests', style={'font-size': '20pt'})
                    ], className='four columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '25px 0'}),
                    html.Div([
                        html.H2('', id='within-sla-indicator', style={'font-size': '25pt'}),
                        html.H3('Within SLA', style={'font-size': '20pt'})
                    ], className='four columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '25px 0'}),
                    html.Div([
                        html.H2('', id='avg-days-out-indicator', style={'font-size': '25pt'}),
                        html.H3('Avg. Days Outstanding', style={'font-size': '20pt'})
                    ], className='four columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '25px 0'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H3('Summary Table', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                editable=False,
                                sortable=True,
                                id='uninspected-sr-summary-table'
                            ),
                        ], style={'text-align': 'center'},
                           id='uninspected-sr-summary-table-div'
                        ),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='uninspected-sr-summary-table-download-link',
                                download='uninspected-sr-summary.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], className='twelve columns', style={'margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H3('Individual Service Requests', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                editable=False,
                                sortable=True,
                                filterable=True,
                                id='uninspected-sr-table'
                            ),
                        ], style={'text-align': 'center'},
                           id='uninspected-sr-table-div'
                        ),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='uninspected-sr-table-download-link',
                                download='uninspected-sr.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], className='twelve columns', style={'margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow')
            ])

@app.callback(
    Output('uninspected-sr-indicator', 'children'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value')])
def update_sr_indicator(start_date, end_date, selected_problem, selected_unit, selected_district):
    total_sr_volume = update_sr_volume(start_date, end_date, selected_problem, selected_unit, selected_district)
    return str(total_sr_volume)

@app.callback(
    Output('within-sla-indicator', 'children'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value')])
def update_within_sla_indicator(start_date, end_date, selected_problem, selected_unit, selected_district):
    within_sla = update_within_sla(start_date, end_date, selected_problem, selected_unit, selected_district)
    return str(within_sla)

@app.callback(
    Output('avg-days-out-indicator', 'children'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value')])
def update_avg_days_out_indicator(start_date, end_date, selected_problem, selected_unit, selected_district):
    avg_days_out = update_avg_days_out(start_date, end_date, selected_problem, selected_unit, selected_district)
    return str(avg_days_out)

@app.callback(
    Output('uninspected-sr-summary-table', 'rows'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value')])
def update_summary_table(start_date, end_date, selected_problem, selected_unit, selected_district):
    df_table = update_summary_table_data(start_date, end_date, selected_problem, selected_unit, selected_district)
    return df_table.to_dict('records')

@app.callback(
    Output('uninspected-sr-summary-table-download-link', 'href'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value')])
def update_summary_table_download_link(start_date, end_date, selected_problem, selected_unit, selected_district):
    df_table = update_summary_table_data(start_date, end_date, selected_problem, selected_unit, selected_district)
    csv_string = df_table.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(
    Output('uninspected-sr-table', 'rows'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value')])
def update_table(start_date, end_date, selected_problem, selected_unit, selected_district):
    df_table = update_table_data(start_date, end_date, selected_problem, selected_unit, selected_district)
    return df_table.to_dict('records')

@app.callback(
    Output('uninspected-sr-table-download-link', 'href'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value')])
def update_table_download_link(start_date, end_date, selected_problem, selected_unit, selected_district):
    df_table = update_table_data(start_date, end_date, selected_problem, selected_unit, selected_district)
    csv_string = df_table.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string