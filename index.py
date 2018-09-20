import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output
from gevent.pywsgi import WSGIServer

from app import app, server
from apps import Slide1BL

app.index_string = '''
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta http-equiv="x-ua-compatible" content="ie=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>LI Stat | City of Philadelphia</title>
  <link rel="stylesheet" type="text/css" href="https://unpkg.com/phila-standards@0.11.2/dist/css/phila-app.min.css">
  <link rel="shortcut icon" type="image/x-icon" href="https://standards.phila.gov/img/favicon.png"> <meta name="twitter:card" content="summary">
<meta property="og:title" content=""> 
<meta property="og:description" content=""> 
<meta property="og:type" content="website">
<meta property="og:url" content="">
<meta property="og:site_name" content="Digital Standards | City of Philadelphia">
<meta property="og:image" content="https://beta.phila.gov/media/20160715133810/phila-gov.jpg">

</head>
<body lang="en">
  <div id="application">
  <!-- Begin header -->
  <header class="site-header app group">
    <div class="row expanded">
      <!-- if you don't want a full-width header, remove the expanded class -->
      <div class="columns">
        <a href="http://beta.phila.gov/" class="logo">
          <img src="https://standards.phila.gov/img/logo/city-of-philadelphia-yellow-white.png" alt="City of Philadelphia">
        </a>
        <div class="app-divide"></div>
        <div class="page-title-container">
          <a href="/">
            <h1 class="page-title">LI Stat</h1>
            <h2 class="page-subtitle">For Internal Use Only</h2>
          </a>
        </div>
      </div>
    </div>
  </header>
  <main id="main">
    {%app_entry%}
  </main>
    <div class="app-footer anchor">
    <!-- remove the anchor class if you want to handle footer placement yourself, otherwise it will be postion: fixed -->
    <footer>
      {%config%}
      {%scripts%}
      <div class="row expanded">
        <div class="columns">
          <nav>
            <ul class="inline-list">
              <li>
                <a href="mailto:ligisteam@phila.gov">Questions? Click Here to Contact LIGISTeam</a>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </footer>
  </div>
</div>
'''
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])

index_page = html.Div([
    html.H2('Licenses & Inspections'),
    html.Br(),
    html.H3('LI Stat Dashboards'),
    html.Br(),
    dcc.Link('Business Licenses Mode of Submittal (Online, In-person, Mail)', href='/apps/Slide4BL')
], style={'text-align': 'center'})


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/Slide1BL':
        return Slide1BL.layout
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=5001)
    # http_server = WSGIServer(('0.0.0.0', 5000), server)
    # http_server.serve_forever()