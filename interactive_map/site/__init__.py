import dash
import dash_table
import dash_auth
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import json
import plotly.graph_objects as go # or plotly.express as px
import os
import time
from flask import request
import geopandas as gpd

def get_time_of_latest_commit():
    filename = ".git/index"
    modified_time = time.gmtime(os.path.getmtime(filename))
    output_string = "Updated on: {}/{}/{}".format(modified_time.tm_mday, modified_time.tm_mon, modified_time.tm_year)
    return output_string


VALID_USERNAME_PASSWORD_PAIRS = {"guest": "DoUlikeRockz1"}

def plot_points(dataframe_all_points):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

    data_yes_no_Asp = []
    for criterion in ["yes", "no"]:
        data_filling_criterion = dataframe_all_points[dataframe_all_points["Asp.Fm"] == criterion]
        data_dictionary = dict(
            x=data_filling_criterion["Easting"],
            y=data_filling_criterion["Northing"],
            text=data_filling_criterion["Author"] + " " + "(" + data_filling_criterion["Year"].astype(str) + ")",
            mode='markers',
            name="Data point includes Asp.Fm" if criterion == "yes" else "Data point excludes Asp.Fm",
            opacity=0.7,
            customdata=data_filling_criterion.index,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
        )
        data_yes_no_Asp.append(data_dictionary)

    

    bg_map = go.Figure() # or any Plotly Express function
    #bg_map.add_trace(
    #    go.Scatter(x=[0, 0.5, 1, 2, 2.2], y=[1.23, 2.5, 0.42, 3, 1])
    #)
    bg_map.add_layout_image(
        dict(
            source="/static/Dash_background_map_noFM.jpg",
            xref="x",
            yref="y",
            x=484914.000,
            y=8687643.227,
            sizex=71309.39099999995,
            sizey=100851.85400000028,
            sizing="stretch",
            opacity=0.7,
            layer="below"
           )
    )

    aspelintoppen = gpd.read_file("Shapes for interactive map/Aspelintoppen.shp")
    x_cords = []
    y_cords = []
    for geometry in aspelintoppen.geometry:

        x_cords += geometry.exterior.xy[0].tolist() +[None]
        y_cords += geometry.exterior.xy[1].tolist() +[None]

    bg_map.add_trace(go.Scatter(
        x=x_cords,
        y=y_cords,
        fill="toself",
        fillcolor="rgb(252, 217, 88)",
        opacity=0.75,
        line=dict(color="rgba(0, 0, 0, 0)"),
        name="Aspelintoppen Formation"
    ))

    helisurvey = gpd.read_file("Shapes for interactive map/own_localities.shp")
    x_cords = []
    y_cords = []
    for geometry in helisurvey.geometry:

        x_cords += geometry.exterior.xy[0].tolist() +[None]
        y_cords += geometry.exterior.xy[1].tolist() +[None]

    bg_map.add_trace(go.Scatter(
        x=x_cords,
        y=y_cords,
        fill="toself",
        fillcolor="rgb(227, 113, 144)",
        opacity=0.75,
        line=dict(color="rgba(227, 113, 144, 100)"),
        name="Aerial images (2020)"
    ))


    for data_dictionary in data_yes_no_Asp:  # Plots data from data_dictionary on map
        bg_map.add_trace(data_dictionary)

    bg_map.layout["yaxis"] = {
                "scaleanchor": "x",
                "scaleratio": 1
            }




    app.layout = html.Div(children=[
        html.H1(children="Upper Van Mijenfjorden Group interactive map"),
        html.H4(children="Created as part of master thesis project by Anna Bøgh Mannerfelt"),
        html.Div(children=get_time_of_latest_commit()),

        html.Div(children='''This interactive map was created by the author, Anna Bøgh (MSc student at UiB and UNIS).'''),

        html.Div(children='''All previously collected data was compiled and extracted from articles, master theses and PhD theses by the author.'''),

        html.Div(children='''Data with reference "Bøgh..." was collected by the author.'''),

        dcc.Graph(figure=bg_map, id='Aspelintoppen Fm data', style={"width": "50%", "height": "1000px", "float": "left"}),
        

        html.Div(id="hidden_div_for_redirect_callback"),

        html.Div([
            dcc.Markdown("""
                **Selection Data**

                To view and download data, choose the lasso or rectangle tool in the graph's menu
                bar and then mark one or several points in the map.
                
                To select more points without letting go of the first selection, hold down Shift button.

                To view log data and reference, **click on a row**. To view log image in greater detail and to download, click on the image. The image will load in another tab in your browser.
                
                (Empty Index name fields indicate no available log image. Instead, please see article reference to learn more.) 
            """),
            dash_table.DataTable(
                id='selected_data',
                columns=[{"name": i, "id": i} for i in dataframe_all_points.columns],
                data=dataframe_all_points.to_dict("records"),
                hidden_columns=["Reference"],
                css=[{"selector": ".show-hide", "rule": "display: none"}]

            ),
        ], 
        style={"width": "50%", "float": "right"}
        ),
        html.P(children="Reference: Select data in table above", id="reference_paragraph"),
        html.A(id="reference_link", target="_blank"),
        html.A(children=html.Img(id="log_image", style={"height": "600px", "float": "right", "max-width": "40%", "object-fit": "scale-down"}), target="_blank", id="image_link"),
        
        html.Div([
            html.A(rel="license", href='http://creativecommons.org/licenses/by-nc-sa/4.0/', children=[
                html.Img(alt='Creative Commons License', style={'border-width':'0'}, src="/static/88x31.png")
            ]),
            html.Br(),
            html.P("This work is licensed under a ", style={"display":"inline"}),
            html.A(rel="license", href='http://creativecommons.org/licenses/by-nc-sa/4.0/', children="Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License")
        ], style={"bottom": "0%", "position":"fixed"})
        ])



    @app.callback(
        Output('selected_data', 'data'),
        [Input('Aspelintoppen Fm data', 'selectedData')])
    def display_selected_data(selectedData):
        selected_data = json.dumps(selectedData, indent=2)
        # points = selected_data["points"]

        if selectedData is None:
            return pd.DataFrame(columns=dataframe_all_points.columns).to_dict('records')
        # To do: change point index to something we know what is!
        indices = [point["customdata"] for point in selectedData["points"]]
        dataframe_all_points_copy = dataframe_all_points.copy()
        dataframe_all_points_copy[["Easting", "Northing"]] = dataframe_all_points_copy[["Easting", "Northing"]].astype(int)

        output = dataframe_all_points_copy.iloc[indices].to_dict('records')
        return output


    @app.callback(Output("selected_data", "selected_cells"), [Input('Aspelintoppen Fm data', 'selectedData')])
    def reset_datatable_selection(selected_data):
        return []

    @app.callback([Output("log_image", "src"), Output("image_link", "href"), Output("reference_paragraph", "children"), Output("reference_link", "children"), Output("reference_link", "href")],
        [Input("selected_data", "selected_cells"), Input('selected_data', 'data')]  # When this is run two outputs are created: log image and image link
    )
    def open_image_on_click(selected_cells, selectedData):
        results = {
            "log_image": None,
            "image_link": None,
            "reference_paragraph": "Reference: Select data in table above",
            "reference_link_text": None,
            "reference_link_link": None
        }
        #print(selected_cells)
        #if selected_cells is None:
        #    return list(results.values())

        try:
            column_id = selected_cells[0]["column_id"]
        except IndexError:
            return list(results.values())
        row = selected_cells[0]["row"]
        selected_row = selectedData[row]

        reference = selected_row["Reference"]
        index_name = selected_row["Index name"]
      
 
        if reference is None or reference.strip() == "":
            results["reference_paragraph"] = "Reference: Reference not available, contact author for further details."
        else:
            results["reference_paragraph"] = "Reference: "
            results["reference_link_text"] = reference
            results["reference_link_link"] = reference

        if isinstance(index_name, str) and (index_name is not None and index_name.strip() != ""):
            link = "/static/Logs/{}.jpg".format(index_name)
            results["log_image"] = link
            results["image_link"] = link
        else:
            results["reference_paragraph"] = results["reference_paragraph"].replace("Reference: ", "Reference: Image not available. ")

    
        return list(results.values())
        

    app.run_server(debug=True, port=1337, host="0.0.0.0")

# TODO: 
# 1) 
# 2) Ændre styling på Index name og Reference kolonnerne så det er tydeligt, at det er der, man skal klikke
# 3) Gør så hele rækken bliver selected og ikke kun enkelte bokse
# 4) Lav knap for download af tabel i csv
# 5) 
# 6) 
# 7) 
# 8) 
# 9) 
