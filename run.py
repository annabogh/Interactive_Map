import matplotlib.pyplot as plt  # Package to plot maps and figures
import shapefile as shp  # Package to handle shapefiles and shapes
from pyproj import CRS, Transformer  # Package to convert coordinates from WGS84 to UTM33N
import pandas as pd  # Package to handle data tables with attributes and column names
import time
import interactive_map as im
from interactive_map import data, interaction, plotting, site
from interactive_map.site import plot_points

FIGURE = plt.figure()


plotting.show_map()
dataframe_previously_studied = data.shapefile_to_dataframe(filepath="../Shapes/Previously_studied.shp")  # Locality point plot is run
dataframe_clifton = data.shapefile_to_dataframe(filepath="../Shapes/Clifton_locations_and_cores.shp")
dataframe_all_points = data.combine_and_sort([dataframe_previously_studied, dataframe_clifton])

plotting.show_points(dataframe_all_points)

interaction.add_button_press_event(FIGURE, dataframe_all_points)

plot_points(dataframe_all_points)

#plotting.plot_table(dataframe_all_points)
#plt.show()  # Locality points are plotted on map