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
            sql = 'SELECT * FROM li_stat_licenserevenue_tl'
            df = pd.read_sql_query(sql=sql, con=con, parse_dates=['PAYMENTDATE'])
        elif dataset == 'last_ddl_time':
            sql = 'SELECT SCN_TO_TIMESTAMP(MAX(ora_rowscn)) last_ddl_time FROM LI_STAT_LICENSEREVENUE_TL'
            df = pd.read_sql_query(sql=sql, con=con)
    return df.to_json(date_format='iso', orient='split')

def dataframe(dataset):
    return pd.read_json(query_data(dataset), orient='split')

def get_last_ddl_time():
    last_ddl_time = dataframe('last_ddl_time')
    return last_ddl_time['LAST_DDL_TIME'].iloc[0]

def get_df_ind():
    df_ind = dataframe('df_ind')
    df_ind['PAYMENTDATE'] = pd.to_datetime(df_ind['PAYMENTDATE'])
    df_ind.rename(columns={
                    'JOBTYPE': 'Job Type', 
                    'PAYMENTDATE': 'Date', 
                    'TOTALAMOUNT': 'Revenue Collected'}, inplace=True)
    return df_ind

def get_total_revenue(df_ind):
    return'${:,.0f}'.format(df_ind['Revenue Collected'].sum())

def get_df_line_chart(df_ind):
    df_line_chart = (df_ind.groupby(['Date'])['Revenue Collected']
                          .sum()
                          .reset_index()
                          .assign(DateText=lambda x: x['Date'].dt.strftime('%b %Y')))
    return df_line_chart

def get_df_pie_chart(df_ind):
    df_pie_chart = (df_ind.groupby(['Job Type'])['Revenue Collected']
                           .sum()
                           .reset_index())
    return df_pie_chart

def get_unique_job_types(df_ind):
    unique_job_types = df_ind['Job Type'].unique()
    return unique_job_types

def get_job_type_options(unique_job_types):
    job_type_options = [{'label': unique_job_type,
                        'value': unique_job_type}
                        for unique_job_type in unique_job_types]
    return job_type_options

def update_count_data(selected_start, selected_end, selected_jobtype):
    df_ind = get_df_ind()
    df_counts = df_ind[(df_ind['Date'] >= selected_start)
                  & (df_ind['Date']<=selected_end)
                  & df_ind['Job Type'].isin(selected_jobtype)]
    df_counts['Date'] = df_counts['Date'].dt.strftime('%b %Y') 
    return df_counts

def update_line_chart_data(selected_start, selected_end, selected_jobtype):
    df_ind = get_df_ind()
    df_line_chart = df_ind[(df_ind['Date'] >= selected_start)
                  & (df_ind['Date']<=selected_end)
                  & df_ind['Job Type'].isin(selected_jobtype)]
    df_line_chart = (df_line_chart.groupby(['Date'])['Revenue Collected']
                                  .sum()
                                  .reset_index()
                                  .assign(DateText=lambda x: x['Date'].dt.strftime('%b %Y')))
    return df_line_chart

def update_pie_data(selected_start, selected_end, selected_jobtype):
    df_ind = get_df_ind()
    df_pie_chart = df_ind[(df_ind['Date'] >= selected_start)
                    & (df_ind['Date'] <= selected_end)
                    & df_ind['Job Type'].isin(selected_jobtype)]
    df_pie_chart = df_pie_chart.groupby(['Job Type'])['Revenue Collected'].sum()
    return df_pie_chart

def update_total_revenue(selected_start, selected_end, selected_jobtype):
    df_ind = get_df_ind()
    df_selected = df_ind[(df_ind['Date'] >= selected_start)
                  & (df_ind['Date']<=selected_end)
                  & df_ind['Job Type'].isin(selected_jobtype)]
    total_license_volume = df_selected['Revenue Collected'].sum()
    return '${:,.0f}'.format(total_license_volume)

def update_layout():
    last_ddl_time = get_last_ddl_time()
    df_ind = get_df_ind()
    total_revenue = get_total_revenue(df_ind)
    df_line_chart = get_df_line_chart(df_ind)
    df_pie_chart = get_df_pie_chart(df_ind)
    unique_job_types = get_unique_job_types(df_ind)
    job_type_options = get_job_type_options(unique_job_types)

    return html.Div(children=[
                html.H1('Trade License Revenue', style={'text-align': 'center'}),
                html.P(f"Data last updated {last_ddl_time}", style = {'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Payment Date'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='slide2TL-my-date-picker-range',
                            start_date=df_ind['Date'].min(),
                            end_date=datetime.now()
                        )
                    ], className='four columns'),
                    html.Div([
                        html.P('Job Type'),
                        dcc.Dropdown(
                            id='slide2TL-jobtype-dropdown',
                            options=job_type_options,
                            multi=True,
                            value=unique_job_types
                        )
                    ], className='five columns')
                ], className='dashrow filters'),
                html.Div([
                    html.Div(
                        [
                            dcc.Graph(
                                id='slide2TL-my-graph',
                                config={
                                    'displayModeBar': False
                                },
                                figure=go.Figure(
                                    data=[
                                        go.Scatter(
                                            x=df_line_chart['Date'],
                                            y=df_line_chart['Revenue Collected'],
                                            name='Revenue Collected',
                                            mode='lines',
                                            text=df_line_chart['DateText'],
                                            hoverinfo = 'text+y',
                                            line=dict(
                                                shape='spline',
                                                color='rgb(26, 118, 255)'
                                            ),
                                            showlegend = False
                                        )
                                    ],
                                    layout=go.Layout(
                                                title=('Revenue Collected By Month'), 
                                                xaxis=dict(zeroline = False), 
                                                yaxis=dict(hoverformat = '4.0f')
                                            )
                                ),
                            )
                        ], className='nine columns'),
                    html.Div([
                        html.H1('', id='slide2TL-indicator', style={'font-size': '45pt'}),
                        html.H2('Collected', style={'font-size': '40pt'})
                    ], className='three columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '150px 0'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        dcc.Graph(id='slide2TL-piechart',
                            figure=go.Figure(
                                data=[
                                    go.Pie(
                                        labels=df_pie_chart.index,
                                        values=df_pie_chart.values,
                                        hoverinfo='label+value+percent', 
                                        hole=0.4,
                                        textfont=dict(color='#000000'),
                                        marker=dict(colors=['#FF7070', '#FFCD70', '#77FF70', '#70F0FF'], 
                                            line=dict(color='#000000', width=2)
                                        )
                                    )
                                ],
                                layout=go.Layout(title=('Revenue Breakdown by Job Type'))
                            )
                        )
                    ], className='six columns'),
                    html.Div([
                        html.H3('Revenue Collected By Month and Job Type', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                # Initialise the rows
                                rows=[{}],
                                columns=["Date", "Job Type", "Revenue Collected"],
                                editable=False,
                                sortable=True,
                                id='slide2TL-count-table'
                            )
                        ], style={'text-align': 'center'}),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='slide2TL-count-table-download-link',
                                download='slide2TL.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], className='six columns')
                ], className='dashrow'),
                html.Details([
                    html.Summary('Query Description'),
                    html.Div([
                        html.P(
                            'Fees paid (aka revenue collected) since 1/1/16 from all trade license amend/renew and '
                            'application jobs.')
                    ])
                ])
            ])

layout = update_layout

@app.callback(
    Output('slide2TL-piechart', 'figure'),
    [Input('slide2TL-my-date-picker-range', 'start_date'),
     Input('slide2TL-my-date-picker-range', 'end_date'),
     Input('slide2TL-jobtype-dropdown', 'value')])
def update_pie_chart(start_date, end_date, jobtype):
    df_pie_chart_updated = update_pie_data(start_date, end_date, jobtype)
    return {
        'data': [
             go.Pie(
                labels=df_pie_chart_updated.index,
                values=df_pie_chart_updated.values,
                hoverinfo='label+value+percent', 
                hole=0.4,
                textfont=dict(color='#000000'),
                marker=dict(colors=['#FF7070', '#FFCD70', '#77FF70', '#70F0FF'], 
                    line=dict(color='#000000', width=2)
                )
             )
         ],
         'layout': go.Layout(
                legend=dict(orientation='h'),
                title=('Revenue Breakdown by Job Type')
            )
    }

@app.callback(
    Output('slide2TL-my-graph', 'figure'),
    [Input('slide2TL-my-date-picker-range', 'start_date'),
     Input('slide2TL-my-date-picker-range', 'end_date'),
     Input('slide2TL-jobtype-dropdown', 'value')])
def update_line_chart(start_date, end_date, jobtype):
    df_line_chart_updated = update_line_chart_data(start_date, end_date, jobtype)
    return {
        'data': [
             go.Scatter(
                 x=df_line_chart_updated['Date'],
                 y=df_line_chart_updated['Revenue Collected'],
                 name='Revenue Collected',
                 mode='lines',
                 text=df_line_chart_updated['DateText'],
                 hoverinfo='text+y',
                 line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                 ),
                 showlegend=False
             )
         ],
        'layout': go.Layout(
            title=('Revenue Collected By Month'),
            xaxis=dict(zeroline=False),
            yaxis=dict(
                title='$',
                hoverformat='4.0f',
                range=[0, df_line_chart_updated['Revenue Collected'].max() + (df_line_chart_updated['Revenue Collected'].max() / 50)]
            )
        )
    }

@app.callback(
    Output('slide2TL-indicator', 'children'),
    [Input('slide2TL-my-date-picker-range', 'start_date'),
     Input('slide2TL-my-date-picker-range', 'end_date'),
     Input('slide2TL-jobtype-dropdown', 'value')])
def update_total_license_volume_indicator(start_date, end_date, jobtype):
    total_revenue_updated = update_total_revenue(start_date, end_date, jobtype)
    return str(total_revenue_updated)

@app.callback(
    Output('slide2TL-count-table', 'rows'),
    [Input('slide2TL-my-date-picker-range', 'start_date'),
     Input('slide2TL-my-date-picker-range', 'end_date'),
     Input('slide2TL-jobtype-dropdown', 'value')])
def update_count_table(start_date, end_date, jobtype):
    df_counts_updated = update_count_data(start_date, end_date, jobtype)
    return df_counts_updated.to_dict('records')

@app.callback(
    Output('slide2TL-count-table-download-link', 'href'),
    [Input('slide2TL-my-date-picker-range', 'start_date'),
     Input('slide2TL-my-date-picker-range', 'end_date'),
     Input('slide2TL-jobtype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, jobtype):
    df_updated = update_count_data(start_date, end_date, jobtype)
    csv_string = df_updated.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string