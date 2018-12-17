import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from gevent.pywsgi import WSGIServer

from app import app, server
from apps import (Slide1BL, Slide1TL, Slide2BL, Slide2TL, Slide3BL, Slide4BL, Slide4TL,
                  Slide1Permits, Slide2Permits, Slide3Permits, Slide5Permits,
                  ImmDang, Unsafes, PublicDemos, UninspectedServiceRequests)
from send_email import send_email

app.layout = html.Div([
                html.Nav([
                    html.P('City of Philadelphia | LI Stat'),
                    html.Div([
                        html.Button('Miscellaneous', className='dropbtn'),
                        html.Div([
                            html.A('Imminently Dangerous Properties', href='/imminently-dangerous'),
                            html.A('Unsafe Properties', href='/unsafes'),
                            html.A('Public Demolitions', href='/public-demos'),
                            html.A('Uninspected Service Requests', href='/uninspected-service-requests')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                    html.Div([
                        html.Button('Permits', className='dropbtn'),
                        html.Div([
                            html.A('Volumes and Revenues', href='/permit-volumes-and-revenues'),
                            html.A('Trends', href='/permit-trends'),
                            html.A('OTC vs Review', href='/permits-otc-vs-review'),
                            html.A('Accelerated Reviews', href='/permits-accelerated-review')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                    html.Div([
                        html.Button('Trade Licenses', className='dropbtn'),
                        html.Div([
                            html.A('Volumes', href='/trade-license-volumes'),
                            html.A('Revenue', href='/trade-license-revenue'),
                            html.A('Trends', href='/trade-license-trends'),
                            html.A('Submittal Type', href='/trade-license-submittal-types')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                    html.Div([
                        html.Button('Business Licenses', className='dropbtn'),
                        html.Div([
                            html.A('Volumes', href='/business-license-volumes'),
                            html.A('Revenue', href='/business-license-revenue'),
                            html.A('Trends', href='/business-license-trends'),
                            html.A('Submittal Type', href='/business-license-submittal-types')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                ], className='navbar'),
                html.Div([
                    dcc.Location(id='url', refresh=False),
                    html.Div(id='page-content'),
                    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
                ], className='container', style={'margin': 'auto', 'margin-bottom': '45px'}),
                html.Nav([
                    html.Div([
                        html.A('Contact LI GIS Team',
                               href='mailto:ligisteam@phila.gov',
                               style={'color': '#f2f2f2', 'float': 'left', 'margin-right': '10px'}),
                        html.A('GitHub',
                               href='https://github.com/CityOfPhiladelphia/LI_Stat',
                               style={'color': '#f2f2f2', 'float': 'left', 'margin-left': '10px'})
                    ], style={'width': '500px', 'margin-left': 'auto', 'margin-right': 'auto'})
                ], className='footer-navbar')
            ])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/business-license-volumes':
        return Slide1BL.layout
    elif pathname == '/trade-license-volumes':
        return Slide1TL.layout
    elif pathname == '/business-license-revenue':
        return Slide2BL.layout
    elif pathname == '/trade-license-revenue':
        return Slide2TL.layout
    elif pathname == '/business-license-trends':
        return Slide3BL.layout
    elif pathname == '/business-license-submittal-types':
        return Slide4BL.layout
    elif pathname == '/trade-license-submittal-types':
        return Slide4TL.layout
    elif pathname == '/permit-volumes-and-revenues':
        return Slide1Permits.layout
    elif pathname == '/permit-trends':
        return Slide2Permits.layout
    elif pathname == '/permits-otc-vs-review':
        return Slide3Permits.layout
    elif pathname == '/permits-accelerated-review':
        return Slide5Permits.layout
    elif pathname == '/public-demos':
        return PublicDemos.layout
    elif pathname == '/imminently-dangerous':
        return ImmDang.layout
    elif pathname == '/unsafes':
        return Unsafes.layout
    elif pathname == '/uninspected-service-requests':
        return UninspectedServiceRequests.layout
    else:
        return Slide1BL.layout

if __name__ == '__main__':
    #app.run_server(host='127.0.0.1', port=5001)
    try:
        http_server = WSGIServer(('0.0.0.0', 5000), server)
    except:
        send_email()

    print('Server has loaded.')
    http_server.serve_forever()
