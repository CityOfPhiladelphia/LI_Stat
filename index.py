import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from gevent.pywsgi import WSGIServer

from app import app, server
from apps import Slide4BL


app.layout = html.Div([
    html.Nav(className = 'navbar navbar-dark bg-dark', 
             children =[
                html.A('Home', className="navbar-brand", href='/'),
                       ]
            ),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])

index_page = html.Div([
    html.Img(src='/assets/city-of-philadelphia-logo.png'),
    html.H2('Licenses & Inspections'),
    html.Br(),
    html.H3('LI Stat Dashboards'),
    html.Br(),
    dcc.Link('Business Licenses Mode of Submittal (Online, In-person, Mail)', href='/apps/Slide4BL')
], style={'text-align': 'center'})


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/Slide4BL':
        return Slide4BL.layout
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=5001)
    # http_server = WSGIServer(('0.0.0.0', 5000), server)
    # http_server.serve_forever()