import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import numpy as np
import urllib.parse

from app import app, con

testing_mode = True
print('slide2.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('Slide2.csv', parse_dates=['PAYMENTDAYMONTHYEAR'])
    
else:
    with con() as con:
        with open(r'queries/licenses/FinalQueries_SQL/slide2_PaymentsbyMonth.sql') as counts_query:
            df = pd.read_sql_query(sql=counts_query.read(), con=con, parse_dates={'PAYMENTDAYMONTHYEAR': {'format': '%Y-%m-%d'}})

df.rename(columns={'JOBTYPE': 'Job Type', 'PAYMENTDAYMONTHYEAR': 'Date', 'TOTALAMOUNT': 'Revenue Collected'}, inplace=True)
df_counts = df.copy(deep=True) # Make a copy to keep the original for filtering
df_chart = df_counts.groupby(['Date'])['Revenue Collected'].sum()

def update_count_data(selected_start, selected_end, selected_jobtype):
    df_counts = df[(df['Date']>=selected_start)&(df['Date']<=selected_end)]
    if selected_jobtype != "All":
        df_counts = df_counts[(df_counts['Job Type']==selected_jobtype)]
    df_counts['Date'] = df_counts['Date'].dt.strftime('%B %Y') 
    return df_counts

def update_graph_data(selected_start, selected_end, selected_jobtype):
    df_chart = df[(df['Date']>=selected_start)&(df['Date']<=selected_end)]
    if selected_jobtype != "All":
        df_chart = df_chart[(df_chart['Job Type']==selected_jobtype)]
    df_chart = df_chart.groupby(['Date'])['Revenue Collected'].sum()
    return df_chart

layout = html.Div(children=[
                html.H1(children='License Revenue'),
                html.Div(children='Please Select Date Range'),
                html.Div([
                    dcc.DatePickerRange(
                        id='slide2-my-date-picker-range',
                        start_date=datetime(2016, 1, 1),
                        end_date=datetime.now()
                    ),
                ]),
                html.Div([
                    html.Div(children='Please Select A Job Type'),
                    dcc.Dropdown(
                        id='slide2-jobtype-dropdown',
                        options=[
                            {'label': 'All', 'value': 'All'},
                            {'label': 'Amendment/Renewal', 'value': 'Amendment/Renewal'},
                            {'label': 'Business License Application', 'value': 'Business License Application'},
                            {'label': 'Trade License Amend/Renew', 'value': 'Trade License Amend/Renew'},
                            {'label': 'Trade License Application', 'value': 'Trade License Application'}
                        ],
                        value='All'
                    ),
                ], style={'width': '30%', 'display': 'inline-block'}),
                dcc.Graph(id='slide2-my-graph',
                    figure=go.Figure(
                        data=[
                            go.Bar(
                                x=df_chart.index,
                                y=df_chart.values,
                                name='Revenue Collected',
                                marker=go.bar.Marker(
                                    color='rgb(26, 118, 255)'
                                )
                            )
                        ],
                    ),
                ),
                html.Div([
                    html.A(
                        'Download Data',
                        id='slide2-count-table-download-link',
                        download='slide2.csv',
                        href='',
                        target='_blank',
                    )
                ], style={'text-align': 'right'}),
                table.DataTable(
                    # Initialise the rows
                    rows=[{}],
                    columns=["Date", "Job Type", "Revenue Collected"],
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    id='slide2-count-table'
                )
                ])

@app.callback(
    Output('slide2-my-graph', 'figure'),
    [Input('slide2-my-date-picker-range', 'start_date'),
     Input('slide2-my-date-picker-range', 'end_date'),
     Input('slide2-jobtype-dropdown', 'value')])
def update_graph(start_date, end_date, jobtype):
    df_chart = update_graph_data(start_date, end_date, jobtype)
    return {
        'data': [
             go.Bar(
                 x=df_chart.index,
                 y=df_chart.values,
                 name='Revenue Collected',
                 marker=go.bar.Marker(
                     color='rgb(26, 118, 255)'
                 )
             )
         ],
        'layout': go.Layout(
            showlegend=True,
            legend=go.layout.Legend(
                x=.75,
                y=1
            ),
            margin=go.layout.Margin(l=40, r=0, t=40, b=80)
        )
    }

@app.callback(
    Output('slide2-count-table', 'rows'),
    [Input('slide2-my-date-picker-range', 'start_date'),
     Input('slide2-my-date-picker-range', 'end_date'),
     Input('slide2-jobtype-dropdown', 'value')])
def update_count_table(start_date, end_date, jobtype):
    df_counts = update_count_data(start_date, end_date, jobtype)
    return df_counts.to_dict('records')

@app.callback(
    Output('slide2-count-table-download-link', 'href'),
    [Input('slide2-my-date-picker-range', 'start_date'),
     Input('slide2-my-date-picker-range', 'end_date'),
     Input('slide2-jobtype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, jobtype):
    df = update_count_data(start_date, end_date, jobtype)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string