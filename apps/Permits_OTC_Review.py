import os
from datetime import datetime, date
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
            sql = 'SELECT * FROM li_stat_permits_otcvsreview'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['ISSUEDATE'])
        elif dataset == 'last_ddl_time':
            sql = 'SELECT SCN_TO_TIMESTAMP(MAX(ora_rowscn)) last_ddl_time FROM LI_STAT_PERMITS_OTCVSREVIEW'
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def get_df_ind():
    df_ind = dataframe('df_ind')
    df_ind = (df_ind.rename(
                columns={
                    'ISSUEDATE': 'Issue Date', 
                    'PERMITDESCRIPTION': 'Permit Type', 
                    'TYPEOFWORK': 'Work Type', 
                    'COUNTOTCPERMITS': 'OTC Permits Issued', 
                    'COUNTREVIEWPERMITS': 'Reviewed Permits Issued'
                }))
    df_ind['Issue Date'] = pd.to_datetime(df_ind['Issue Date'])
    df_ind['DateText'] = df_ind['Issue Date'].dt.strftime('%b %Y')
    df_ind['Issue Date'] = df_ind['Issue Date'].map(lambda x: x.date())
    df_ind['Permit Type'] = df_ind['Permit Type'].astype(str)
    df_ind['Permit Type'] = df_ind['Permit Type'].map(lambda x: x.replace(" PERMIT", ""))
    df_ind['Permit Type'] = df_ind['Permit Type'].str.lower()
    df_ind['Permit Type'] = df_ind['Permit Type'].str.title()
    df_ind['Work Type'] = df_ind['Work Type'].fillna('None').astype(str)
    df_ind.sort_values(by='Issue Date', inplace=True)
    return df_ind

def get_last_ddl_time():
    last_ddl_time = dataframe('last_ddl_time')
    return last_ddl_time['LAST_DDL_TIME'].iloc[0]

def get_issue_dates(df_ind):
    issue_dates = df_ind['Issue Date'].unique()
    return issue_dates

def get_unique_permittypes(df_ind):
    unique_permittypes = df_ind['Permit Type'].unique()
    unique_permittypes.sort()
    unique_permittypes = np.append(['All'], unique_permittypes)
    return unique_permittypes

def get_unique_worktypes(df_ind):
    unique_worktypes = df_ind['Work Type'].unique()
    unique_worktypes.sort()
    unique_worktypes = np.append(['All'], unique_worktypes)
    return unique_worktypes

def get_total_otc_permit_volume(df_ind):
    return '{:,.0f}'.format(df_ind['OTC Permits Issued'].sum())

def get_total_review_permit_volume(df_ind):
    return '{:,.0f}'.format(df_ind['Reviewed Permits Issued'].sum())

def update_total_otc_permit_volume(selected_start, selected_end, selected_permittype, selected_worktype):
    df_selected = get_df_ind()

    start_date = datetime.strptime(selected_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(selected_end, "%Y-%m-%d").date()

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]
    if selected_worktype != "All":
        df_selected = df_selected[(df_selected['Work Type'] == selected_worktype)]

    df_selected = df_selected.loc[(df_selected['Issue Date'] >= start_date)&(df_selected['Issue Date'] <= end_date)]
    total_otc_permit_volume = df_selected['OTC Permits Issued'].sum()
    return '{:,.0f}'.format(total_otc_permit_volume)

def update_total_review_permit_volume(selected_start, selected_end, selected_permittype, selected_worktype):
    df_selected = get_df_ind()

    start_date = datetime.strptime(selected_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(selected_end, "%Y-%m-%d").date()

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]
    if selected_worktype != "All":
        df_selected = df_selected[(df_selected['Work Type'] == selected_worktype)]

    df_selected = df_selected.loc[(df_selected['Issue Date'] >= start_date)&(df_selected['Issue Date'] <= end_date)]
    total_review_permit_volume = df_selected['Reviewed Permits Issued'].sum()
    return '{:,.0f}'.format(total_review_permit_volume)

def update_counts_graph_data(selected_start, selected_end, selected_permittype, selected_worktype):
    df_selected = get_df_ind()
    issue_dates = get_issue_dates(df_selected)

    start_date = datetime.strptime(selected_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(selected_end, "%Y-%m-%d").date()

    selected_issue_dates = issue_dates[(issue_dates >= start_date) & (issue_dates <= end_date)]

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]
    if selected_worktype != "All":
        df_selected = df_selected[(df_selected['Work Type'] == selected_worktype)]

    df_selected = (df_selected.loc[(df_selected['Issue Date'] >= start_date) & (df_selected['Issue Date'] <= end_date)]
                              .groupby(by=['Issue Date', 'DateText'])['OTC Permits Issued', 'Reviewed Permits Issued']
                              .sum()
                              .reset_index())
    for month in selected_issue_dates:
        if month not in df_selected['Issue Date'].values:
            df_missing_month = pd.DataFrame([[month, month.strftime('%b %Y'), 0, 0]], columns=['Issue Date', 'DateText', 'OTC Permits Issued', 'Reviewed Permits Issued'])
            df_selected = df_selected.append(df_missing_month, ignore_index=True)
    df_selected['Issue Date'] = pd.Categorical(df_selected['Issue Date'], issue_dates)
    return df_selected.sort_values(by='Issue Date')

def update_counts_table_data(selected_start, selected_end, selected_permittype, selected_worktype):
    df_selected = get_df_ind()

    start_date = datetime.strptime(selected_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(selected_end, "%Y-%m-%d").date()
    
    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]
    if selected_worktype != "All":
        df_selected = df_selected[(df_selected['Work Type'] == selected_worktype)]

    df_selected = (df_selected.loc[(df_selected['Issue Date']>=start_date) & (df_selected['Issue Date']<=end_date)]
                              .groupby(by=['Issue Date', 'Permit Type', 'Work Type'])['OTC Permits Issued', 'Reviewed Permits Issued']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Issue Date', 'Permit Type', 'Work Type']))
    df_selected['Issue Date'] = df_selected['Issue Date'].apply(lambda x: datetime.strftime(x, '%b %Y'))
    df_selected['OTC Permits Issued'] = df_selected['OTC Permits Issued'].map('{:,.0f}'.format)
    df_selected['Reviewed Permits Issued'] = df_selected['Reviewed Permits Issued'].map('{:,.0f}'.format)
    return df_selected

def update_layout():
    last_ddl_time = get_last_ddl_time()
    df_ind = get_df_ind()
    issue_dates = get_issue_dates(df_ind)
    unique_permittypes = get_unique_permittypes(df_ind)
    unique_worktypes = get_unique_worktypes(df_ind)
    total_otc_permit_volume = get_total_otc_permit_volume(df_ind)
    total_review_permit_volume = get_total_review_permit_volume(df_ind)

    return html.Div(children=[
                html.H1('Permits Issued: Over the Counter (OTC) vs Back Office (Reviewed)', style={'text-align': 'center'}),
                html.P(f"Data last updated {last_ddl_time}", style = {'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Issue Date'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='slide3-permits-date-picker-range',
                            start_date=datetime(2016, 1, 1),
                            end_date=date.today()
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by Permit Type'),
                        dcc.Dropdown(
                                id='slide3-permits-permittype-dropdown',
                                options=[{'label': k, 'value': k} for k in unique_permittypes],
                                value='All'
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by Work Type'),
                        dcc.Dropdown(
                            id='slide3-permits-worktype-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_worktypes],
                            value='All'
                        ),
                    ], className='four columns'),
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='slide3-permits-graph',
                            config={
                                'displayModeBar': False
                            },
                            figure=go.Figure(
                                data=[
                                    go.Scatter(
                                        x=df_ind['Issue Date'],
                                        y=df_ind['OTC Permits Issued'],
                                        mode='lines',
                                        text=df_ind['DateText'],
                                        hoverinfo='text+y',
                                        line=dict(
                                            shape='spline',
                                            color='rgb(26, 118, 255)'
                                        ),
                                        name='OTC'
                                    ),
                                    go.Scatter(
                                        x=df_ind['Issue Date'],
                                        y=df_ind['Reviewed Permits Issued'],
                                        mode='lines',
                                        text=df_ind['DateText'],
                                        hoverinfo='text+y',
                                        line=dict(
                                            shape='spline',
                                            color='#ff7f0e'
                                        ),
                                        name='Reviewed'
                                    )
                                ],
                                layout=go.Layout(
                                    title='Permits Issued: OTC vs Reviewed',
                                    yaxis=dict(
                                        title='Permits Issued'
                                    )
                                )
                            )
                        )
                    ], className='twelve columns'),
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H1('', id='slide3-otcpermits-indicator', style={'font-size': '35pt'}),
                        html.H2('OTC Permits Issued', style={'font-size': '30pt'})
                    ], className='six columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'}),
                    html.Div([
                        html.H1('', id='slide3-reviewpermits-indicator', style={'font-size': '35pt'}),
                        html.H2('Reviewed Permits Issued', style={'font-size': '30pt'})
                    ], className='six columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H3('Permits Issued', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                columns=['Issue Date', 'Permit Type', 'Work Type', 'OTC Permits Issued', 'Reviewed Permits Issued'],
                                editable=False,
                                sortable=True,
                                id='slide3-permits-count-table'
                            ),
                        ], style={'text-align': 'center'},
                           id='slide3-permits-count-table-div'
                        ),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='slide3-permits-count-table-download-link',
                                download='slide3_permit_volumes_counts.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'width': '80%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow'),
                html.Details([
                    html.Summary('Query Description'),
                    html.Div([
                        html.P(
                            'Permits applied for since 1/1/16 that don\'t have a parent-child relationship. Grouped by '
                            'whether they were processed OTC (over-the-counter) or went back for Review:'),
                        html.P(
                            'OTC: When the processing date equals the issue date'),
                        html.P(
                            'Review: All the other permits, i.e. ones where the application/processing date does not '
                            'equal the issue date.')
                    ])
                ])
            ])

layout = update_layout

@app.callback(
    Output('slide3-permits-graph', 'figure'),
    [Input('slide3-permits-date-picker-range', 'start_date'),
     Input('slide3-permits-date-picker-range', 'end_date'),
     Input('slide3-permits-permittype-dropdown', 'value'),
     Input('slide3-permits-worktype-dropdown', 'value')])
def update_graph(start_date, end_date, permittype, worktype):
    df_updated = update_counts_graph_data(start_date, end_date, permittype, worktype)
    return {
        'data': [
            go.Scatter(
                x=df_updated['Issue Date'],
                y=df_updated['OTC Permits Issued'],
                mode='lines',
                text=df_updated['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                ),
                name='OTC'
            ),
            go.Scatter(
                x=df_updated['Issue Date'],
                y=df_updated['Reviewed Permits Issued'],
                mode='lines',
                text=df_updated['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='#ff7f0e'
                ),
                name='Reviewed'
            )
        ],
        'layout': go.Layout(
            title='Permits Issued: OTC vs Reviewed',
            yaxis=dict(
                title='Permits Issued',
                range=[0, (df_updated['OTC Permits Issued'].max() + (df_updated['OTC Permits Issued'].max()/50)) if (df_updated['OTC Permits Issued'].max() > df_updated['Reviewed Permits Issued'].max()) else (df_updated['Reviewed Permits Issued'].max() + (df_updated['Reviewed Permits Issued'].max()/50))]
            )
        )
    }

@app.callback(
    Output('slide3-otcpermits-indicator', 'children'),
    [Input('slide3-permits-date-picker-range', 'start_date'),
     Input('slide3-permits-date-picker-range', 'end_date'),
     Input('slide3-permits-permittype-dropdown', 'value'),
     Input('slide3-permits-worktype-dropdown', 'value')])
def update_total_otcpermits_volume_indicator(start_date, end_date, permittype, worktype):
    total_permit_volume = update_total_otc_permit_volume(start_date, end_date, permittype, worktype)
    return str(total_permit_volume)

@app.callback(
    Output('slide3-reviewpermits-indicator', 'children'),
    [Input('slide3-permits-date-picker-range', 'start_date'),
     Input('slide3-permits-date-picker-range', 'end_date'),
     Input('slide3-permits-permittype-dropdown', 'value'),
     Input('slide3-permits-worktype-dropdown', 'value')])
def update_total_reviewpermits_indicator(start_date, end_date, permittype, worktype):
    total_fees_paid = update_total_review_permit_volume(start_date, end_date, permittype, worktype)
    return str(total_fees_paid)

@app.callback(
    Output('slide3-permits-count-table', 'rows'),
    [Input('slide3-permits-date-picker-range', 'start_date'),
     Input('slide3-permits-date-picker-range', 'end_date'),
     Input('slide3-permits-permittype-dropdown', 'value'),
     Input('slide3-permits-worktype-dropdown', 'value')])
def update_count_table(start_date, end_date, permittype, worktype):
    df_updated = update_counts_table_data(start_date, end_date, permittype, worktype)
    return df_updated.to_dict('records')

@app.callback(
    Output('slide3-permits-count-table-download-link', 'href'),
    [Input('slide3-permits-date-picker-range', 'start_date'),
     Input('slide3-permits-date-picker-range', 'end_date'),
     Input('slide3-permits-permittype-dropdown', 'value'),
     Input('slide3-permits-worktype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, permittype, worktype):
    df_updated = update_counts_table_data(start_date, end_date, permittype, worktype)
    csv_string = df_updated.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string