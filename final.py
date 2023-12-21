from shapely.geometry import *
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
from tkinter import *
from tkinter import filedialog, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Create the main Tkinter window
root = Tk()
root.title("Kitik_Kitik")

file_path = ''

# Open Shapefile button
open_button = Button(root, text='Open Csvfile',
                     command=lambda: open_shapefile())
open_button.grid(row=1, column=0, padx=10, pady=10, sticky=W)

# Display selected file path
file_label = Label(root, text='No file selected')
file_label.grid(row=151,  columnspan=2, sticky=W)

# Label and Combobox for selecting Remarks
Label(root, text='Select to digitize').grid(
    row=3, column=0, padx=10, pady=5, sticky=W)
off4 = StringVar()
choose4 = ttk.Combobox(root, width=30, textvariable=off4)
choose4.grid(row=4, column=0, padx=10, pady=5, sticky=W)

# check button
Label(root, text='Join the corners:').grid(
    row=1, column=0, padx=20, pady=5, sticky=E)
v = IntVar()

check = Checkbutton(root, text='Yes/No', variable=v)
check.grid(row=2, column=0, padx=20,  sticky=E)

# offset
Label(root, text='Select the points:').grid(
    row=1, column=1, padx=10, pady=5, sticky=W)

c = IntVar()
check2 = Checkbutton(root, text='Yes/No', variable=c)
check2.grid(row=2, column=1, sticky=W)

off1 = IntVar()
choose1 = ttk.Combobox(root, width=30, textvariable=off1)
choose1.grid(row=3, column=1, padx=10, pady=5, sticky=W)

off2 = IntVar()
choose2 = ttk.Combobox(root, width=30, textvariable=off2)
choose2.grid(row=4, column=1, padx=10, pady=5, sticky=W)


# Radio buttons
n = IntVar()
polygon = Radiobutton(root, text='Polygon', variable=n, value=1)
polygon.grid(row=5, column=0, sticky=W)

line = Radiobutton(root, text='Line', variable=n, value=2)
line.grid(row=6, column=0, sticky=W)

linear_ring = Radiobutton(root, text='Linear Ring', variable=n, value=3)
linear_ring.grid(row=7, column=0, sticky=W)

# export
export = Button(root, text='Export',command =lambda : export())
export.grid(row=7,column=1,sticky=W)

compute = Button(root, text='Compute', command=lambda: get_layer(
    choose4.get(), n.get(), v.get(),  choose1.get(), choose2.get(), c.get() ))
compute.grid(row=20, padx=10, sticky=W)


def export():
    global merged_gdf

    file_path = filedialog.asksaveasfilename(
    defaultextension=".geojson",
    filetypes=[("GeoJSON", "*.geojson")],
    title="Save GeoJSON"
    )
    if file_path:
        merged_gdf.to_file(file_path, driver="GeoJSON")



def get_layer(rem, n, v, choose1, choose2, c ):

    gdf = gpd.read_file(file_path)
    gdf = gpd.GeoDataFrame(gdf, geometry=gpd.points_from_xy(gdf['X'], gdf['Y']), crs='EPSG:3857')
    gdf = gdf[gdf['geometry'].notna()]
    # temp = gpd.GeoDataFrame(geometry=[], crs=gdf.crs)

    sub1 = gdf[gdf['Remarks'] == rem]


    points = sub1['geometry'].tolist()
    print(c, choose1, choose2)

    if len(points) > 2:

        new_gdf = gpd.GeoDataFrame(geometry=[], crs=gdf.crs)
        if v == 1 and n == 1:
            sub1['X'] = sub1.geometry.x
            sub1['Y'] = sub1.geometry.y
            x = sub1['X'].tolist()
            y = sub1['Y'].tolist()
            for i in range(len(x)-2):
                x.append(x[i+2]+x[i]-x[i+1])
                y.append(y[i+2]+y[i]-y[i+1])
            new_gdf = gpd.GeoDataFrame(
                geometry=[Polygon(zip(x, y))], crs=gdf.crs)
            new_gdf['Remarks'] = rem

        elif c == 1 and n == 2:

            p1 = gdf[gdf['pkuid'] == choose1]['geometry']
            p2 = gdf[gdf['pkuid'] == choose2]['geometry']

            x1 = p1.geometry.x[p1.index[0]]
            y1 = p1.geometry.y[p1.index[0]]
            x2 = p2.geometry.x[p2.index[0]]
            y2 = p2.geometry.y[p2.index[0]]
            sub1['X'] = sub1.geometry.x
            sub1['Y'] = sub1.geometry.y
            dx = x2-x1
            dy = y2-y1
            sub1['XX'] = sub1['X']+dx
            sub1['YY'] = sub1['Y']+dy
            sub1['geometry'] = sub1.apply(
                lambda row: Point(row['XX'], row['YY']), axis=1)
            line = LineString(sub1['geometry'].tolist())
            new_gdf = gpd.GeoDataFrame(geometry=[line], crs=gdf.crs)
            new_gdf['Remarks'] = rem+'off'

        elif n == 2:
            new_gdf = gpd.GeoDataFrame(
                geometry=[LineString(points)], crs=new_gdf.crs)
            new_gdf['Remarks'] = rem

        elif n == 3:
            new_gdf = gpd.GeoDataFrame(
                geometry=[LinearRing(points)], crs=new_gdf.crs)
            new_gdf['Remarks'] = rem

        elif n == 1:
            new_gdf = gpd.GeoDataFrame(
                geometry=[Polygon(points)], crs=new_gdf.crs)
            new_gdf['Remarks'] = rem

        merge_layers(new_gdf)


merged_gdf = gpd.GeoDataFrame(geometry=[], crs=None)


def merge_layers(gdf):
    global merged_gdf

    merged_gdf = pd.concat([merged_gdf, gdf], ignore_index=True)

    merged_gdf = merged_gdf[~merged_gdf['Remarks'].duplicated(keep='last')]

    print(merged_gdf)

    fig, ax = plt.subplots()
    merged_gdf.plot(ax=ax)

    plot_canvas(fig, ax, 1, merged_gdf)


def open_shapefile():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        file_label.config(text=file_path)
        plot_shapefile(file_path)


def plot_shapefile(file_path):
    gdf = gpd.read_file(file_path)
    gdf = gpd.GeoDataFrame(gdf, geometry=gpd.points_from_xy(gdf['X'], gdf['Y']), crs='EPSG:3857')

    # Update Combobox values with unique remarks
    choose4['values'] = tuple(gdf['Remarks'].unique())
    choose1['values'] = tuple(gdf['pkuid'].unique())
    choose2['values'] = tuple(gdf['pkuid'].unique())

    fig, ax = plt.subplots()

    plot_canvas(fig, ax, 0, gdf)


def plot_canvas(fig, ax, n, gdf):

    for rem in gdf['Remarks'].unique():
        gdf[gdf['Remarks'] == rem].plot(ax=ax, label=rem)

    ax.legend(loc='upper right')
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=150, column=n)

    plt.close(fig)


# Run the Tkinter event loop
root.mainloop()
