import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from gevent.pywsgi import WSGIServer

from app import app, server
from apps import (BL_Volumes, TL_Volumes, BL_Revenue, TL_Revenue, BL_Trends, BL_Submittal_Type, TL_Submittal_Type,
                  Permits_Volumes_Revenues, Permits_Trends, Permits_OTC_Review, Permits_Accel_Review,
                  Imm_Dang, Unsafes, Public_Demos, Uninspected_Service_Requests)
from send_email import send_email

def serve_layout():
    return html.Div([
                html.Nav([
                    html.P('City of Philadelphia | LI Stat'),
                    html.Div([
                        html.Button('Miscellaneous', className='dropbtn'),
                        html.Div([
                            html.A('Imminently Dangerous Violations', href='/imminently-dangerous'),
                            html.A('Unsafe Violations', href='/unsafes'),
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

app.layout = serve_layout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/business-license-volumes':
        return BL_Volumes.layout()
    elif pathname == '/trade-license-volumes':
        return TL_Volumes.layout
    elif pathname == '/business-license-revenue':
        return BL_Revenue.layout()
    elif pathname == '/trade-license-revenue':
        return TL_Revenue.layout
    elif pathname == '/business-license-trends':
        return BL_Trends.layout()
    elif pathname == '/business-license-submittal-types':
        return BL_Submittal_Type.layout()
    elif pathname == '/trade-license-submittal-types':
        return TL_Submittal_Type.layout
    elif pathname == '/permit-volumes-and-revenues':
        return Permits_Volumes_Revenues.layout
    elif pathname == '/permit-trends':
        return Permits_Trends.layout
    elif pathname == '/permits-otc-vs-review':
        return Permits_OTC_Review.layout
    elif pathname == '/permits-accelerated-review':
        return Permits_Accel_Review.layout()
    elif pathname == '/public-demos':
        return Public_Demos.layout
    elif pathname == '/imminently-dangerous':
        return Imm_Dang.layout()
    elif pathname == '/unsafes':
        return Unsafes.layout
    elif pathname == '/uninspected-service-requests':
        return Uninspected_Service_Requests.layout
    else:
        return BL_Volumes.layout()

if __name__ == '__main__':
    #app.run_server(host='127.0.0.1', port=5001)
    try:
        http_server = WSGIServer(('0.0.0.0', 5000), server)
    except:
        send_email()

    print('Server has loaded.')
    http_server.serve_forever()
