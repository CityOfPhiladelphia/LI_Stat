import os
from datetime import datetime
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
            sql = 'SELECT * FROM li_stat_permits_accelreview'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['PERMITAPPLICATIONDATE', 'PERMITISSUEDATE',
                                                                        'REVIEWISSUEDATE', 'PAIDDTTM'])
            df = (df.rename(columns={'APNO': 'Permit Number', 'PERMITAPPLICATIONDATE': 'Permit Application Date',
                                     'PERMITISSUEDATE': 'Permit Issue Date', 'SLACOMPLIANCE': 'SLA Compliance',
                                     'PERMITDESCRIPTION': 'Permit Type', 'WORKTYPE': 'Work Type'}))

            df['Permit Type'] = df['Permit Type'].astype(str)
            df['Permit Type'] = df['Permit Type'].map(lambda x: x.replace(" PERMIT", ""))
            df['Permit Type'] = df['Permit Type'].str.lower()
            df['Permit Type'] = df['Permit Type'].str.title()
            df['Work Type'] = df['Work Type'].fillna('None').astype(str)
        elif dataset == 'last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_PERMITS_ACCELREVIEW'"
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def get_df_ind():
    df = dataframe('df_ind')
    return df

def get_last_ddl_time():
    df = dataframe('last_ddl_time')
    df = df['LAST_DDL_TIME'].iloc[0]
    return df

def get_unique_permittypes():
    df = get_df_ind()
    unique_permittypes = df['Permit Type'].unique()
    unique_permittypes.sort()
    unique_permittypes = np.append(['All'], unique_permittypes)
    return unique_permittypes

def get_unique_worktypes():
    df = get_df_ind()
    unique_worktypes = df['Work Type'].unique()
    unique_worktypes.sort()
    unique_worktypes = np.append(['All'], unique_worktypes)
    return unique_worktypes

def get_null_hours():
    df = get_df_ind()
    null_hour_values = df['HOURS'].isna().sum()
    return null_hour_values

def get_zero_hour_values():
    df = get_df_ind()
    zero_hour_values = (df['HOURS']==0).sum()
    return zero_hour_values

def get_records_count():
    df = get_df_ind()
    records = len(df)
    return records

def update_table_data(selected_start, selected_end, selected_permittype, selected_worktype):
    df_selected = get_df_ind()

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]
    if selected_worktype != "All":
        df_selected = df_selected[(df_selected['Work Type'] == selected_worktype)]

    df_selected_grouped = (df_selected.loc[(df_selected['Permit Issue Date'] >= selected_start) & (df_selected['Permit Issue Date'] <= selected_end)]
                            .groupby('SLA Compliance')
                            .agg({'Permit Number': 'count', 'HOURS': 'mean'})
                            .reset_index()
                            .rename(columns={'Permit Number': '# of Accel. Reviews', 'HOURS': 'Avg. Hours Per Review [1]'}))
    df_selected_grouped['Avg. Hours Per Review [1]'] = df_selected_grouped['Avg. Hours Per Review [1]'].map('{:,.2f}'.format)
    df_selected_grouped['% of Total'] = df_selected_grouped['# of Accel. Reviews'] / len(df_selected) * 100
    df_selected_grouped['% of Total'] = df_selected_grouped['% of Total'].round(0).map('{:,.0f}%'.format)
    df_selected_grouped['# of Accel. Reviews'] = df_selected_grouped['# of Accel. Reviews'].map('{:,.0f}'.format)
    return df_selected_grouped.sort_values(by=['SLA Compliance'])

def update_footnote(selected_start, selected_end, selected_permittype, selected_worktype):
    df_selected = get_df_ind()

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]
    if selected_worktype != "All":
        df_selected = df_selected[(df_selected['Work Type'] == selected_worktype)]
    df_selected = df_selected.loc[(df_selected['Permit Issue Date'] >= selected_start) & (df_selected['Permit Issue Date'] <= selected_end)]

    records = len(df_selected)
    if records > 0:
        null_hour_values = df_selected['HOURS'].isna().sum()
        zero_hour_values = (df_selected['HOURS'] == 0).sum()
        return '[1] Only ' + str('{:,.0f}%'.format(round(null_hour_values / records * 100, 0))) + \
                ' of these accelerated reviews had recorded hour values. And ' + \
                str('{:,.0f}%'.format(round(zero_hour_values / records * 100, 0))) + \
                ' had values of 0. Which means ' + \
                str('{:,.0f}%'.format(round((records - (null_hour_values + zero_hour_values)) / records * 100, 0))) + \
                ' (' + str('{:,.0f}'.format(round((records - (null_hour_values + zero_hour_values)), 0))) + ') had non-zero values.'
    else:
        return '[1] No records'

def update_layout():
    last_ddl_time = get_last_ddl_time()
    unique_permittypes = get_unique_permittypes()
    unique_worktypes = get_unique_worktypes()

    return html.Div(children=[
                    html.H1('Accelerated Reviews', style={'text-align': 'center'}),
                    html.P(f"Data last updated {last_ddl_time}", style = {'text-align': 'center'}),
                    html.Div([
                        html.Div([
                            html.P('Filter by Permit Application Date'),
                            dcc.DatePickerRange(
                                display_format='MMM Y',
                                id='slide5-permits-date-picker-range',
                                start_date=datetime(2016, 1, 1),
                                end_date=datetime.now()
                            ),
                        ], className='four columns'),
                        html.Div([
                            html.P('Filter by Permit Type'),
                            dcc.Dropdown(
                                    id='slide5-permits-permittype-dropdown',
                                    options=[{'label': k, 'value': k} for k in unique_permittypes],
                                    value='All'
                            ),
                        ], className='four columns'),
                        html.Div([
                            html.P('Filter by Work Type'),
                            dcc.Dropdown(
                                id='slide5-permits-worktype-dropdown',
                                options=[{'label': k, 'value': k} for k in unique_worktypes],
                                value='All'
                            ),
                        ], className='four columns'),
                    ], className='dashrow filters'),
                    html.Div([
                        html.Div([
                            html.H3('Accelerated Reviews', style={'text-align': 'center'}),
                            html.Div([
                                table.DataTable(
                                    rows=[{}],
                                    columns=['SLA Compliance', '# of Accel. Reviews', '% of Total', 'Avg. Hours Per Review [1]'],
                                    editable=False,
                                    sortable=True,
                                    id='slide5-permits-count-table'
                                ),
                            ], style={'text-align': 'center'},
                            id='slide5-permits-count-table-div'
                            ),
                            html.Div([
                                html.A(
                                    'Download Data',
                                    id='slide5-permits-count-table-download-link',
                                    download='slide5_permit_volumes_counts.csv',
                                    href='',
                                    target='_blank',
                                )
                            ], style={'text-align': 'right'})
                        ], style={'width': '70%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '50px', 'margin-bottom': '50px'})
                    ], className='dashrow'),
                    html.Div([
                        html.P(
                            style={'text-align': 'center'},
                            id='footnote'
                        )
                    ]),
                    html.Details([
                        html.Summary('Query Description'),
                        html.Div([
                            html.P(
                                'Permits applied for since 1/1/16 that have been issued and have paid an accelerated fee.'),
                            html.P(
                                'Within SLA: When the permit was issued within 10 days or less of when it was applied for.'),
                            html.P(
                                'Outside SLA: When the permit was issued 10 days or longer from when it was applied for.'),
                            html.P(
                                'Avg. Hours Per Review: This data comes from the Hours field in the Supplementary -> Log tab in Hansen.'),
                        ])
                    ])
    ])

layout = update_layout

@app.callback(
    Output('slide5-permits-count-table', 'rows'),
    [Input('slide5-permits-date-picker-range', 'start_date'),
     Input('slide5-permits-date-picker-range', 'end_date'),
     Input('slide5-permits-permittype-dropdown', 'value'),
     Input('slide5-permits-worktype-dropdown', 'value')])
def update_table(start_date, end_date, permittype, worktype):
    df_updated = update_table_data(start_date, end_date, permittype, worktype)
    return df_updated.to_dict('records')

@app.callback(
    Output('slide5-permits-count-table-download-link', 'href'),
    [Input('slide5-permits-date-picker-range', 'start_date'),
     Input('slide5-permits-date-picker-range', 'end_date'),
     Input('slide5-permits-permittype-dropdown', 'value'),
     Input('slide5-permits-worktype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, permittype, worktype):
    df_updated = update_table_data(start_date, end_date, permittype, worktype)
    csv_string = df_updated.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(
    Output('footnote', 'children'),
    [Input('slide5-permits-date-picker-range', 'start_date'),
     Input('slide5-permits-date-picker-range', 'end_date'),
     Input('slide5-permits-permittype-dropdown', 'value'),
     Input('slide5-permits-worktype-dropdown', 'value')])
def update_footnote_text(start_date, end_date, permittype, worktype):
    return update_footnote(start_date, end_date, permittype, worktype)

