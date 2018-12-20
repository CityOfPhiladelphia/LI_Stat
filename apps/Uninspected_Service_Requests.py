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
import os

from app import app, con
from config import MAPBOX_ACCESS_TOKEN

print(os.path.basename(__file__))

with con() as con:
    sql = 'SELECT * FROM li_stat_uninspectedservreq'
    df = pd.read_sql_query(sql=sql, con=con, parse_dates=['CALLDATE'])
    sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_UNINSPECTEDSERVREQ'"
    last_ddl_time = pd.read_sql_query(sql=sql, con=con)

#Create df of just the SLA lengths for each problem description. Just for documentation/help purposes.
df_sla_records = (df.drop(['SERVREQNO', 'ADDRESS', 'CALLDATE', 'UNIT', 'DISTRICT', 'LON', 'LAT'], axis=1)
                  .drop_duplicates()
                  .rename(columns={'PROBLEMDESCRIPTION': 'Problem Description', 'SLA': 'SLA Length(days)'})
                  .sort_values('Problem Description', ascending=True)
                  .to_dict('records'))

df.rename(columns=
            {'SERVREQNO': 'Service Request Num',
             'CALLDATE': 'Call Date',
             'PROBLEMDESCRIPTION': 'Problem Description',
             'UNIT': 'Unit',
             'DISTRICT': 'District'},
        inplace=True)

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

unique_within_sla = df['Within SLA'].unique()
unique_within_sla = np.append(['All'], unique_within_sla)


def update_sr_volume(selected_start, selected_end, selected_problem, selected_unit, selected_district, selected_within_sla):
    df_selected = df.copy(deep=True)

    if selected_problem != "All":
        df_selected = df_selected[(df_selected['Problem Description'] == selected_problem)]
    if selected_unit != "All":
        df_selected = df_selected[(df_selected['Unit'] == selected_unit)]
    if selected_district != "All":
        df_selected = df_selected[(df_selected['District'] == selected_district)]
    if selected_within_sla != "All":
        df_selected = df_selected[(df_selected['Within SLA'] == selected_within_sla)]

    df_selected = df_selected.loc[(df_selected['Call Date'] >= selected_start) & (df_selected['Call Date'] <= selected_end)]
    total_sr_volume = df_selected['Service Request Num'].count()
    return '{:,.0f}'.format(total_sr_volume)


def update_within_sla(selected_start, selected_end, selected_problem, selected_unit, selected_district, selected_within_sla):
    df_selected = df.copy(deep=True)

    if selected_problem != "All":
        df_selected = df_selected[(df_selected['Problem Description'] == selected_problem)]
    if selected_unit != "All":
        df_selected = df_selected[(df_selected['Unit'] == selected_unit)]
    if selected_district != "All":
        df_selected = df_selected[(df_selected['District'] == selected_district)]
    if selected_within_sla != "All":
        df_selected = df_selected[(df_selected['Within SLA'] == selected_within_sla)]

    df_selected = df_selected.loc[(df_selected['Call Date'] >= selected_start) & (df_selected['Call Date'] <= selected_end)]
    within_sla = len(df_selected[df_selected['Within SLA'] == 'Yes']) / len(df_selected) * 100
    return '{:,.0f}%'.format(within_sla)


def update_avg_days_out(selected_start, selected_end, selected_problem, selected_unit, selected_district, selected_within_sla):
    df_selected = df.copy(deep=True)

    if selected_problem != "All":
        df_selected = df_selected[(df_selected['Problem Description'] == selected_problem)]
    if selected_unit != "All":
        df_selected = df_selected[(df_selected['Unit'] == selected_unit)]
    if selected_district != "All":
        df_selected = df_selected[(df_selected['District'] == selected_district)]
    if selected_within_sla != "All":
        df_selected = df_selected[(df_selected['Within SLA'] == selected_within_sla)]

    df_selected = df_selected.loc[(df_selected['Call Date'] >= selected_start) & (df_selected['Call Date'] <= selected_end)]
    avg_days_out = df_selected['Bus. Days Outstanding'].mean()
    return '{:,.0f}'.format(avg_days_out)

def update_summary_table_data(selected_start, selected_end, selected_problem, selected_unit, selected_district, selected_within_sla):
    df_selected = df.copy(deep=True)

    if selected_problem != "All":
        df_selected = df_selected[(df_selected['Problem Description'] == selected_problem)].drop(['Problem Description'], axis=1)
    if selected_unit != "All":
        df_selected = df_selected[(df_selected['Unit'] == selected_unit)].drop(['Unit'], axis=1)
    if selected_district != "All":
        df_selected = df_selected[(df_selected['District'] == selected_district)].drop(['District'], axis=1)
    if selected_within_sla != "All":
        df_selected = df_selected[(df_selected['Within SLA'] == selected_within_sla)]

    possible_groupby_cols = ['Problem Description', 'Unit', 'District']
    col_list = list(df_selected.columns.values)
    groupby_cols = []
    for col in possible_groupby_cols:
        if col in col_list:
            groupby_cols.append(col)

    df_grouped = (df_selected.loc[(df_selected['Call Date'] >= selected_start) & (df_selected['Call Date'] <= selected_end)]
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

def update_table_data(selected_start, selected_end, selected_problem, selected_unit, selected_district, selected_within_sla):
    df_selected = df.copy(deep=True)

    if selected_problem != "All":
        df_selected = df_selected[(df_selected['Problem Description'] == selected_problem)]
    if selected_unit != "All":
        df_selected = df_selected[(df_selected['Unit'] == selected_unit)]
    if selected_district != "All":
        df_selected = df_selected[(df_selected['District'] == selected_district)]
    if selected_within_sla != "All":
        df_selected = df_selected[(df_selected['Within SLA'] == selected_within_sla)]

    df_selected = df_selected.loc[(df_selected['Call Date'] >= selected_start) & (df_selected['Call Date'] <= selected_end)]
    return df_selected.drop(['Call Date (no time)', 'SLA', 'LON', 'LAT'], axis=1)

def update_map_data(selected_start, selected_end, selected_problem, selected_unit, selected_district, selected_within_sla):
    df_selected = df.copy(deep=True)

    if selected_problem != "All":
        df_selected = df_selected[(df_selected['Problem Description'] == selected_problem)]
    if selected_unit != "All":
        df_selected = df_selected[(df_selected['Unit'] == selected_unit)]
    if selected_district != "All":
        df_selected = df_selected[(df_selected['District'] == selected_district)]
    if selected_within_sla != "All":
        df_selected = df_selected[(df_selected['Within SLA'] == selected_within_sla)]

    df_selected = df_selected.loc[(df_selected['Call Date'] >= selected_start) & (df_selected['Call Date'] <= selected_end)]
    return df_selected

layout = html.Div(children=[
                html.H1('Uninspected Service Requests', style={'text-align': 'center'}),
                html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
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
                    ], className='four columns'),
                    html.Div([
                        html.P('District'),
                        dcc.Dropdown(
                            id='district-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_districts],
                            value='All'
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Within SLA'),
                        dcc.Dropdown(
                            id='within-sla-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_within_sla],
                            value='All'
                        ),
                    ], className='four columns'),
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
                        dcc.Graph(
                            id='uninspected-sr-map',
                            config={
                                'displayModeBar': False
                            },
                              figure=go.Figure(
                                  data=[
                                      go.Scattermapbox(
                                          lon=df['LON'],
                                          lat=df['LAT'],
                                          mode='markers',
                                          marker=dict(
                                              size=14
                                          ),
                                          text='Address: ' + df['ADDRESS'].map(str) +
                                               '<br>' +
                                               'Problem: ' + df['Problem Description'].map(str) +
                                               '<br>' +
                                               'Unit: ' + df['Unit'].map(str) +
                                               '<br>' +
                                               'District: ' + df['District'].map(str) +
                                               '<br>' +
                                               'Call Date: ' + df['Call Date (no time)'].map(str) +
                                               '<br>' +
                                               'Within SLA: ' + df['Within SLA'].map(str),
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
                ], className='dashrow'),
                html.Details([
                    html.Summary('Query Description'),
                    html.Div([
                        html.P(
                            'Ops, Building, and CSU service requests with call dates since 1/1/16 that haven\'t been '
                            'inspected or resolved.'),
                        html.P('Problem codes by unit: '),
                        html.Ul(children=[
                            html.Li("Ops: 'BRH', 'DCC', 'DCR', 'DRGMR', 'FC', 'FR', 'HM', "
                            "'IR', 'LB', 'LR', 'LVCIP', 'MC', 'MR', 'NH', 'NPU', 'SMR', 'VC', 'VH', 'VRS', 'ZB', 'ZR'"),
                            html.Li("Building: 'BC', 'BLK', 'COMP', 'EC', 'LC', 'PC', 'SPC', 'SR311', 'X', 'ZC', 'ZM'"),
                            html.Li("District: 'BD', 'BDH', 'BDO'")
                        ]),
                        html.P(),
                        html.P(
                            "Avg. Days Outstanding: The average number of business days between call date and today."),
                        html.P(
                            "Business days: weekdays that aren't US Federal holidays."),
                        html.P(
                            "Within SLA: A service request is considered Within SLA if the number of business days it's "
                            "been outstanding is less than or equal to the SLA length for that type of problem. "),
                        html.P(),
                        html.Div([
                            html.Div([
                                html.H3('SLA Lengths', style={'text-align': 'center'}),
                                html.Div([
                                    table.DataTable(
                                        rows=df_sla_records,
                                        editable=False,
                                        sortable=True,
                                        filterable=True,
                                        min_width=500,
                                        id='sla-lengths-table'
                                    ),
                                ], style={'text-align': 'center'},
                                   id='sla-lengths-table-div'
                                ),
                            ], className='six columns'),
                        ], className='dashrow')
                    ])
                ])
            ])

@app.callback(
    Output('uninspected-sr-indicator', 'children'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value'),
     Input('within-sla-dropdown', 'value')])
def update_sr_indicator(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla):
    total_sr_volume = update_sr_volume(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla)
    return str(total_sr_volume)

@app.callback(
    Output('within-sla-indicator', 'children'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value'),
     Input('within-sla-dropdown', 'value')])
def update_within_sla_indicator(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla):
    within_sla = update_within_sla(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla)
    return str(within_sla)

@app.callback(
    Output('avg-days-out-indicator', 'children'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value'),
     Input('within-sla-dropdown', 'value')])
def update_avg_days_out_indicator(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla):
    avg_days_out = update_avg_days_out(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla)
    return str(avg_days_out)

@app.callback(
    Output('uninspected-sr-summary-table', 'rows'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value'),
     Input('within-sla-dropdown', 'value')])
def update_summary_table(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla):
    df_table = update_summary_table_data(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla)
    return df_table.to_dict('records')

@app.callback(
    Output('uninspected-sr-summary-table-download-link', 'href'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value'),
     Input('within-sla-dropdown', 'value')])
def update_summary_table_download_link(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla):
    df_table = update_summary_table_data(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla)
    csv_string = df_table.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(
    Output('uninspected-sr-map', 'figure'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value'),
     Input('within-sla-dropdown', 'value')])
def update_map(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla):
    df_results = update_map_data(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla)
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
                     'Problem: ' + df_results['Problem Description'].map(str) +
                     '<br>' +
                     'Unit: ' + df_results['Unit'].map(str) +
                     '<br>' +
                     'District: ' + df_results['District'].map(str) +
                     '<br>' +
                     'Call Date: ' + df_results['Call Date (no time)'].map(str) +
                     '<br>' +
                     'Within SLA: ' + df_results['Within SLA'].map(str),
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
    Output('uninspected-sr-table', 'rows'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value'),
     Input('within-sla-dropdown', 'value')])
def update_table(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla):
    df_table = update_table_data(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla)
    return df_table.to_dict('records')

@app.callback(
    Output('uninspected-sr-table-download-link', 'href'),
    [Input('uninspected-sr-call-date-picker-range', 'start_date'),
     Input('uninspected-sr-call-date-picker-range', 'end_date'),
     Input('problem-dropdown', 'value'),
     Input('unit-dropdown', 'value'),
     Input('district-dropdown', 'value'),
     Input('within-sla-dropdown', 'value')])
def update_table_download_link(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla):
    df_table = update_table_data(start_date, end_date, selected_problem, selected_unit, selected_district, selected_within_sla)
    csv_string = df_table.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string