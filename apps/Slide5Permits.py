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

testing_mode = True
print('slide5Permits.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('test_data/Slide5_Permits.csv', parse_dates=['PERMITAPPLICATIONDATE', 'PERMITISSUEDATE', 'REVIEWISSUEDATE', 'PAIDDTTM'])

else:
    with con_LIDB() as con_LIDB:
        with open(r'queries/permits/Slide5_accelerated_reviews.sql') as sql:
            df = pd.read_sql_query(sql=sql.read(), con=con_LIDB, parse_dates=['PERMITAPPLICATIONDATE', 'PERMITISSUEDATE', 'REVIEWISSUEDATE', 'PAIDDTTM'])

# Rename the columns to be more readable
df = (df.rename(columns={'APNO': 'Permit Number', 'PERMITAPPLICATIONDATE': 'Permit Application Date', 'PERMITISSUEDATE': 'Permit Issue Date', 'PERMITDESCRIPTION': 'Permit Type', 'WORKTYPE': 'Work Type'}))

df['Permit Type'] = df['Permit Type'].astype(str)
df['Permit Type'] = df['Permit Type'].map(lambda x: x.replace(" PERMIT", ""))
df['Permit Type'] = df['Permit Type'].str.lower()
df['Permit Type'] = df['Permit Type'].str.title()

unique_permittypes = df['Permit Type'].unique()
unique_permittypes.sort()
unique_permittypes = np.append(['All'], unique_permittypes)

df['Work Type'] = df['Work Type'].fillna('None').astype(str)

unique_worktypes = df['Work Type'].unique()
unique_worktypes.sort()
unique_worktypes = np.append(['All'], unique_worktypes)

total_accel_review_volume = '{:,.0f}'.format(len(df.index))

def update_table_data(selected_start, selected_end, selected_permittype, selected_worktype):
    df_selected = df.copy(deep=True)

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]
    if selected_worktype != "All":
        df_selected = df_selected[(df_selected['Work Type'] == selected_worktype)]

    df_selected_grouped = (df_selected.loc[(df['Permit Issue Date'] >= selected_start) & (df_selected['Permit Issue Date'] <= selected_end)]
                            .groupby('SLACOMPLIANCE')
                            .agg({'Permit Number': 'count', 'HOURS': 'mean'})
                            .reset_index()
                            .rename(columns={'Permit Number': '# of Accelerated Reviews', 'HOURS': 'Avg. Hours Per Review'}))
    df_selected_grouped['Avg. Hours Per Review'] = df_selected_grouped['Avg. Hours Per Review'].map('{:,.2f}'.format)
    df_selected_grouped['% Within SLA'] = df_selected_grouped['# of Accelerated Reviews'] / len(df_selected) * 100
    df_selected_grouped['% Within SLA'] = df_selected_grouped['% Within SLA'].round(0).map('{:,.0f}%'.format)
    return df_selected_grouped.sort_values(by=['# of Accelerated Reviews'], ascending=False)

layout = html.Div(children=[
                html.H1('Accelerated Reviews', style={'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Permit Application Date'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='slide5-permits-date-picker-range',
                            start_date=datetime(2016, 1, 1),
                            end_date=datetime.now()
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by Permit Type'),
                        dcc.Dropdown(
                                id='slide5-permits-permittype-dropdown',
                                options=[{'label': k, 'value': k} for k in unique_permittypes],
                                value='All'
                        ),
                    ], className='four columns'),
                    html.Div([
                        html.P('Filter by Work Type'),
                        dcc.Dropdown(
                            id='slide5-permits-worktype-dropdown',
                            options=[{'label': k, 'value': k} for k in unique_worktypes],
                            value='All'
                        ),
                    ], className='four columns'),
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        html.H3('Accelerated Reviews', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                columns=['SLACOMPLIANCE', '# of Accelerated Reviews', '% Within SLA', 'Avg. Hours Per Review'],
                                editable=False,
                                sortable=True,
                                id='slide5-permits-count-table'
                            ),
                        ], style={'text-align': 'center'},
                           id='slide5-permits-count-table-div'
                        ),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='slide5-permits-count-table-download-link',
                                download='slide5_permit_volumes_counts.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'width': '75%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow')
            ])


@app.callback(
    Output('slide5-permits-count-table', 'rows'),
    [Input('slide5-permits-date-picker-range', 'start_date'),
     Input('slide5-permits-date-picker-range', 'end_date'),
     Input('slide5-permits-permittype-dropdown', 'value'),
     Input('slide5-permits-worktype-dropdown', 'value')])
def update_table(start_date, end_date, permittype, worktype):
    df = update_table_data(start_date, end_date, permittype, worktype)
    return df.to_dict('records')

@app.callback(
    Output('slide5-permits-count-table-download-link', 'href'),
    [Input('slide5-permits-date-picker-range', 'start_date'),
     Input('slide5-permits-date-picker-range', 'end_date'),
     Input('slide5-permits-permittype-dropdown', 'value'),
     Input('slide5-permits-worktype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, permittype, worktype):
    df = update_table_data(start_date, end_date, permittype, worktype)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string