import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from gevent.pywsgi import WSGIServer

from app import app, server
from apps import (Slide1BL, Slide1TL, Slide2, Slide3BL, Slide4BL, Slide4TL,
                  Slide1Permits, Slide2Permits, Slide3Permits, Slide5Permits,
                  ImmDang, Unsafes, PublicDemos)
from send_email import send_email


app.layout = html.Div([
                html.Nav([
                    html.P('City of Philadelphia | LI Stat'),
                    html.Div([
                        html.Button('Miscellaneous', className='dropbtn'),
                        html.Div([
                            html.A('Imminently Dangerous Properties', href='/ImmDang'),
                            html.A('Unsafe Properties', href='/Unsafes'),
                            html.A('Public Demolitions', href='/PublicDemos')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                    html.Div([
                        html.Button('Permits', className='dropbtn'),
                        html.Div([
                            html.A('Volumes and Revenues', href='/Slide1Permits'),
                            html.A('Trends', href='/Slide2Permits'),
                            html.A('OTC vs Review', href='/Slide3Permits'),
                            html.A('Accelerated Reviews', href='/Slide5Permits')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                    html.A('License Revenue', href='/Slide2'),
                    html.Div([
                        html.Button('Trade Licenses', className='dropbtn'),
                        html.Div([
                            html.A('Volumes', href='/Slide1TL'),
                            html.A('Trends', href='/Slide3TL'),
                            html.A('Submittal Type', href='/Slide4TL')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                    html.Div([
                        html.Button('Business Licenses', className='dropbtn'),
                        html.Div([
                            html.A('Volumes', href='/Slide1BL'),
                            html.A('Trends', href='/Slide3BL'),
                            html.A('Submittal Type', href='/Slide4BL')
                        ], className='dropdown-content')
                    ], className='dropdown'),
                ], className='navbar'),
                html.Div([
                    dcc.Location(id='url', refresh=False),
                    html.Div(id='page-content'),
                    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
                ], className='container', style={'margin': 'auto'}),
                html.Nav([
                    html.A('Questions? Click Here to Contact LI GIS Team', href='mailto:ligisteam@phila.gov')
                ], className='footer-navbar')
            ])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/Slide1BL':
        return Slide1BL.layout
    elif pathname == '/Slide1TL':
        return Slide1TL.layout
    elif pathname == '/Slide2':
        return Slide2.layout
    elif pathname == '/Slide3BL':
        return Slide3BL.layout
    elif pathname == '/Slide4BL':
        return Slide4BL.layout
    elif pathname == '/Slide4TL':
        return Slide4TL.layout
    elif pathname == '/Slide1Permits':
        return Slide1Permits.layout
    elif pathname == '/Slide2Permits':
        return Slide2Permits.layout
    elif pathname == '/Slide3Permits':
        return Slide3Permits.layout
    elif pathname == '/Slide5Permits':
        return Slide5Permits.layout
    elif pathname == '/PublicDemos':
        return PublicDemos.layout
    elif pathname == '/ImmDang':
        return ImmDang.layout
    elif pathname == '/Unsafes':
        return Unsafes.layout
    else:
        return Slide1BL.layout

if __name__ == '__main__':
    #app.run_server(host='127.0.0.1', port=5001)
    try:
        http_server = WSGIServer(('0.0.0.0', 8000), server) 
    except:
        send_email()

    http_server.serve_forever()
