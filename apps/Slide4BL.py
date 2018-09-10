import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output
import urllib.parse
import datetime
import cx_Oracle

from app import con


app = dash.Dash()
server = app.server

with con() as con:
    sql_chart = """SELECT DISTINCT licensenumber, issuedate, createdbytype, jobtype, licensetype, licenselink FROM( ( SELECT DISTINCT ( CASE WHEN ap.createdby LIKE '%2%' THEN 'Online' WHEN ap.createdby LIKE '%3%' THEN 'Online' WHEN ap.createdby LIKE '%4%' THEN 'Online' WHEN ap.createdby LIKE '%5%' THEN 'Online' WHEN ap.createdby LIKE '%6%' THEN 'Online' WHEN ap.createdby LIKE '%7%' THEN 'Online' WHEN ap.createdby LIKE '%7%' THEN 'Online' WHEN ap.createdby LIKE '%9%' THEN 'Online' WHEN ap.createdby = 'PPG User' THEN 'Online' WHEN ap.createdby = 'POSSE system power user' THEN 'Revenue' ELSE 'Staff' END) AS createdbytype, ( CASE WHEN ap.applicationtype LIKE 'Application' THEN 'Application' END ) jobtype, lic.initialissuedate issuedate, lt.name licensetype, lic.licensenumber licensenumber, ( CASE WHEN ap.applicationtype LIKE 'Application' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1244067&objectHandle=' || lic.objectid || '&processHandle=&paneId=1244067_3' END ) AS licenselink FROM lmscorral.bl_license lic, lmscorral.bl_licensetype lt, query.j_bl_application ap, query.r_bl_application_license apl WHERE lt.objectid = lic.licensetypeobjectid (+) AND lic.objectid = apl.licenseobjectid (+) AND apl.applicationobjectid = ap.objectid (+) AND lic.initialissuedate > '01-APR-16' AND lic.initialissuedate < SYSDATE AND ap.applicationtype = 'Application' ) UNION ( SELECT DISTINCT ( CASE WHEN ap.createdby LIKE '%2%' THEN 'Online' WHEN ap.createdby LIKE '%3%' THEN 'Online' WHEN ap.createdby LIKE '%4%' THEN 'Online' WHEN ap.createdby LIKE '%5%' THEN 'Online' WHEN ap.createdby LIKE '%6%' THEN 'Online' WHEN ap.createdby LIKE '%7%' THEN 'Online' WHEN ap.createdby LIKE '%7%' THEN 'Online' WHEN ap.createdby LIKE '%9%' THEN 'Online' WHEN ap.createdby = 'PPG User' THEN 'Online' WHEN ap.createdby = 'POSSE system power user' THEN 'Revenue' ELSE 'Staff' END ) AS createdbytype, ( CASE WHEN ar.applicationtype LIKE 'Renewal' THEN 'Renewal' END ) jobtype, ar.issuedate issuedate, lt.name licensetype, lic.licensenumber licensenumber, ( CASE WHEN ar.applicationtype LIKE 'Renewal' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1244067&objectHandle=' || lic.objectid || '&processHandle=&paneId=1244067_3' END ) AS licenselink FROM lmscorral.bl_amendmentrenewal ar, query.r_bl_amendrenew_license rla, lmscorral.bl_license lic, lmscorral.bl_licensetype lt, query.j_bl_application ap, query.r_bl_application_license apl WHERE lic.licensetypeobjectid = lt.objectid AND lic.objectid = apl.licenseobjectid AND apl.applicationobjectid = ap.objectid AND lic.objectid = rla.licenseid AND rla.amendrenewid = ar.jobid AND lt.name NOT LIKE 'Activity' AND ar.statusdescription LIKE 'Approved' AND ar.applicationtype LIKE 'Renewal' AND ar.issuedate > '01-APR-16' AND ar.issuedate < SYSDATE ) ) ORDER BY issuedate, createdbytype, jobtype, licensetype, licensenumber"""
    df_chart = pd.read_sql(sql=sql_chart, con=con, parse_dates=['ISSUEDATE'])

df_chart_by_month = (df_chart.copy(deep=True)
                             .assign(ISSUEDATE=pd.to_datetime(df_chart.ISSUEDATE.dt.strftime('%b-%Y')))
                             .groupby(['ISSUEDATE', 'CREATEDBYTYPE', 'JOBTYPE'])
                             .sum()
                             .sort_values(by='ISSUEDATE')
                             .reset_index())

df_chart_by_quarter = (df_chart.copy(deep=True)
                               .assign(ISSUEDATE=df_chart.ISSUEDATE.dt.to_period('Q-JUN'))
                               .groupby(['ISSUEDATE', 'CREATEDBYTYPE', 'JOBTYPE'])
                               .sum()
                               .sort_values(by='ISSUEDATE')
                               .reset_index()
                               # Convert ISSUEDATE to string to avoid JSON serialization error with Period Datetime Objects
                               .assign(ISSUEDATE=lambda row: row.ISSUEDATE.map(str)))

df_created_by_type = (df_chart.copy(deep=True)
                              .groupby(['CREATEDBYTYPE'])
                              .sum()
                              .reset_index())

df_job_type = (df_chart.copy(deep=True)
                       .groupby(['JOBTYPE'])
                       .sum()
                       .reset_index())

def get_data_object(user_selection):
    return df_chart[df_chart['CREATEDBYTYPE']==user_selection]

app.layout = html.Div([
    html.H1('Business Licenses By Submittal Type'),
    html.Div(
        [
            html.Div(
                [
                    html.P('Filter the data', style={'float': 'right'}),
                    html.P('using the checkboxes below:', style={'float': 'right'}),
                    html.Br(),
                    dcc.Checklist(
                        id='checklist-one',
                        options=[
                            {'label': 'Staff', 'value': 'Staff'},
                            {'label': 'Online', 'value': 'Online'}
                        ],
                        values=['Staff', 'Online'],
                        style={'float': 'right'}
                    ),
                    html.Br(),
                    dcc.Checklist(
                        id='checklist-two',
                        options=[
                            {'label': 'Renewal', 'value': 'Renewal'},
                            {'label': 'Application', 'value': 'Application'}
                        ],
                        values=['Renewal', 'Application'],
                        style={'float': 'right'}
                    )
                ], 
                className='two columns'
            ),
            html.Div(
                [
                    dcc.Graph(id='createdbytype-piechart',
                        figure=go.Figure(
                            data=[
                                go.Pie(
                                    labels=df_created_by_type['CREATEDBYTYPE'],
                                    values=df_created_by_type['COUNTLICENSES'],
                                    hoverinfo='label+percent', 
                                    textinfo='value',
                                    textfont=dict(color='#FFFFFF'),
                                    marker=dict(colors=['#1a6313', '#24b766'], 
                                        line=dict(color='#000000', width=2)))
                            ]
                        )
                    )
                ], className='four columns'
            ),
            html.Div(
                [
                    dcc.Graph(id='jobtype-piechart',
                        figure=go.Figure(
                            data=[
                                go.Pie(
                                    labels=df_job_type['JOBTYPE'],
                                    values=df_job_type['COUNTLICENSES'],
                                    hoverinfo='label+percent', 
                                    textinfo='value',
                                    textfont=dict(color='#FFFFFF'),
                                    marker=dict(colors=['rgb(55, 83, 109)', 'rgb(26, 118, 255)'], 
                                        line=dict(color='#000000', width=2)))
                            ]
                        )
                    )
                ], className='four columns'
            )
        ], className='row'
    ),
    html.H2('Monthly View'),
    dcc.Graph(id='monthly-barchart',
        figure=go.Figure(
            data=[
                go.Bar(
                    x=df_chart_by_month.loc[df_chart_by_month['JOBTYPE'] == 'Application']['ISSUEDATE'],
                    y=df_chart_by_month.loc[df_chart_by_month['JOBTYPE'] == 'Application']['COUNTLICENSES'],
                    name='BL New Applications',
                    marker=go.bar.Marker(
                        color='rgb(55, 83, 109)'
                    )
                ),
                go.Bar(
                    x=df_chart_by_month.loc[df_chart_by_month['JOBTYPE'] == 'Renewal']['ISSUEDATE'],
                    y=df_chart_by_month.loc[df_chart_by_month['JOBTYPE'] == 'Renewal']['COUNTLICENSES'],
                    name='BL Renewals',
                    marker=go.bar.Marker(
                        color='rgb(26, 118, 255)'
                    )
                )
            ],
            layout=go.Layout(
                showlegend=True,
                legend=go.layout.Legend(
                    x=.75,
                    y=1
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=30),
                xaxis=dict(
                    title='Month'
                )
            )   
        )
    ),
    html.H2('Quarterly View'),
    dcc.Graph(id='quarterly-barchart',
        figure=go.Figure(
            data=[
                go.Bar(
                    x=df_chart_by_quarter.loc[df_chart_by_quarter['JOBTYPE'] == 'Application']['ISSUEDATE'],
                    y=df_chart_by_quarter.loc[df_chart_by_quarter['JOBTYPE'] == 'Application']['COUNTLICENSES'],
                    name='BL New Applications',
                    marker=go.bar.Marker(
                        color='rgb(55, 83, 109)'
                    )
                ),
                go.Bar(
                    x=df_chart_by_quarter.loc[df_chart_by_quarter['JOBTYPE'] == 'Renewal']['ISSUEDATE'],
                    y=df_chart_by_quarter.loc[df_chart_by_quarter['JOBTYPE'] == 'Renewal']['COUNTLICENSES'],
                    name='BL Renewals',
                    marker=go.bar.Marker(
                        color='rgb(26, 118, 255)'
                    )
                )
            ],
            layout=go.Layout(
                showlegend=True,
                legend=go.layout.Legend(
                    x=.75,
                    y=1
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=30),
                                xaxis=dict(
                    title='Fiscal Quarter'
                )
            )   
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
    ], style={'text-align': 'right'}),
    dt.DataTable(
        # Initialise the rows
        rows=[{}],
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='Slide4BL-table'
    )
], className='ten columns offset-by-one')

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