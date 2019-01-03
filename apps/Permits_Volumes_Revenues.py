import os
from datetime import datetime
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
            sql = 'SELECT * FROM li_stat_permitsfees'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['ISSUEDATE'])
        elif dataset == 'last_ddl_time':
            sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_PERMITSFEES'"
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def get_last_ddl_time():
    last_ddl_time = dataframe('last_ddl_time')
    return last_ddl_time['LAST_DDL_TIME'].iloc[0]

def get_permits():
    permits = dataframe('df_ind')
    permits['ISSUEDATE'] = pd.to_datetime(permits['ISSUEDATE'])
    permits = (permits.rename(columns={'ISSUEDATE': 'Issue Date', 'PERMITDESCRIPTION': 'Permit Type', 'COUNTPERMITS': 'Permits Issued', 'TOTALFEESPAID': 'Fees Paid'})
        .assign(DateText=lambda x: x['Issue Date'].dt.strftime('%b %Y')))
    permits['Fees Paid'] = pd.to_numeric(permits['Fees Paid'])
    permits['Permit Type'] = permits['Permit Type'].map(lambda x: x.replace(" PERMIT", ""))
    permits['Permit Type'] = permits['Permit Type'].str.lower()
    permits['Permit Type'] = permits['Permit Type'].str.title()
    return permits

def get_unique_permittypes(permits):
    unique_permittypes = permits['Permit Type'].unique()
    unique_permittypes = np.append(['All'], unique_permittypes)
    return unique_permittypes

def get_total_permit_volume(permits):
    return '{:,.0f}'.format(permits['Permits Issued'].sum())

def get_total_permit_feespaid(permits):
    return '{:,.0f}'.format(permits['Fees Paid'].sum())

def update_total_permit_volume(selected_start, selected_end, selected_permittype):
    df_selected = get_permits()

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]

    df_selected = df_selected.loc[(df_selected['Issue Date'] >= selected_start)&(df_selected['Issue Date'] <= selected_end)]
    total_permit_volume = df_selected['Permits Issued'].sum()
    return '{:,.0f}'.format(total_permit_volume)

def update_total_fees_paid(selected_start, selected_end, selected_permittype):
    df_selected = get_permits()

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]

    df_selected = df_selected.loc[(df_selected['Issue Date'] >= selected_start)&(df_selected['Issue Date'] <= selected_end)]
    total_fees_paid = df_selected['Fees Paid'].sum()
    return '${:,.0f}'.format(total_fees_paid)

def update_counts_graph_data(selected_start, selected_end, selected_permittype):
    df_selected = get_permits()

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]

    df_selected = (df_selected.loc[(df_selected['Issue Date'] >= selected_start) & (df_selected['Issue Date'] <= selected_end)]
                              .groupby(by=['Issue Date', 'DateText'])['Permits Issued', 'Fees Paid']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Issue Date']))
    return df_selected

def update_counts_table_data(selected_start, selected_end, selected_permittype):
    df_selected = get_permits()

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]

    df_selected = (df_selected.loc[(df_selected['Issue Date']>=selected_start) & (df_selected['Issue Date']<=selected_end)]
                              .groupby(by=['Issue Date', 'Permit Type'])['Permits Issued', 'Fees Paid']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Issue Date', 'Permit Type']))
    df_selected['Issue Date'] = df_selected['Issue Date'].apply(lambda x: datetime.strftime(x, '%b %Y'))
    df_selected['Permits Issued'] = df_selected['Permits Issued'].map('{:,.0f}'.format)
    df_selected['Fees Paid'] = df_selected['Fees Paid'].map('${:,.0f}'.format)
    return df_selected

def update_layout():
    last_ddl_time = get_last_ddl_time()
    permits = get_permits()
    unique_permittypes = get_unique_permittypes(permits)
    total_permit_volume = get_total_permit_volume(permits)
    total_fees_paid = get_total_permit_feespaid(permits)

    return html.Div(children=[
                html.H1('Permit Volumes and Revenues', style={'text-align': 'center'}),
                html.P(f"Data last updated {last_ddl_time}", style = {'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Issue Date'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='slide1-permits-date-picker-range',
                            start_date=datetime(2016, 1, 1),
                            end_date=datetime.now()
                        ),
                    ], className='six columns'),
                    html.Div([
                        html.P('Filter by Permit Type'),
                        dcc.Dropdown(
                                id='slide1-permits-permittype-dropdown',
                                options=[{'label': k, 'value': k} for k in unique_permittypes],
                                value='All'
                        ),
                    ], className='five columns'),
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='slide1-permits-graph',
                            config={
                                'displayModeBar': False
                            },
                            figure=go.Figure(
                                data=[
                                    go.Scatter(
                                        x=permits['Issue Date'],
                                        y=permits['Permits Issued'],
                                        mode='lines',
                                        text=permits['DateText'],
                                        hoverinfo='text+y',
                                        line=dict(
                                            shape='spline',
                                            color='rgb(26, 118, 255)'
                                        ),
                                        name='Permits Issued'
                                    ),
                                    go.Scatter(
                                        x=permits['Issue Date'],
                                        y=permits['Fees Paid'],
                                        mode='lines',
                                        text=permits['DateText'],
                                        hoverinfo='text+y',
                                        line=dict(
                                            shape='spline',
                                            color='#ff7f0e'
                                        ),
                                        name='Fees Paid ($)',
                                        yaxis='y2'
                                    )
                                ],
                                layout=go.Layout(
                                    title='Permits Issued vs Fees Paid',
                                    yaxis=dict(
                                        title='Permits Issued'
                                    ),
                                    yaxis2=dict(
                                        title='Fees Paid ($)',
                                        titlefont=dict(
                                            color='#ff7f0e'
                                        ),
                                        tickfont=dict(
                                            color='#ff7f0e'
                                        ),
                                        overlaying='y',
                                        side='right'
                                    )
                                )
                            )
                        )
                    ], className='twelve columns'),
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H1('', id='slide1-permits-indicator', style={'font-size': '35pt'}),
                        html.H2('Permits Issued', style={'font-size': '30pt'})
                    ], className='six columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'}),
                    html.Div([
                        html.H1('', id='slide1-feespaid-indicator', style={'font-size': '35pt'}),
                        html.H2('Fees Paid', style={'font-size': '30pt'})
                    ], className='six columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H3('Permits Issued and Fees Paid By Type and Month', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                columns=['Issue Date', 'Permit Type', 'Permits Issued', 'Fees Paid'],
                                editable=False,
                                sortable=True,
                                id='slide1-permits-count-table'
                            ),
                        ], style={'text-align': 'center'},
                           id='slide1-permits-count-table-div'
                        ),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='slide1-permits-count-table-download-link',
                                download='slide1_permit_volumes_counts.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'width': '65%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow'),
                html.Details([
                    html.Summary('Query Description'),
                    html.Div([
                        html.P(
                            'Permits (with paid fees) issued since 1/1/2016.'),
                    ])
                ])
            ])

layout = update_layout

@app.callback(
    Output('slide1-permits-graph', 'figure'),
    [Input('slide1-permits-date-picker-range', 'start_date'),
     Input('slide1-permits-date-picker-range', 'end_date'),
     Input('slide1-permits-permittype-dropdown', 'value')])
def update_graph(start_date, end_date, permittype):
    dfr = update_counts_graph_data(start_date, end_date, permittype)
    return {
        'data': [
            go.Scatter(
                x=dfr['Issue Date'],
                y=dfr['Permits Issued'],
                mode='lines',
                text=dfr['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                ),
                name='Permits Issued'
            ),
            go.Scatter(
                x=dfr['Issue Date'],
                y=dfr['Fees Paid'],
                mode='lines',
                text=dfr['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='#ff7f0e'
                ),
                name='Fees Paid ($)',
                yaxis='y2'
            )
        ],
        'layout': go.Layout(
            title='Permits Issued vs Fees Paid',
            yaxis=dict(
                title='Permits Issued',
                range=[0, dfr['Permits Issued'].max() + (dfr['Permits Issued'].max() / 50)]
            ),
            yaxis2=dict(
                title='Fees Paid ($)',
                range=[0, dfr['Fees Paid'].max() + (dfr['Fees Paid'].max() / 50)],
                titlefont=dict(
                    color='#ff7f0e'
                ),
                tickfont=dict(
                    color='#ff7f0e'
                ),
                overlaying='y',
                side='right'
            )
        )
    }

@app.callback(
    Output('slide1-permits-indicator', 'children'),
    [Input('slide1-permits-date-picker-range', 'start_date'),
     Input('slide1-permits-date-picker-range', 'end_date'),
     Input('slide1-permits-permittype-dropdown', 'value')])
def update_total_permit_volume_indicator(start_date, end_date, permittype):
    total_permit_volume_updated = update_total_permit_volume(start_date, end_date, permittype)
    return str(total_permit_volume_updated)

@app.callback(
    Output('slide1-feespaid-indicator', 'children'),
    [Input('slide1-permits-date-picker-range', 'start_date'),
     Input('slide1-permits-date-picker-range', 'end_date'),
     Input('slide1-permits-permittype-dropdown', 'value')])
def update_total_fees_paid_indicator(start_date, end_date, permittype):
    total_fees_paid = update_total_fees_paid(start_date, end_date, permittype)
    return str(total_fees_paid)

@app.callback(
    Output('slide1-permits-count-table', 'rows'),
    [Input('slide1-permits-date-picker-range', 'start_date'),
     Input('slide1-permits-date-picker-range', 'end_date'),
     Input('slide1-permits-permittype-dropdown', 'value')])
def update_count_table(start_date, end_date, permittype):
    df_counts = update_counts_table_data(start_date, end_date, permittype)
    return df_counts.to_dict('records')

@app.callback(
    Output('slide1-permits-count-table-download-link', 'href'),
    [Input('slide1-permits-date-picker-range', 'start_date'),
     Input('slide1-permits-date-picker-range', 'end_date'),
     Input('slide1-permits-permittype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, permittype):
    df_counts = update_counts_table_data(start_date, end_date, permittype)
    csv_string = df_counts.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string