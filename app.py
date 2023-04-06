import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import port_services_scrape as pss
import pandas as pd
from dash import Dash, dcc, html, dash_table
from selenium import webdriver
from time import sleep
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

pd.options.display.width = None
pd.options.display.max_columns = None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)
#options = webdriver.EdgeOptions()
options = Options()
options.add_argument("headless")
options.add_experimental_option('excludeSwitches', ['enable-logging'])


url = 'http://webaccess.gaports.com/express/secure/Today.jsp?Facility=GCT'
user_id = 'inorberg'
password = 'ni2396'

#components
app = Dash(__name__,
            title="Port Services: GCT Scraper",
            external_stylesheets=[dbc.themes.SPACELAB]
           )
app.enable_dev_tools(debug=True, dev_tools_hot_reload=False)

app.layout = dbc.Container([
    html.Br(),

    html.Div(dcc.Markdown(children="# Port Services Drayage Report Scrape")),

    html.Hr(),

    html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select File')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                #'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=False
        ),

        html.Br(),

        dcc.Loading(id='loading', children=[
            html.Div(id='output-data-upload')],
            type='circle',
            fullscreen=True
        )
    ]),

    html.Br(),

    html.Div(id='upload_text'),

    html.Br(),

])

@app.callback(
    [Output("upload_text", "children"),
    Output("output-data-upload", "children")],
    [Input("upload-data", "contents"),
     Input("upload-data", "filename")
     ], prevent_initial_call=True
)
def update_table(contents, filename):
    table = html.Div()
    try:
        all_containers = pss.parse_data(contents, filename)
    except Exception as e:
        upload_text = "Upload Failed"
        table = html.H5(
                style={"color": "#a64452"},
                children=["The File Was Unable to be Uploaded. Did You Upload the Correct File?"]
        )

    browser = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
    #browser.maximize_window()

    browser.get(url)

    browser = pss.login(browser, user_id, password)

    try:
        visible_containers = pss.get_visible_cont(browser, all_containers)

        visible_containers = visible_containers.drop(columns=['Status'])

        all_containers = pss.get_container_history(browser, all_containers)
        all_containers = pd.merge(left=all_containers, right=visible_containers, how='left', left_on='Container',
                                  right_on='EQUIP ID')
        all_containers = all_containers[['Container', 'OTW ETA', 'Status', 'Transload Received', 'LOCATION',
                                        'available_date', 'full_out_date', 'empty_in_date', 'is_visible']]
        all_containers = all_containers.rename(columns={'LOCATION':'Location', 'available_date':'Available Date',
                                                        'full_out_date':'Full Out Date', 'empty_in_date':'Empty In Date',
                                                        'is_visible':'Is Visible'})

        #all_containers = pss.new_status(all_containers)

        print('Finished')
        sleep(2)

        browser.quit()

        if not all_containers.empty:
            upload_text = 'Uploaded Successfully'
        else:
            upload_text = 'You Uploaded A Blank File'

        print(all_containers.head())

        table = html.Div(
            [
                html.H5('Containers Scraped'),
                dash_table.DataTable(
                    data=all_containers.to_dict("rows"),
                    columns=[{"name": i, "id": i} for i in all_containers.columns],
                    export_format='xlsx',
                    export_headers='display',
                    style_as_list_view=True,
                    style_header={
                        'backgroundColor': 'black',
                        'color': 'white',
                        'fontWeight': 'bold'
                    },
                    style_cell={'textAlign': 'center'}
                )
            ]
        )
    except Exception as e:
        upload_text = "Upload Failed"
        table = html.H5(
            style={"color": "#a64452"},
            children=["The File Was Unable to be Uploaded. Did You Upload the Correct File?"]
        )

    return upload_text, table




#run app
if __name__ == '__main__':
    app.run_server(debug=True, port=3050)
