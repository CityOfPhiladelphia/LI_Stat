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
print('slide3Permits.py')
print('Testing mode: ' + str(testing_mode))

if testing_mode:
    df = pd.read_csv('test_data/Slide3_all_count_monthly_permits.csv', parse_dates=['ISSUEDATE'])

else:
    with con_LIDB() as con_LIDB:
        with open(r'queries/permits/Slide3_all_count_monthly_permits.sql') as sql:
            df = pd.read_sql_query(sql=sql.read(), con=con_LIDB, parse_dates=['ISSUEDATE'])

# Rename the columns to be more readable
# Make a DateText Column to display on the graph
df = (df.rename(columns={'ISSUEDATE': 'Issue Date', 'PERMITDESCRIPTION': 'Permit Type', 'COUNTOTCPERMITS': 'OTC Permits Issued', 'COUNTREVIEWPERMITS': 'Reviewed Permits Issued'})
        .assign(DateText=lambda x: x['Issue Date'].dt.strftime('%b %Y')))

df['Permit Type'] = df['Permit Type'].map(lambda x: x.replace(" PERMIT", ""))
df['Permit Type'] = df['Permit Type'].str.lower()
df['Permit Type'] = df['Permit Type'].str.title()

unique_permittypes = df['Permit Type'].unique()
unique_permittypes = np.append(['All'], unique_permittypes)

total_otc_permit_volume = '{:,.0f}'.format(df['OTC Permits Issued'].sum())
total_review_permit_volume = '{:,.0f}'.format(df['Reviewed Permits Issued'].sum())

def update_total_otc_permit_volume(selected_start, selected_end, selected_permittype):
    df_selected = df.copy(deep=True)

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]

    df_selected = df_selected.loc[(df['Issue Date'] >= selected_start)&(df_selected['Issue Date'] <= selected_end)]
    total_otc_permit_volume = df_selected['OTC Permits Issued'].sum()
    return '{:,.0f}'.format(total_otc_permit_volume)

def update_total_review_permit_volume(selected_start, selected_end, selected_permittype):
    df_selected = df.copy(deep=True)

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]

    df_selected = df_selected.loc[(df['Issue Date'] >= selected_start)&(df_selected['Issue Date'] <= selected_end)]
    total_review_permit_volume = df_selected['Reviewed Permits Issued'].sum()
    return '{:,.0f}'.format(total_review_permit_volume)

def update_counts_graph_data(selected_start, selected_end, selected_permittype):
    df_selected = df.copy(deep=True)

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]

    df_selected = (df_selected.loc[(df['Issue Date'] >= selected_start) & (df_selected['Issue Date'] <= selected_end)]
                              .groupby(by=['Issue Date', 'DateText'])['OTC Permits Issued', 'Reviewed Permits Issued']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Issue Date']))
    return df_selected

def update_counts_table_data(selected_start, selected_end, selected_permittype):
    df_selected = df.copy(deep=True)

    if selected_permittype != "All":
        df_selected = df_selected[(df_selected['Permit Type'] == selected_permittype)]

    (df_selected.loc[(df['Issue Date']>=selected_start) & (df_selected['Issue Date']<=selected_end)]
                              .groupby(by=['Issue Date', 'Permit Type'])['OTC Permits Issued', 'Reviewed Permits Issued']
                              .sum()
                              .reset_index()
                              .sort_values(by=['Issue Date', 'Permit Type']))
    df_selected['Issue Date'] = df_selected['Issue Date'].apply(lambda x: datetime.strftime(x, '%b %Y'))
    df_selected['OTC Permits Issued'] = df_selected['OTC Permits Issued'].map('{:,.0f}'.format)
    df_selected['Reviewed Permits Issued'] = df_selected['Reviewed Permits Issued'].map('{:,.0f}'.format)
    return df_selected

layout = html.Div(children=[
                html.H1('Permits Issued: Over the Counter (OTC) vs Back Office (Reviewed)', style={'text-align': 'center'}),
                html.Div([
                    html.Div([
                        html.P('Filter by Date Range'),
                        dcc.DatePickerRange(
                            display_format='MMM Y',
                            id='slide3-permits-date-picker-range',
                            start_date=datetime(2016, 1, 1),
                            end_date=datetime.now()
                        ),
                    ], className='six columns'),
                    html.Div([
                        html.P('Filter by Permit Type'),
                        dcc.Dropdown(
                                id='slide3-permits-permittype-dropdown',
                                options=[{'label': k, 'value': k} for k in unique_permittypes],
                                value='All'
                        ),
                    ], className='five columns'),
                ], className='dashrow filters'),
                html.Div([
                    html.Div([
                        dcc.Graph(id='slide3-permits-graph',
                            figure=go.Figure(
                                data=[
                                    go.Scatter(
                                        x=df['Issue Date'],
                                        y=df['OTC Permits Issued'],
                                        mode='lines',
                                        text=df['DateText'],
                                        hoverinfo='text+y',
                                        line=dict(
                                            shape='spline',
                                            color='rgb(26, 118, 255)'
                                        ),
                                        name='OTC'
                                    ),
                                    go.Scatter(
                                        x=df['Issue Date'],
                                        y=df['Reviewed Permits Issued'],
                                        mode='lines',
                                        text=df['DateText'],
                                        hoverinfo='text+y',
                                        line=dict(
                                            shape='spline',
                                            color='#ff7f0e'
                                        ),
                                        name='Reviewed'
                                    )
                                ],
                                layout=go.Layout(
                                    title='Permits Issued: OTC vs Reviewed',
                                    yaxis=dict(
                                        title='Permits Issued'
                                    )
                                )
                            )
                        )
                    ], className='twelve columns'),
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H1('', id='slide3-otcpermits-indicator', style={'font-size': '35pt'}),
                        html.H2('OTC Permits Issued', style={'font-size': '30pt'})
                    ], className='six columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'}),
                    html.Div([
                        html.H1('', id='slide3-reviewpermits-indicator', style={'font-size': '35pt'}),
                        html.H2('Reviewed Permits Issued', style={'font-size': '30pt'})
                    ], className='six columns', style={'text-align': 'center', 'margin': 'auto', 'padding': '50px 0'})
                ], className='dashrow'),
                html.Div([
                    html.Div([
                        html.H3('OTC and Reviewed Permits Issued by Type and Month', style={'text-align': 'center'}),
                        html.Div([
                            table.DataTable(
                                rows=[{}],
                                columns=['Issue Date', 'Permit Type', 'OTC Permits Issued', 'Reviewed Permits Issued'],
                                editable=False,
                                sortable=True,
                                id='slide3-permits-count-table'
                            ),
                        ], style={'text-align': 'center'},
                           id='slide3-permits-count-table-div'
                        ),
                        html.Div([
                            html.A(
                                'Download Data',
                                id='slide3-permits-count-table-download-link',
                                download='slide3_permit_volumes_counts.csv',
                                href='',
                                target='_blank',
                            )
                        ], style={'text-align': 'right'})
                    ], style={'width': '65%', 'margin-left': 'auto', 'margin-right': 'auto','margin-top': '50px', 'margin-bottom': '50px'})
                ], className='dashrow')
            ])

@app.callback(
    Output('slide3-permits-graph', 'figure'),
    [Input('slide3-permits-date-picker-range', 'start_date'),
     Input('slide3-permits-date-picker-range', 'end_date'),
     Input('slide3-permits-permittype-dropdown', 'value')])
def update_graph(start_date, end_date, permittype):
    df = update_counts_graph_data(start_date, end_date, permittype)
    return {
        'data': [
            go.Scatter(
                x=df['Issue Date'],
                y=df['OTC Permits Issued'],
                mode='lines',
                text=df['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='rgb(26, 118, 255)'
                ),
                name='OTC'
            ),
            go.Scatter(
                x=df['Issue Date'],
                y=df['Reviewed Permits Issued'],
                mode='lines',
                text=df['DateText'],
                hoverinfo='text+y',
                line=dict(
                    shape='spline',
                    color='#ff7f0e'
                ),
                name='Reviewed'
            )
        ],
        'layout': go.Layout(
            title='Permits Issued: OTC vs Reviewed',
            yaxis=dict(
                title='Permits Issued'
            )
        )
    }

@app.callback(
    Output('slide3-otcpermits-indicator', 'children'),
    [Input('slide3-permits-date-picker-range', 'start_date'),
     Input('slide3-permits-date-picker-range', 'end_date'),
     Input('slide3-permits-permittype-dropdown', 'value')])
def update_total_otcpermits_volume_indicator(start_date, end_date, permittype):
    total_permit_volume = update_total_otc_permit_volume(start_date, end_date, permittype)
    return str(total_permit_volume)

@app.callback(
    Output('slide3-reviewpermits-indicator', 'children'),
    [Input('slide3-permits-date-picker-range', 'start_date'),
     Input('slide3-permits-date-picker-range', 'end_date'),
     Input('slide3-permits-permittype-dropdown', 'value')])
def update_total_reviewpermits_indicator(start_date, end_date, permittype):
    total_fees_paid = update_total_review_permit_volume(start_date, end_date, permittype)
    return str(total_fees_paid)

@app.callback(
    Output('slide3-permits-count-table', 'rows'),
    [Input('slide3-permits-date-picker-range', 'start_date'),
     Input('slide3-permits-date-picker-range', 'end_date'),
     Input('slide3-permits-permittype-dropdown', 'value')])
def update_count_table(start_date, end_date, permittype):
    df = update_counts_table_data(start_date, end_date, permittype)
    return df.to_dict('records')

@app.callback(
    Output('slide3-permits-count-table-download-link', 'href'),
    [Input('slide3-permits-date-picker-range', 'start_date'),
     Input('slide3-permits-date-picker-range', 'end_date'),
     Input('slide3-permits-permittype-dropdown', 'value')])
def update_count_table_download_link(start_date, end_date, permittype):
    df = update_counts_table_data(start_date, end_date, permittype)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string