import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
import urllib.parse
import datetime

from app import app, con

testing_mode = True
print('slide4.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('Slide4_BL.csv', parse_dates={'LICENSEISSUEDATE': {'format': '%m-%d-%Y'}})
    
else:
    with con() as con:
        with open(r'queries/licenses/FinalQueries_SQL/slide4_submittal_volumes_BL_ind_records_query.sql') as sql:
            df = (pd.read_sql(sql=sql.read(), con=con, parse_dates={'LICENSEISSUEDATE': {'format': '%m-%d-%Y'}})
                    .sort_values(by='LICENSEISSUEDATE'))

df_chart_by_month = (df.copy(deep=True)
                       .assign(LICENSEISSUEDATE=pd.to_datetime(df.LICENSEISSUEDATE.dt.strftime('%b-%Y')))
                       .groupby(['LICENSEISSUEDATE', 'CREATEDBYTYPE', 'JOBTYPE'])['LICENSENUMBERCOUNT']
                       .sum()
                       .reset_index())

df_chart_by_quarter = (df.copy(deep=True)
                         .assign(LICENSEISSUEDATE=df.LICENSEISSUEDATE.dt.to_period('Q-JUN'))
                         .groupby(['LICENSEISSUEDATE', 'CREATEDBYTYPE', 'JOBTYPE'])['LICENSENUMBERCOUNT']
                         .sum()
                         .reset_index()
                         # Convert LICENSEISSUEDATE to string to avoid JSON serialization error with Period Datetime Objects
                         .assign(LICENSEISSUEDATE=lambda row: row.LICENSEISSUEDATE.map(str)))

df_created_by_type = (df.copy(deep=True)
                        .groupby(['CREATEDBYTYPE'])['LICENSENUMBERCOUNT']
                        .sum())

df_job_type = (df.copy(deep=True)
                 .groupby(['JOBTYPE'])['LICENSENUMBERCOUNT']
                 .sum())

def get_data_object(user_selection):
    return df[df['CREATEDBYTYPE']==user_selection]

layout = html.Div([
    html.H1('Business Licenses By Submittal Type'),
    html.P('Filter the data using the dropdowns below:'),
    html.Div([
        html.Div([
            html.P('Created by Type'),
            dcc.Dropdown(
                id='slide4BL-dropdown-one',
                options=[
                    {'label': 'Staff', 'value': 'Staff'},
                    {'label': 'Online', 'value': 'Online'}
                ],
                multi=True,
                value=['Staff', 'Online'],
            )
        ], className='six columns'),
        html.Div([
            html.P('Job Type'),
            dcc.Dropdown(
                id='slide4BL-dropdown-two',
                options=[
                    {'label': 'Renewal', 'value': 'Renewal'},
                    {'label': 'Application', 'value': 'Application'}
                ],
                multi=True,
                value=['Renewal', 'Application'],
            )
        ], className='six columns') 
    ], className='dashrow'),
    html.Div([
        html.Div([
            dcc.Graph(id='slide4BL-createdbytype-piechart',
                figure=go.Figure(
                    data=[
                        go.Pie(
                            labels=df_created_by_type.index,
                            values=df_created_by_type.values,
                            hoverinfo='label+value+percent', 
                            hole=0.4,
                            textfont=dict(color='#FFFFFF'),
                            marker=dict(colors=['#1a6313', '#24b766'], 
                            line=dict(color='#000000', width=2))
                        )
                    ]
                )
            )
        ], className='six columns'),
        html.Div([
            dcc.Graph(id='slide4BL-jobtype-piechart',
                figure=go.Figure(
                    data=[
                        go.Pie(
                            labels=df_job_type.index,
                            values=df_job_type.values,
                            hoverinfo='label+value+percent',
                            hole=0.4, 
                            textfont=dict(color='#FFFFFF'),
                            marker=dict(colors=['#FF7070', '#FFCD70'], 
                                line=dict(color='#000000', width=2))
                        )
                    ]
                )
            )
        ], className='six columns')
    ], className='dashrow'),     
    html.H2('Monthly View'),
    dcc.Graph(id='monthly-barchart',
        figure=go.Figure(
            data=[
                go.Bar(
                    x=df_chart_by_month.loc[df_chart_by_month['JOBTYPE'] == 'Application']['LICENSEISSUEDATE'],
                    y=df_chart_by_month.loc[df_chart_by_month['JOBTYPE'] == 'Application']['LICENSENUMBERCOUNT'],
                    name='BL New Applications',
                    marker=go.bar.Marker(
                        color='rgb(55, 83, 109)'
                    )
                ),
                go.Bar(
                    x=df_chart_by_month.loc[df_chart_by_month['JOBTYPE'] == 'Renewal']['LICENSEISSUEDATE'],
                    y=df_chart_by_month.loc[df_chart_by_month['JOBTYPE'] == 'Renewal']['LICENSENUMBERCOUNT'],
                    name='BL Renewals',
                    marker=go.bar.Marker(
                        color='rgb(26, 118, 255)'
                    )
                )
            ]
        )
    ),
    html.H2('Quarterly View'),
    dcc.Graph(id='quarterly-barchart',
        figure=go.Figure(
            data=[
                go.Bar(
                    x=df_chart_by_quarter.loc[df_chart_by_quarter['JOBTYPE'] == 'Application']['LICENSEISSUEDATE'],
                    y=df_chart_by_quarter.loc[df_chart_by_quarter['JOBTYPE'] == 'Application']['LICENSENUMBERCOUNT'],
                    name='BL New Applications',
                    marker=go.bar.Marker(
                        color='rgb(55, 83, 109)'
                    )
                ),
                go.Bar(
                    x=df_chart_by_quarter.loc[df_chart_by_quarter['JOBTYPE'] == 'Renewal']['LICENSEISSUEDATE'],
                    y=df_chart_by_quarter.loc[df_chart_by_quarter['JOBTYPE'] == 'Renewal']['LICENSENUMBERCOUNT'],
                    name='BL Renewals',
                    marker=go.bar.Marker(
                        color='rgb(26, 118, 255)'
                    )
                )
            ]   
        )
    ),
    html.Div([
        html.A(
            'Download Data',
            id='Slide4BL-download-link',
            download='Slide4BL.csv',
            href='',
            target='_blank',
        )
    ], style={'text-align': 'right'})
])

# @app.callback(
#     Output('Slide4BL-table', 'rows'), 
#     [Input('field-dropdown', 'value')])
# def update_table(user_selection):
#     df = get_data_object(user_selection)
#     return df.to_dict('records')

# @app.callback(
#     Output('Slide4BL-download-link', 'href'),
#     [Input('field-dropdown', 'value')])
# def update_download_link(user_selection):
#     df = get_data_object(user_selection)
#     csv_string = df.to_csv(index=False, encoding='utf-8')
#     csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
#     return csv_string

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=5001)