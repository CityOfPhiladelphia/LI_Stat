import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import numpy as np
import urllib.parse
import os

from app import app, con

print(os.path.basename(__file__))

with con() as con:
    sql = 'SELECT * FROM li_stat_licenserevenue_bl'
    df = pd.read_sql_query(sql=sql, con=con, parse_dates=['PAYMENTDATE'])
    sql = "SELECT from_tz(cast(last_ddl_time as timestamp), 'GMT') at TIME zone 'US/Eastern' as LAST_DDL_TIME FROM user_objects WHERE object_name = 'LI_STAT_LICENSEREVENUE_BL'"
    last_ddl_time = pd.read_sql_query(sql=sql, con=con)

df.rename(columns={'JOBTYPE': 'Job Type', 'PAYMENTDATE': 'Date', 'TOTALAMOUNT': 'Revenue Collected'}, inplace=True)

total_revenue = '${:,.0f}'.format(df['Revenue Collected'].sum())

df_counts = df.copy(deep=True) # Make a copy to keep the original for filtering

df_line_chart = (df_counts.groupby(['Date'])['Revenue Collected']
                          .sum()
                          .reset_index()
                          .assign(DateText=lambda x: x['Date'].dt.strftime('%b %Y')))

df_pie_chart = (df.copy(deep=True)
                  .groupby(['Job Type'])['Revenue Collected']
                  .sum()
                  .reset_index())

unique_job_types = df['Job Type'].unique()

job_type_options = [{'label': unique_job_type,
                     'value': unique_job_type}
                     for unique_job_type in unique_job_types]

def update_count_data(selected_start, selected_end, selected_jobtype):
    df_counts = df[(df['Date'] >= selected_start)
                  & (df['Date']<=selected_end)
                  & df['Job Type'].isin(selected_jobtype)]
    df_counts['Date'] = df_counts['Date'].dt.strftime('%b %Y') 
    return df_counts

def update_line_chart_data(selected_start, selected_end, selected_jobtype):
    df_line_chart = df[(df['Date'] >= selected_start)
                  & (df['Date']<=selected_end)
                  & df['Job Type'].isin(selected_jobtype)]
    df_line_chart = (df_line_chart.groupby(['Date'])['Revenue Collected']
                                  .sum()
                                  .reset_index()
                                  .assign(DateText=lambda x: x['Date'].dt.strftime('%b %Y')))
    return df_line_chart

def update_pie_data(selected_start, selected_end, selected_jobtype):
    df_pie_chart = df[(df['Date'] >= selected_start)
                    & (df['Date'] <= selected_end)
                    & df['Job Type'].isin(selected_jobtype)]
    df_pie_chart = df_pie_chart.groupby(['Job Type'])['Revenue Collected'].sum()
    return df_pie_chart

def update_total_revenue(selected_start, selected_end, selected_jobtype):
    df_selected = df[(df['Date'] >= selected_start)
                  & (df['Date']<=selected_end)
                  & df['Job Type'].isin(selected_jobtype)]
    total_license_volume = df_selected['Revenue Collected'].sum()
    return '${:,.0f}'.format(total_license_volume)

layout = html.Div(children=[
                html.H1('Business License Revenue', style={'text-align': 'center'}),
                html.P(f"Data last updated {last_ddl_time['LAST_DDL_TIME'].iloc[0]}", style = {'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Payment Date'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='slide2BL-my-date-picker-range',
                            start_date=datetime(2016, 1, 1),
                            end_date=datetime.now()
                        )
                    ], className='four columns'),
                    html.Div([
                        html.P('Job Type'),
                        dcc.Dropdown(
                            id='slide2BL-jobtype-dropdown',
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
                                id='slide2BL-my-graph',
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
                        html.H1('', id='slide2BL-indicator', style={'font-size': '45pt'}),
                        html.H2('Collected', style={'font-size': '40pt'})
                    ], className='three columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '150px 0'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        dcc.Graph(id='slide2BL-piechart',
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
                                id='slide2BL-count-table'
                            )
                        ], style={'text-align': 'center'}),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='slide2BL-count-table-download-link',
                                download='slide2BL.csv',
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
                            'Fees paid (aka revenue collected) since 1/1/16 from all business license amend/renew and '
                            'application jobs.')
                    ])
                ])
            ])

@app.callback(
    Output('slide2BL-piechart', 'figure'),
    [Input('slide2BL-my-date-picker-range', 'start_date'),
     Input('slide2BL-my-date-picker-range', 'end_date'),
     Input('slide2BL-jobtype-dropdown', 'value')])
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
    Output('slide2BL-my-graph', 'figure'),
    [Input('slide2BL-my-date-picker-range', 'start_date'),
     Input('slide2BL-my-date-picker-range', 'end_date'),
     Input('slide2BL-jobtype-dropdown', 'value')])
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
    Output('slide2BL-indicator', 'children'),
    [Input('slide2BL-my-date-picker-range', 'start_date'),
     Input('slide2BL-my-date-picker-range', 'end_date'),
     Input('slide2BL-jobtype-dropdown', 'value')])
def update_total_license_volume_indicator(start_date, end_date, jobtype):
    total_revenue_updated = update_total_revenue(start_date, end_date, jobtype)
    return str(total_revenue_updated)

@app.callback(
    Output('slide2BL-count-table', 'rows'),
    [Input('slide2BL-my-date-picker-range', 'start_date'),
     Input('slide2BL-my-date-picker-range', 'end_date'),
     Input('slide2BL-jobtype-dropdown', 'value')])
def update_count_table(start_date, end_date, jobtype):
    df_counts_updated = update_count_data(start_date, end_date, jobtype)
    return df_counts_updated.to_dict('records')

@app.callback(
    Output('slide2BL-count-table-download-link', 'href'),
    [Input('slide2BL-my-date-picker-range', 'start_date'),
     Input('slide2BL-my-date-picker-range', 'end_date'),
     Input('slide2BL-jobtype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, jobtype):
    df_updated = update_count_data(start_date, end_date, jobtype)
    csv_string = df_updated.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string