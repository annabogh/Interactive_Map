import time
import interactive_map as im
import subprocess

time_of_last_click = 0

def add_button_press_event(figure, dataframe_all_points):
    # Makes double clicks possible to locate the nearest point on map, gives back information (attributes) on that specific point
    def onclick(event):
        global time_of_last_click
        time_limit = 1  # max. 1 second between clicks to make it a double click

        if (time.time() - time_of_last_click) > time_limit:
            time_of_last_click = time.time()
            return

        easting, northing = event.xdata, event.ydata
        nearest = im.plotting.find_nearest_point(dataframe_all_points, easting, northing)
        open_data_image("../" + nearest["Data image"])  # remember, these are relative paths, not absolute
        print(nearest)
        time_of_last_click = time.time()
    figure.canvas.mpl_connect('button_press_event', onclick)

def open_data_image(filepath_to_data_image):
    print(filepath_to_data_image)
    windows_file_path = filepath_to_data_image.replace("/", "\\")
    print(windows_file_path)
    subprocess.run(["explorer", windows_file_path])
