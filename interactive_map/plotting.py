import matplotlib.pyplot as plt  # Used for plotting data in tables, figures...
import plotly.graph_objects as go  # Used for plotting data in table (on server??)

def show_map():
    """Import a hillshade and plot it."""
    image = plt.imread("../Rasters/whole_svalbard_hillshade_CTB_cropped.tif")  # Define image from a specified tif-file

    # Coordinates are read from project in QGIS for min and max values. Extent is defined from these values.
    xmin = 483130
    ymin = 8582110
    xmax = 554830
    ymax = 8701170

    extent = (xmin, xmax, ymin, ymax)

    # Show image with defined extents and a chosen color scheme
    plt.imshow(image, cmap="Greys_r", extent=extent)

def show_points(dataframe_attributes_coordinates):
    """This plots the data in the dataframe and map."""
    for i, row in dataframe_attributes_coordinates.iterrows():
        plt.scatter(row["Easting"], row["Northing"])  # Points are plottet in map
        plt.annotate(row["Author"], (row["Easting"], row["Northing"]))  # Annotates points with corresponding author name (could be anything else, like location name, etc.)


def find_nearest_point(dataframe_attributes_coordinates, x_coordinate, y_coordinate):
    """Finds nearest point (within given distance limit) and returns data on point."""
    dataframe_attributes_coordinates_copy = dataframe_attributes_coordinates.copy()  # Copies dataframe_attributes_coordinates so as to not add a distance column
    dataframe_attributes_coordinates_copy["dx"] = dataframe_attributes_coordinates_copy["Easting"] - x_coordinate  # Takes x-coodinate for the chosen point on map and subtracts it from the "Easting" column
    dataframe_attributes_coordinates_copy["dy"] = dataframe_attributes_coordinates_copy["Northing"] - y_coordinate  # Takes y-coodinate for the chosen point on map and subtracts it from the "Northing" column
    dataframe_attributes_coordinates_copy["distance"] = (dataframe_attributes_coordinates_copy["dx"]**2 + dataframe_attributes_coordinates_copy["dy"]**2)**0.5  # Uses Pythagoras trigonometry to find distance using chosen point (x, y) againts the (x, y) from all points in dataframe

    if dataframe_attributes_coordinates_copy["distance"].min() > 30000:
        return  # Returns nothing if distance is above chosen distance limit

    return dataframe_attributes_coordinates_copy.sort_values("distance").iloc[0]  # Returns Closest dataframe point to chosen point on map


def plot_table(dataframe_attributes_coordinates):
    """Plots a dataframe using plotly, method copied from internet. Plots dataframe table on private server in internet browser."""
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(dataframe_attributes_coordinates.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=dataframe_attributes_coordinates.values.T,
                fill_color='lavender',
                align='left'))
        ])

    fig.show()

