import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as table
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
from datetime import datetime
import numpy as np
import urllib.parse

from app import app, con_LIDB

testing_mode = False
print('slide1Permits.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('test_data/Slide1Permits.csv', parse_dates=['ISSUEDATE'])

else:
    with con_LIDB() as con_LIDB:
        with open(r'queries/permits/slide1_MonthlyPermitsSubmittedwithPaidFees.sql') as sql:
            df = pd.read_sql_query(sql=sql.read(), con=con_LIDB, parse_dates=['ISSUEDATE'])

# Rename the columns to be more readable
# Make a DateText Column to display on the graph
df = (df.rename(columns={'ISSUEDATE': 'Issue Date', 'PERMITDESCRIPTION': 'Permit Type', 'COUNTPERMITS': 'Number of Permits Issued'})
        .assign(DateText=lambda x: x['Issue Date'].dt.strftime('%b %Y')))

unique_permittypes = df['Permit Type'].unique()
unique_permittypes = np.append(['All'], unique_permittypes)

total_permit_volume = '{:,.0f}'.format(df['Number of Permits Issued'].sum())

def update_total_permit_volume(selected_start, selected_end, selected_permittype):
    df_selected = df.copy(deep=True)

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type']==selected_permittype)]

    df_selected = df_selected.loc[(df['Issue Date']>=selected_start)&(df_selected['Issue Date']<=selected_end)]
    total_permit_volume = df_selected['Number of Permits Issued'].sum()
    return '{:,.0f}'.format(total_permit_volume)

def update_counts_graph_data(selected_start, selected_end, selected_permittype):
    df_selected = df.copy(deep=True)

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]

    df_selected = (df_selected.loc[(df['Issue Date'] >= selected_start) & (df_selected['Issue Date'] <= selected_end)]
                              .groupby(by=['Issue Date', 'DateText'])['Number of Permits Issued']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Issue Date']))
    return df_selected

def update_counts_table_data(selected_start, selected_end, selected_permittype):
    df_selected = df.copy(deep=True)

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]

    (df_selected.loc[(df['Issue Date']>=selected_start) & (df_selected['Issue Date']<=selected_end)]
                              .groupby(by=['Issue Date', 'Permit Type'])['Number of Permits Issued']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Issue Date', 'Permit Type']))
    df_selected['Issue Date'] = df_selected['Issue Date'].apply(lambda x: datetime.strftime(x, '%b %Y'))
    return df_selected

layout = html.Div(children=[
                html.H1('Permit Volumes', style={'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Date Range'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='slide1-permits-date-picker-range',
                            start_date=datetime(2016, 1, 1),
                            end_date=datetime.now()
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by Permit Type'),
                        dcc.Dropdown(
                                id='slide1-permits-permittype-dropdown',
                                options=[{'label': k, 'value': k} for k in unique_permittypes],
                                value='All'
                        ),
                    ], className='four columns'),
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        dcc.Graph(id='slide1-permits-graph',
                            figure=go.Figure(
                                data=[
                                    go.Scatter(
                                        x=df['Issue Date'],
                                        y=df['Permits Issued'],
                                        mode='lines',
                                        text=df['DateText'],
                                        hoverinfo='text+y',
                                        line=dict(
                                            shape='spline',
                                            color='rgb(26, 118, 255)'
                                        )
                                    )
                                ],
                            ),
                        ),
                    ], className='nine columns'),
                    html.Div([
                        html.H1('', id='slide1-permits-indicator', style={'font-size': '45pt'}),
                        html.H2('Permits Issued', style={'font-size': '40pt'})
                    ], className='three columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '75px 0'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H3('Permit Volumes By Permit Type and Month', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                columns=['Issue Date', 'Permit Type', 'Number of Permits Issued'],
                                editable=False,
                                sortable=True,
                                id='slide1-permits-count-table'
                            ),
                        ], style={'text-align': 'center'}),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='slide1-permits-count-table-download-link',
                                download='slide1_permit_volumes_counts.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'width': '55%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '45px', 'margin-bottom': '45px'})
                ], className='dashrow')
            ])

@app.callback(
    Output('slide1-permits-graph', 'figure'),
    [Input('slide1-permits-date-picker-range', 'start_date'),
     Input('slide1-permits-date-picker-range', 'end_date'),
     Input('slide1-permits-permittype-dropdown', 'value')])
def update_graph(start_date, end_date, permittype):
    df = update_counts_graph_data(start_date, end_date, permittype)
    return {
        'data': [
             go.Scatter(
                 x=df['Issue Date'],
                 y=df['Number of Permits Issued'],
                 mode='lines',
                 text=df['DateText'],
                 hoverinfo='text+y',
                 line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                 )
             )
         ],
        'layout': go.Layout(
            title='Number of Permits Issued By Month',
            yaxis= dict(title='Number of Permits Issued')
        )
    }

@app.callback(
    Output('slide1-permits-indicator', 'children'),
    [Input('slide1-permits-date-picker-range', 'start_date'),
     Input('slide1-permits-date-picker-range', 'end_date'),
     Input('slide1-permits-permittype-dropdown', 'value')])
def update_total_permit_volume_indicator(start_date, end_date, permittype):
    total_permit_volume = update_total_permit_volume(start_date, end_date, permittype)
    return str(total_permit_volume)

@app.callback(
    Output('slide1-permits-count-table', 'rows'),
    [Input('slide1-permits-date-picker-range', 'start_date'),
     Input('slide1-permits-date-picker-range', 'end_date'),
     Input('slide1-permits-permittype-dropdown', 'value')])
def update_count_table(start_date, end_date, permittype):
    df = update_counts_table_data(start_date, end_date, permittype)
    return df.to_dict('records')

@app.callback(
    Output('slide1-permits-count-table-download-link', 'href'),
    [Input('slide1-permits-date-picker-range', 'start_date'),
     Input('slide1-permits-date-picker-range', 'end_date'),
     Input('slide1-permits-permittype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, permittype):
    df = update_counts_table_data(start_date, end_date, permittype)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string