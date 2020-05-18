import shapefile as shp  # Package to handle shapefiles and shapes
import pandas as pd
from pyproj import CRS, Transformer  # Package to convert coordinates from WGS84 to UTM33N

def shapefile_to_dataframe(filepath) -> pd.DataFrame:
    """Define and convert points from QGIS project showing points of interest"""
    wgs84 = CRS.from_epsg(4326)  # 4326 is number code for WGS84 type coordinates
    utm33n = CRS.from_epsg(25833)  # 25833 is number code for UTM33N type coordinates
    transformer = Transformer.from_crs(wgs84, utm33n)  # Creates a transformer class with method (i.e. function) used to convert point coordinates from WGS84 to UTM33N.

    localities = shp.Reader(filepath, encoding='windows-1252')  # Localities are defined from the shape points (coordinates) in the chosen file

    locality_points = localities.shapes()  # Locality points are refered from the locality shape above

    columns = ["Easting", "Northing"]  # Defines a list of columns

    locality_fields = localities.fields  # Defines locality fields refered to in the localities shapefile
    for field in locality_fields:  # creates for loop in locality fields
        field_name = field[0]  # picks out column names (i.e. field names) from first field (0)
        if field_name == "DeletionFlag":  # if the field name is DeletionFlag, skip it
            continue  # if field name is DeletationFlag it is skipped and the loop continues
        columns.append(field_name)  # adds column names to the list of columns from above

    dataframe_attributes_coordiantes = pd.DataFrame(columns=columns)  # Creates a table (e.g. those in Excel)

    # Creates for loop to enumerate (give numbers) to rows in dataframe from shapefile
    for index, point in enumerate(locality_points):
        x_coordinate, y_coordinate = point.points[0]  # Extracts the first (and only) point coordinate set (because its a point and not a 2 or 3 dimentional object)
        if y_coordinate > 90:  # Checks if coordinates are in correct units (we want utm33n not lat-long), if the  y_coordinate is over 90, it must be utm already and doesn't have to be transformed
            easting, northing = x_coordinate, y_coordinate
        else:
            easting, northing = transformer.transform(y_coordinate, x_coordinate)  # Uses transformer class to convert coordinates
        attributes = localities.record(index)  # Extracts record with index from 0...n and defines it in variable called attributes
        data = [easting, northing, *attributes]  # Defines data to lie in dataframe in any row (from 0...n). *takes all items in attributes list and adds it to newly created data list
        dataframe_attributes_coordiantes.loc[index] = data  # dataframe matches index number with data


    return dataframe_attributes_coordiantes  #

def combine_and_sort(list_of_dataframes):
    dataframe_all_points = pd.concat(list_of_dataframes, ignore_index=True, sort=False)
    sorted_dataframe_columns = dataframe_all_points[["Index name", "Location", "Author", "Year", "Asp.Fm", "Batt.Fm", "Frys.Fm", "Data type", "Reference", "Easting", "Northing"]]
    return sorted_dataframe_columns