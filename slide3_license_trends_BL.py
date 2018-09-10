import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import cx_Oracle
from dash.dependencies import Input, Output
import datetime
import dash_table_experiments as table
import plotly.graph_objs as go
import numpy as np
import urllib.parse

from config import USERNAME_PASSWORD_PAIRS
from app import con

app = dash.Dash()
print("dash app initialized")
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server
print("flask app initialized")

with con() as con:
    counts_query = """SELECT JobType, LicenseType, JobIssueMonthYear, JobIssueYear, JobIssueMonth, Count(DISTINCT licensenumber) CountJobs FROM((SELECT DISTINCT lt.name LicenseType, lic.externalfilenum LicenseNumber, ( CASE WHEN ap.applicationtype LIKE 'Application' THEN 'BL_Application' END) JobType, ( CASE WHEN Extract(month FROM ap.issuedate) LIKE '1' THEN 'January' WHEN Extract(month FROM ap.issuedate) LIKE '2' THEN 'February' WHEN Extract(month FROM ap.issuedate) LIKE '3' THEN 'March' WHEN Extract(month FROM ap.issuedate) LIKE '4' THEN 'April' WHEN Extract(month FROM ap.issuedate) LIKE '5' THEN 'May' WHEN Extract(month FROM ap.issuedate) LIKE '6' THEN 'June' WHEN Extract(month FROM ap.issuedate) LIKE '7' THEN 'July' WHEN Extract(month FROM ap.issuedate) LIKE '8' THEN 'August' WHEN Extract(month FROM ap.issuedate) LIKE '9' THEN 'September' WHEN Extract(month FROM ap.issuedate) LIKE '10' THEN 'October' WHEN Extract(month FROM ap.issuedate) LIKE '11' THEN 'November' WHEN Extract(month FROM ap.issuedate) LIKE '12' THEN 'December' END ) || ' ' || Extract(year FROM ap.issuedate) JobIssueMonthYear, Extract(year FROM ap.issuedate) JobIssueYear, Extract(month FROM ap.issuedate) JobIssueMonth FROM query.j_bl_application ap, query.r_bl_application_license rla, query.o_bl_license lic, lmscorral.bl_licensetype lt WHERE lic.licensetypeid = lt.objectid AND lic.objectid = rla.licenseobjectid AND rla.applicationobjectid = ap.jobid AND lt.name NOT LIKE 'Activity' AND ap.statusdescription LIKE 'Approved' AND ap.issuedate > '01-JAN-16' AND ap.issuedate <= SYSDATE) UNION SELECT DISTINCT lt.name LicenseType, lic.externalfilenum LicenseNumber, ( CASE WHEN ar.applicationtype LIKE 'Renewal' THEN 'BL_Renewal' END ) JobType, ( CASE WHEN Extract(month FROM ar.issuedate) LIKE '1' THEN 'January' WHEN Extract(month FROM ar.issuedate) LIKE '2' THEN 'February' WHEN Extract(month FROM ar.issuedate) LIKE '3' THEN 'March' WHEN Extract(month FROM ar.issuedate) LIKE '4' THEN 'April' WHEN Extract(month FROM ar.issuedate) LIKE '5' THEN 'May' WHEN Extract(month FROM ar.issuedate) LIKE '6' THEN 'June' WHEN Extract(month FROM ar.issuedate) LIKE '7' THEN 'July' WHEN Extract(month FROM ar.issuedate) LIKE '8' THEN 'August' WHEN Extract(month FROM ar.issuedate) LIKE '9' THEN 'September' WHEN Extract(month FROM ar.issuedate) LIKE '10' THEN 'October' WHEN Extract(month FROM ar.issuedate) LIKE '11' THEN 'November' WHEN Extract(month FROM ar.issuedate) LIKE '12' THEN 'December' END ) || ' ' || Extract(year FROM ar.issuedate) JobIssueMonthYear, Extract(year FROM ar.issuedate) JobIssueYear, Extract(month FROM ar.issuedate) JobIssueMonth FROM query.j_bl_amendrenew ar, query.r_bl_amendrenew_license rla, query.o_bl_license lic, lmscorral.bl_licensetype lt WHERE lic.licensetypeid = lt.objectid AND lic.objectid = rla.licenseid AND rla.amendrenewid = ar.jobid AND lt.name NOT LIKE 'Activity' AND ar.statusdescription LIKE 'Approved' AND ar.applicationtype LIKE 'Renewal' AND ar.issuedate > '01-JAN-16' AND ar.issuedate <= SYSDATE) GROUP BY jobIssueMonthYear, JobIssueYear, JobIssueMonth, JobType, LicenseType ORDER BY JobIssueYear, JobIssueMonth, JobType, LicenseType"""
    ind_records_query = """SELECT DISTINCT( CASE WHEN ap.applicationtype LIKE 'Application' THEN 'BL_Application' END) JobType, lt.name LicenseType, lic.externalfilenum LicenseNumber, ap.issuedate IssueDate, ( CASE WHEN Extract(month FROM ap.issuedate) LIKE '1' THEN 'January' WHEN Extract(month FROM ap.issuedate) LIKE '2' THEN 'February' WHEN Extract(month FROM ap.issuedate) LIKE '3' THEN 'March' WHEN Extract(month FROM ap.issuedate) LIKE '4' THEN 'April' WHEN Extract(month FROM ap.issuedate) LIKE '5' THEN 'May' WHEN Extract(month FROM ap.issuedate) LIKE '6' THEN 'June' WHEN Extract(month FROM ap.issuedate) LIKE '7' THEN 'July' WHEN Extract(month FROM ap.issuedate) LIKE '8' THEN 'August' WHEN Extract(month FROM ap.issuedate) LIKE '9' THEN 'September' WHEN Extract(month FROM ap.issuedate) LIKE '10' THEN 'October' WHEN Extract(month FROM ap.issuedate) LIKE '11' THEN 'November' WHEN Extract(month FROM ap.issuedate) LIKE '12' THEN 'December' END ) || ' ' || Extract(year FROM ap.issuedate) JobIssueMonthYear, Extract(year FROM ap.issuedate) JobIssueYear, Extract(month FROM ap.issuedate) JobIssueMonth, ( CASE WHEN ap.applicationtype LIKE 'Application' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1239699&objectHandle=' ||rla.applicationobjectid ||'&processHandle=' END ) JobLink FROM query.j_bl_application ap, query.r_bl_application_license rla, query.o_bl_license lic, lmscorral.bl_licensetype lt WHERE lic.licensetypeid = lt.objectid AND lic.objectid = rla.licenseobjectid AND rla.applicationobjectid = ap.jobid AND lt.name NOT LIKE 'Activity' AND ap.statusdescription LIKE 'Approved' AND ap.issuedate > '01-JAN-16' AND ap.issuedate <= SYSDATE UNION SELECT DISTINCT ( CASE WHEN ar.applicationtype LIKE 'Renewal' THEN 'BL_Renewal' END ) JobType, lt.name LicenseType, lic.externalfilenum LicenseNumber, ar.issuedate IssueDate, ( CASE WHEN Extract(month FROM ar.issuedate) LIKE '1' THEN 'January' WHEN Extract(month FROM ar.issuedate) LIKE '2' THEN 'February' WHEN Extract(month FROM ar.issuedate) LIKE '3' THEN 'March' WHEN Extract(month FROM ar.issuedate) LIKE '4' THEN 'April' WHEN Extract(month FROM ar.issuedate) LIKE '5' THEN 'May' WHEN Extract(month FROM ar.issuedate) LIKE '6' THEN 'June' WHEN Extract(month FROM ar.issuedate) LIKE '7' THEN 'July' WHEN Extract(month FROM ar.issuedate) LIKE '8' THEN 'August' WHEN Extract(month FROM ar.issuedate) LIKE '9' THEN 'September' WHEN Extract(month FROM ar.issuedate) LIKE '10' THEN 'October' WHEN Extract(month FROM ar.issuedate) LIKE '11' THEN 'November' WHEN Extract(month FROM ar.issuedate) LIKE '12' THEN 'December' END ) || ' ' || Extract(year FROM ar.issuedate) JobIssueMonthYear, Extract(year FROM ar.issuedate) JobIssueYear, Extract(month FROM ar.issuedate) JobIssueMonth, ( CASE WHEN ar.applicationtype LIKE 'Renewal' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1243107&objectHandle=' ||rla.amendrenewid ||'&processHandle=' END ) JobLink FROM query.j_bl_amendrenew ar, query.r_bl_amendrenew_license rla, query.o_bl_license lic, lmscorral.bl_licensetype lt WHERE lic.licensetypeid = lt.objectid AND lic.objectid = rla.licenseid AND rla.amendrenewid = ar.jobid AND lt.name NOT LIKE 'Activity' AND ar.statusdescription LIKE 'Approved' AND ar.applicationtype LIKE 'Renewal' AND ar.issuedate > '01-JAN-16' AND ar.issuedate <= SYSDATE --runtime 7-8 min"""
    #print("reading in counts data: querying database and putting results in pandas dataframe")
    #df_counts = pd.read_sql(counts_query,con)
    #print("reading in individual records: querying database and putting results in pandas dataframe")
    #df_ind_records = pd.read_sql(ind_records_query,con)


print("reading in test counts csv")
df_counts = pd.read_csv("Slide1_AppsAndRenewalsCorralByMonthLicenseTypeBL2_test_data.csv")
df_counts['JOBTYPE'] = df_counts['JOBTYPE'].map(lambda x: str(x)[3:])  # strip first 3 characters "BL_" just to make it easier for user to read

unique_licensetypes = df_counts['LICENSETYPE'].unique()
unique_licensetypes = np.append(["All"], unique_licensetypes)


print("reading in test individual records csv")
df_ind_records = pd.read_csv("Slide1_AppsAndRenewalsCorralByMonthLicenseTypeBL_individual_records_test_data.csv")
df_ind_records['ISSUEDATE'] = pd.to_datetime(df_ind_records['ISSUEDATE'], errors = 'coerce') #make sure IssueDate column is of type datetime so that filtering of dataframe based on date can happen later
df_ind_records['JOBTYPE'] = df_ind_records['JOBTYPE'].map(lambda x: str(x)[3:])  # strip first 3 characters "BL_" just to make it easier for user to read

def calculate_counts(selected_start, selected_end, selected_jobtype, selected_licensetype):
    df_countselected = df_ind_records[(df_ind_records['ISSUEDATE']>=selected_start)&(df_ind_records['ISSUEDATE']<=selected_end)]
    if selected_jobtype != "All":
        df_countselected = df_countselected[(df_countselected['JOBTYPE']==selected_jobtype)]
    if selected_licensetype != "All":
        df_countselected = df_countselected[(df_countselected['LICENSETYPE'] == selected_licensetype)]
    df_counts = df_countselected.groupby(by=['JOBTYPE','LICENSETYPE','JOBISSUEYEAR','JOBISSUEMONTH'], as_index=False).size().reset_index()
    df_counts = df_counts.rename(index=str, columns={"JOBTYPE": "JOBTYPE", "LICENSETYPE": "LICENSETYPE", "JOBISSUEYEAR": "JOBISSUEYEAR", "JOBISSUEMONTH": "JOBISSUEMONTH", 0: "Count"})
    df_counts = df_counts.sort_values(by=['JOBISSUEYEAR', 'JOBISSUEMONTH'])
    '''
    # Adding in months that had counts of 0 so there aren't any missing columns in the graph
    idx = pd.date_range(selected_start, selected_end, freq='M').to_period('m')  # Create list of all months in date range
    df_counts['JOBISSUEDAYMONTHYEAR'] = '1 ' + df_counts['JOBISSUEMONTH'].astype(str) + ' ' + df_counts['JOBISSUEYEAR'].astype(str)  # Create field that has day, month, and year so you can convert that to a Date (you have to have a day value)
    df_counts.index = pd.to_datetime(df_counts['JOBISSUEDAYMONTHYEAR'], format='%d %m %Y')  # Make index of df_counts dataframe a Date
    df_counts.index = df_counts.index.to_period('m')  # Turn index from Date to PeriodIndex
    print("duplicates in index: ")
    print(str(df_counts[df_counts.index.duplicated()]))
    df_counts = df_counts.reindex(idx)  # Reindex df_counts based on the list of ALL months in the date range so that it includes even those that didn't have any values
    df_counts['Count'].fillna(0, inplace=True)  # Give any months without a Count value the value of 0
    df_counts['JOBISSUEMONTHYEAR'] = df_counts.index.strftime('%B %Y')  # Replace the values in the JOBISSUEMONTHYEAR field with the (formatted) values from the index. The JOBISSUEMONTHYEAR field values are the ones that are going to display on the x-axis of the graph
    '''
    return df_counts

def calculate_diffs(df_counts1, df_counts2):
    df_counts2['JOBISSUEPREVYEAR'] = df_counts2['JOBISSUEYEAR'] - 1
    df_merged = df_counts1.merge(df_counts2, how="outer", left_on=['JOBTYPE','LICENSETYPE', 'JOBISSUEYEAR', 'JOBISSUEMONTH'], right_on=['JOBTYPE','LICENSETYPE', 'JOBISSUEPREVYEAR', 'JOBISSUEMONTH'])
    # Give any months without a Count value the value of 0
    df_merged['Count_x'].fillna(0, inplace=True)
    df_merged['Count_y'].fillna(0, inplace=True)
    print("df_merged.head(): " + str(df_merged.head()))
    df_merged['Difference'] = df_merged['Count_y'] - df_merged['Count_x']
    df_merged['% Difference raw'] = (df_merged['Count_y'] - df_merged['Count_x']) / df_merged['Count_x']
    df_merged['% Difference'] = pd.Series(["{0:.0f}%".format(val * 100) for val in df_merged['% Difference raw']], index = df_merged.index)
    return df_merged

def update_counts_table_data(selected_start1, selected_end1, selected_start2, selected_end2, selected_jobtype, selected_licensetype):
    df_counts1 = calculate_counts(selected_start1, selected_end1, selected_jobtype, selected_licensetype)
    df_counts2 = calculate_counts(selected_start2, selected_end2, selected_jobtype, selected_licensetype)
    df_counts_and_diffs = calculate_diffs(df_counts1, df_counts2)
    return df_counts_and_diffs

app.layout = html.Div(children=[
                html.H1(children='Business Licenses'),
                html.Div(children='Please Select Date Range (Job Issue Date)'),
                html.Div([
                    dcc.DatePickerRange(
                        id='slide3-BL-my-date-picker-range-1',
                        start_date=datetime.datetime.now() - datetime.timedelta(days=364) - datetime.timedelta(days=365),
                        end_date=datetime.datetime.now() - datetime.timedelta(days=365)
                    ),
                ]),
                html.Div([
                    dcc.DatePickerRange(
                        id='slide3-BL-my-date-picker-range-2',
                        start_date=datetime.datetime.now() - datetime.timedelta(days=364),
                        end_date=datetime.datetime.now()
                    ),
                ]),
                html.Div([
                    dcc.Dropdown(
                        id='slide3-BL-jobtype-dropdown',
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
                        id='slide3-BL-licensetype-dropdown',
                        options=[{'label': k, 'value': k} for k in unique_licensetypes],
                        value='All'
                    ),
                ], style={'width': '30%', 'display': 'inline-block'}),
                table.DataTable(
                    # Initialise the rows
                    rows=[{}],
                    columns=["JOBTYPE", "LICENSETYPE", "JOBISSUEYEAR_x", "JOBISSUEYEAR_y", "JOBISSUEMONTH", "Count_x", "Count_y", "Difference", "% Difference"],
                    row_selectable=True,
                    filterable=True,
                    sortable=True,
                    selected_row_indices=[],
                    id='slide3-BL-count-table'
                )
                ])
@app.callback(
    Output('slide3-BL-count-table', 'rows'),
    [Input('slide3-BL-my-date-picker-range-1', 'start_date'),
     Input('slide3-BL-my-date-picker-range-1', 'end_date'),
     Input('slide3-BL-my-date-picker-range-2', 'start_date'),
     Input('slide3-BL-my-date-picker-range-2', 'end_date'),
     Input('slide3-BL-jobtype-dropdown', 'value'),
     Input('slide3-BL-licensetype-dropdown', 'value')])
def update_count_table(start_date1, end_date1, start_date2, end_date2, jobtype, licensetype):
    df_counts = update_counts_table_data(start_date1, end_date1, start_date2, end_date2, jobtype, licensetype)
    return df_counts.to_dict('records')

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=5003)