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
print('slide1_license_volumes_TL.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('Slide1_TL.csv', parse_dates=['ISSUEDATE'])

else:
    with con() as con:
        with open(r'queries/licenses/slide1_license_volumes_TL.sql') as sql:
            df = pd.read_sql_query(sql=sql.read(), con=con, parse_dates=['ISSUEDATE'])

# Rename the columns to be more readable
# Make a DateText Column to display on the graph            
df = (df.rename(columns={'ISSUEDATE': 'Issue Date', 'LICENSETYPE': 'License Type', 'COUNTJOBS': 'Number of Licenses Issued'})
        .assign(DateText=lambda x: x['Issue Date'].dt.strftime('%b %Y')))

unique_licensetypes = df['License Type'].unique()
unique_licensetypes = np.append(['All'], unique_licensetypes)

total_license_volume = '{:,.0f}'.format(df['Number of Licenses Issued'].sum())

def update_total_license_volume(selected_start, selected_end, selected_jobtype, selected_licensetype):
    df_selected = df.copy(deep=True)

    if selected_jobtype != "All":
        df_selected = df_selected[(df_selected['JOBTYPE']==selected_jobtype)]
    if selected_licensetype != "All":
        df_selected = df_selected[(df_selected['License Type']==selected_licensetype)]

    df_selected = df_selected.loc[(df['Issue Date']>=selected_start)&(df_selected['Issue Date']<=selected_end)]
    total_license_volume = df_selected['Number of Licenses Issued'].sum()
    return '{:,.0f}'.format(total_license_volume)

def update_counts_graph_data(selected_start, selected_end, selected_jobtype, selected_licensetype):
    df_selected = df.copy(deep=True)

    if selected_jobtype != "All":
        df_selected = df_selected[(df_selected['JOBTYPE']==selected_jobtype)]
    if selected_licensetype != "All":
        df_selected = df_selected[(df_selected['License Type']==selected_licensetype)]

    df_selected = (df_selected.loc[(df['Issue Date']>=selected_start)&(df_selected['Issue Date']<=selected_end)]
                              .groupby(by=['Issue Date', 'DateText'])['Number of Licenses Issued']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Issue Date']))
    return df_selected

def update_counts_table_data(selected_start, selected_end, selected_jobtype, selected_licensetype):
    df_selected = df.copy(deep=True)
    
    if selected_jobtype != "All":
        df_selected = df_selected[(df_selected['JOBTYPE']==selected_jobtype)]
    if selected_licensetype != "All":
        df_selected = df_selected[(df_selected['License Type'] == selected_licensetype)]

    (df_selected.loc[(df['Issue Date']>=selected_start)&(df_selected['Issue Date']<=selected_end)]
                              .groupby(by=['Issue Date', 'License Type'])['Number of Licenses Issued']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Issue Date','License Type']))
    df_selected['Issue Date'] = df_selected['Issue Date'].apply(lambda x: datetime.strftime(x, '%b %Y'))
    return df_selected

layout = html.Div(children=[
                html.H1('Trade License Volumes', style={'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Date Range'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='slide1-TL-my-date-picker-range',
                            start_date=datetime(2016, 1, 1),
                            end_date=datetime.now()
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by Job Type'),
                        dcc.Dropdown(
                            id='slide1-TL-jobtype-dropdown',
                            options=[
                                {'label': 'All', 'value': 'All'},
                                {'label': 'Application', 'value': 'Application'},
                                {'label': 'Renewal', 'value': 'Renewal'}
                            ],
                            value='All'
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by License Type'),
                        dcc.Dropdown(
                                id='slide1-TL-licensetype-dropdown',
                                options=[{'label': k, 'value': k} for k in unique_licensetypes],
                                value='All'
                        ),
                    ], className='four columns'),
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        dcc.Graph(id='slide1-TL-my-graph',
                            figure=go.Figure(
                                data=[
                                    go.Scatter(
                                        x=df['Issue Date'],
                                        y=df['Number of Licenses Issued'],
                                        mode='lines',
                                        text=df['DateText'],
                                        hoverinfo='text+y',
                                        line=dict(
                                            shape='spline',
                                            color='rgb(26, 118, 255)'
                                        )
                                    )
                                ],
                            )
                        )
                    ], className='nine columns'),
                    html.Div([
                        html.H1('', id='slide1-TL-indicator', style={'font-size': '45pt'}),
                        html.H2('Licenses Issued', style={'font-size': '40pt'})
                    ], className='three columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '75px 0'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H3('License Volumes By License Type and Month', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                #columns=['Issue Date', 'LICENSETYPE', 'COUNTJOBS'],
                                columns=['Issue Date', 'License Type', 'Number of Licenses Issued'],
                                editable=False,
                                sortable=True,
                                id='slide1-TL-count-table'
                            ),
                        ], style={'text-align': 'center'}),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='slide1-TL-count-table-download-link',
                                download='slide1_TL_license_volumes_counts.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'width': '40%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '45px', 'margin-bottom': '45px'})
                ], className='dashrow')
            ])

@app.callback(
    Output('slide1-TL-my-graph', 'figure'),
    [Input('slide1-TL-my-date-picker-range', 'start_date'),
     Input('slide1-TL-my-date-picker-range', 'end_date'),
     Input('slide1-TL-jobtype-dropdown', 'value'),
     Input('slide1-TL-licensetype-dropdown', 'value')])
def update_graph(start_date, end_date, jobtype, licensetype):
    df = update_counts_graph_data(start_date, end_date, jobtype, licensetype)
    return {
        'data': [
             go.Scatter(
                 x=df['Issue Date'],
                 y=df['Number of Licenses Issued'],
                 mode='lines',
                 text=df['DateText'],
                 hoverinfo = 'text+y',
                 line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                 )
             )
         ],
        'layout': go.Layout(
            title='Number of Licenses Issued By Month',
            yaxis= dict(title='Number of Trade Licenses Issued')
        )
    }

@app.callback(
    Output('slide1-TL-indicator', 'children'),
    [Input('slide1-TL-my-date-picker-range', 'start_date'),
     Input('slide1-TL-my-date-picker-range', 'end_date'),
     Input('slide1-TL-jobtype-dropdown', 'value'),
     Input('slide1-TL-licensetype-dropdown', 'value')])
def update_total_license_volume_indicator(start_date, end_date, jobtype, licensetype):
    total_license_volume = update_total_license_volume(start_date, end_date, jobtype, licensetype)
    return str(total_license_volume)

@app.callback(
    Output('slide1-TL-count-table', 'rows'),
    [Input('slide1-TL-my-date-picker-range', 'start_date'),
     Input('slide1-TL-my-date-picker-range', 'end_date'),
     Input('slide1-TL-jobtype-dropdown', 'value'),
     Input('slide1-TL-licensetype-dropdown', 'value')])
def update_count_table(start_date, end_date, jobtype, licensetype):
    df = update_counts_table_data(start_date, end_date, jobtype, licensetype)
    return df.to_dict('records')

@app.callback(
    Output('slide1-TL-count-table-download-link', 'href'),
    [Input('slide1-TL-my-date-picker-range', 'start_date'),
     Input('slide1-TL-my-date-picker-range', 'end_date'),
     Input('slide1-TL-jobtype-dropdown', 'value'),
     Input('slide1-TL-licensetype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, jobtype, licensetype):
    df = update_counts_table_data(start_date, end_date, jobtype, licensetype)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string