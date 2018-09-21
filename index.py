import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from gevent.pywsgi import WSGIServer

from app import app, server
# from apps import Slide1BL, Slide1TL, Slide2
from apps import Slide2


app.layout = html.Div(className='ten columns offset-by-one', children=[
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])
    
index_page = html.Div([
    html.H2('Licenses & Inspections'),
    html.Br(),
    html.H3('LI Stat Dashboards'),
    html.Br(),
    dcc.Link('Business Licenses Volumes', href='/Slide1BL'),
    html.Br(),
    dcc.Link('Trade Licenses Volumes', href='/Slide1TL')
], style={'text-align': 'center'})


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    # if pathname == '/Slide1BL':
    #     return Slide1BL.layout
    # elif pathname == '/Slide1TL':
    #     return Slide1TL.layout
    if pathname == '/Slide2':
        return Slide2.layout
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=5001)
    # http_server = WSGIServer(('0.0.0.0', 5000), server)
    # http_server.serve_forever()