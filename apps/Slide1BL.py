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

testing_mode = False
print('slide1_license_volumes_BL.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df_counts = pd.read_csv('Slide1_BL_counts.csv')
    df_ind_records = pd.read_csv('Slide1_BL_ind_records.csv')

else:
    with con() as con:
        with open(r'queries/licenses/FinalQueries_SQL/slide1_license_volumes_BL_counts_query.sql') as counts_query:
            df_counts = pd.read_sql_query(counts_query.read(), con)
        with open(r'queries/licenses/FinalQueries_SQL/slide1_license_volumes_BL_ind_records_query.sql') as ind_records_query:
            df_ind_records = pd.read_sql_query(ind_records_query.read(), con)


df_counts['JOBTYPE'] = df_counts['JOBTYPE'].map(lambda x: str(x)[3:])  # strip first 3 characters "BL_" just to make it easier for user to read

unique_licensetypes = df_counts['LICENSETYPE'].unique()
unique_licensetypes = np.append(['All'], unique_licensetypes)

df_ind_records['ISSUEDATE'] = pd.to_datetime(df_ind_records['ISSUEDATE'], errors = 'coerce') #make sure IssueDate column is of type datetime so that filtering of dataframe based on date can happen later
df_ind_records['JOBTYPE'] = df_ind_records['JOBTYPE'].map(lambda x: str(x)[3:])  # strip first 3 characters "BL_" just to make it easier for user to read

def update_counts_graph_data(selected_start, selected_end, selected_jobtype, selected_licensetype):
    df_countselected = df_ind_records[(df_ind_records['ISSUEDATE']>=selected_start)&(df_ind_records['ISSUEDATE']<=selected_end)]
    if selected_jobtype != "All":
        df_countselected = df_countselected[(df_countselected['JOBTYPE']==selected_jobtype)]
    if selected_licensetype != "All":
        df_countselected = df_countselected[(df_countselected['LICENSETYPE']==selected_licensetype)]
    df_counts = df_countselected.groupby(by=['JOBISSUEMONTHYEAR','JOBISSUEYEAR','JOBISSUEMONTH'], as_index=False).size().reset_index()
    df_counts = df_counts.rename(index=str, columns={"JOBISSUEMONTHYEAR":"JOBISSUEMONTHYEAR","JOBISSUEYEAR":"JOBISSUEYEAR","JOBISSUEMONTH":"JOBISSUEMONTH", 0: "Count"})
    df_counts = df_counts.sort_values(by=['JOBISSUEYEAR','JOBISSUEMONTH'])
    #Adding in months that had counts of 0 so there aren't any missing columns in the graph
    idx = pd.date_range(selected_start, selected_end, freq='M').to_period('m') # Create list of all months in date range
    df_counts['JOBISSUEDAYMONTHYEAR'] = '1 ' + df_counts['JOBISSUEMONTH'].astype(str) + ' ' + df_counts['JOBISSUEYEAR'].astype(str) # Create field that has day, month, and year so you can convert that to a Date (you have to have a day value)
    df_counts.index = pd.to_datetime(df_counts['JOBISSUEDAYMONTHYEAR'], format='%d %m %Y') # Make index of df_counts dataframe a Date
    df_counts.index = df_counts.index.to_period('m') # Turn index from Date to PeriodIndex
    df_counts = df_counts.reindex(idx) # Reindex df_counts based on the list of ALL months in the date range so that it includes even those that didn't have any values
    df_counts['Count'].fillna(0, inplace=True) # Give any months without a Count value the value of 0
    df_counts['JOBISSUEMONTHYEAR'] = df_counts.index.strftime('%B %Y') # Replace the values in the JOBISSUEMONTHYEAR field with the (formatted) values from the index. The JOBISSUEMONTHYEAR field values are the ones that are going to display on the x-axis of the graph
    return df_counts

def update_counts_table_data(selected_start, selected_end, selected_jobtype, selected_licensetype):
    df_countselected = df_ind_records[(df_ind_records['ISSUEDATE']>=selected_start)&(df_ind_records['ISSUEDATE']<=selected_end)]
    if selected_jobtype != "All":
        df_countselected = df_countselected[(df_countselected['JOBTYPE']==selected_jobtype)]
    if selected_licensetype != "All":
        df_countselected = df_countselected[(df_countselected['LICENSETYPE'] == selected_licensetype)]
    df_counts = df_countselected.groupby(by=['JOBTYPE','LICENSETYPE','JOBISSUEYEAR','JOBISSUEMONTH'], as_index=False).size().reset_index()
    df_counts = df_counts.rename(index=str, columns={"JOBTYPE": "JOBTYPE", "LICENSETYPE": "LICENSETYPE", "JOBISSUEYEAR": "JOBISSUEYEAR", "JOBISSUEMONTH": "JOBISSUEMONTH", 0: "Count"})
    return df_counts

layout = html.Div(children=[
                html.H1(children='Business License Volumes'),
                html.Div(children='Please Select Date Range (Job Issue Date)'),
                html.Div([
                    dcc.DatePickerRange(
                        id='slide1-BL-my-date-picker-range',
                        start_date=datetime(2016, 1, 1),
                        end_date=datetime.now()
                    ),
                ]),
                html.Div([
                    dcc.Dropdown(
                        id='slide1-BL-jobtype-dropdown',
                        options=[
                            {'label': 'All', 'value': 'All'},
                            {'label': 'Application', 'value': 'Application'},
                            {'label': 'Renewal', 'value': 'Renewal'}
                        ],
                        value='All'
                    ),
                ], style={'width': '30%', 'display': 'inline-block'}),
                html.Div([
                    dcc.Dropdown(
                        id='slide1-BL-licensetype-dropdown',
                        options=[{'label': k, 'value': k} for k in unique_licensetypes],
                        value='All'
                    ),
                ], style={'width': '30%', 'display': 'inline-block'}),
                dcc.Graph(id='slide1-BL-my-graph',
                    figure=go.Figure(
                        data=[
                            go.Scatter(
                                x=df_counts['JOBISSUEMONTHYEAR'],
                                y=df_counts['COUNTJOBS'],
                                mode='lines',
                                line=dict(
                                    shape='spline',
                                    color='rgb(26, 118, 255)'
                                )
                            )
                        ],
                    ),
                ),
                html.Div([
                    html.A(
                        'Download Data',
                        id='slide1-BL-count-table-download-link',
                        download='slide1_BL_license_volumes_counts.csv',
                        href='',
                        target='_blank',
                    )
                ], style={'text-align': 'right'}),
                table.DataTable(
                    # Initialise the rows
                    rows=[{}],
                    columns=["JOBTYPE", "LICENSETYPE", "JOBISSUEYEAR","JOBISSUEMONTH", "Count"],
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    id='slide1-BL-count-table'
                ),
                ])

@app.callback(
    Output('slide1-BL-my-graph', 'figure'),
    [Input('slide1-BL-my-date-picker-range', 'start_date'),
     Input('slide1-BL-my-date-picker-range', 'end_date'),
     Input('slide1-BL-jobtype-dropdown', 'value'),
     Input('slide1-BL-licensetype-dropdown', 'value')])
def update_graph(start_date, end_date, jobtype, licensetype):
    df_counts = update_counts_graph_data(start_date, end_date, jobtype, licensetype)
    return {
        'data': [
             go.Scatter(
                 x=df_counts['JOBISSUEMONTHYEAR'],
                 y=df_counts['Count'],
                 mode='lines',
                 line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                 )
             )
         ],
        'layout': go.Layout(
            yaxis= dict(title='Number of Business Licenses Issued')
        )
    }

@app.callback(
    Output('slide1-BL-count-table', 'rows'),
    [Input('slide1-BL-my-date-picker-range', 'start_date'),
     Input('slide1-BL-my-date-picker-range', 'end_date'),
     Input('slide1-BL-jobtype-dropdown', 'value'),
     Input('slide1-BL-licensetype-dropdown', 'value')])
def update_count_table(start_date, end_date, jobtype, licensetype):
    df_counts = update_counts_table_data(start_date, end_date, jobtype, licensetype)
    return df_counts.to_dict('records')

@app.callback(
    Output('slide1-BL-count-table-download-link', 'href'),
    [Input('slide1-BL-my-date-picker-range', 'start_date'),
     Input('slide1-BL-my-date-picker-range', 'end_date'),
     Input('slide1-BL-jobtype-dropdown', 'value'),
     Input('slide1-BL-licensetype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, jobtype, licensetype):
    df = update_counts_table_data(start_date, end_date, jobtype, licensetype)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string