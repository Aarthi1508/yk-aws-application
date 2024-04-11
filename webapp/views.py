from django.shortcuts import render
from django.http import JsonResponse

import datetime
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from .solarposition import *
from matplotlib import dates
from .shadowingfunction_wallheight_13 import shadowingfunction_wallheight_13
import pymongo
import pytz
from pathlib import Path
import os
import rasterio
import numpy as np
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()



BASE_DIR = Path(__file__).resolve().parent.parent


def read_geotiff(input_file):
    with rasterio.open(input_file, 'r') as src:
        # Read metadata
        width = src.width
        height = src.height
        count = src.count  # Number of bands
        crs = src.crs.to_epsg()  # EPSG code of the coordinate reference system
        transform = src.transform  # Affine transformation parameters

        # Read each band
        data_arrays = [src.read(band_index + 1) for band_index in range(count)]
        data_names = [src.descriptions[band_index] for band_index in range(count)]

    return {
        'width': width,
        'height': height,
        'count': count,
        'crs': crs,
        'transform': transform,
        'data_arrays': data_arrays,
        'data_names': data_names
    }


input_file = os.path.join(BASE_DIR, 'webapp', 'data', 'sample_400_400_sampled.tif') # Replace with the path to your GeoTIFF file

# Read GeoTIFF file
geotiff_data = read_geotiff(input_file)

# Access data
width = geotiff_data['width']
height = geotiff_data['height']
count = geotiff_data['count']
crs = geotiff_data['crs']
transform = geotiff_data['transform']
data_arrays = geotiff_data['data_arrays']
data_names = geotiff_data['data_names']

# Print information
print(f"Width: {width}, Height: {height}, Bands: {count}")
print(f"Coordinate Reference System (CRS): EPSG:{crs}")
print(f"Affine Transformation: {transform}")

# Accessing individual bands
for band_index, (data_array, data_name) in enumerate(zip(data_arrays, data_names)):
    print(f"Band {band_index + 1} - ({data_name}):")
    print(data_array.shape)

output_latitude_array = data_arrays[0]
output_longitude_array = data_arrays[1]
output_sm_array = data_arrays[2]
output_dem_array = data_arrays[3]

dsm = output_dem_array

# Replace NaN values with zeros
dsm = np.nan_to_num(dsm, nan=0)

print(dsm.shape)

def shadow_analysis(request):
    # TODO implement

    print("Starting the shadow analysis!")
    
    # data_path = os.path.join(BASE_DIR, 'webapp', 'data', 'dsm_local_array.npy')

    # # Save the array to a file
    # dsm = np.load(data_path)

    # # Replace NaN values with zeros
    # dsm = np.nan_to_num(dsm, nan=0)

    # # print(dsm)

    # # f, ax = plt.subplots(dpi=500)

    # # plt.imshow(dsm, cmap='viridis')

    # # plt.show()

    lon = -95.30052
    lat = 29.73463

    utc_offset= -6
    

    if request.method == 'POST':
        input_timestamp = request.POST.get('timestampInput')
        if input_timestamp:
            # If input timestamp is provided, parse and format it
            print("input_timestamp is", input_timestamp)

            try:
                input_datetime = datetime.datetime.strptime(input_timestamp, '%Y-%m-%d %H:%M:%S')
                formatted_timestamp = input_datetime.strftime('%Y-%m-%d %H:%M:%S')
                timestamps = [formatted_timestamp]
            except ValueError:
                # Handle invalid input timestamp
                # Return a JSON response with an error message
                return JsonResponse({"error": "Invalid input timestamp format"})
        else:
            # If no input timestamp is provided, use the current timestamp
            print("no timestamp so taking default ts")
            cdt_timezone = pytz.timezone('America/Chicago')
            current_datetime = datetime.datetime.now(cdt_timezone)
            formatted_timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            timestamps = [formatted_timestamp]
    else:
        # Default behavior: use current timestamp
        print("no timestamp so taking default ts")
        cdt_timezone = pytz.timezone('America/Chicago')
        current_datetime = datetime.datetime.now(cdt_timezone)
        formatted_timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
        timestamps = [formatted_timestamp]

    # Create a DataFrame using the timestamps as a column
    df = pd.DataFrame({'TimeStamp': timestamps})
    

    # Print the DataFrame
    df.head()

    df_solar = df.copy()

    df_solar["TimeStamp"] = df_solar["TimeStamp"].apply(pd.to_datetime)
    df_solar.set_index("TimeStamp", inplace = True)
    df_solar.head()

    df_solar_data = df.copy()

    # UTC time
    df_solar_data['TimeStamp'] = pd.DatetimeIndex(df_solar_data['TimeStamp']) - pd.DateOffset(hours=utc_offset)

    # To_Datetime
    df_solar_data["TimeStamp"] = df_solar_data["TimeStamp"].apply(pd.to_datetime)
    df_solar_data.set_index("TimeStamp", inplace = True)

    # Add time index
    df_solar_data["TimeStamp"] = df_solar_data.index

    df_solar_data.head()

    df_solar = get_solarposition(df_solar_data.index, lat, lon)

    df_solar['TimeStamp'] = pd.DatetimeIndex(df_solar.index) + pd.DateOffset(hours=utc_offset)

    df_solar = df_solar[['TimeStamp', 'apparent_zenith', 'zenith', 'apparent_elevation', 'elevation',
                    'azimuth', 'equation_of_time']]

    # To_Datetime
    df_solar["TimeStamp"] = df_solar["TimeStamp"].apply(pd.to_datetime)
    df_solar.set_index("TimeStamp", inplace = True)

    df_solar.head()

    df_solar["TimeStamp"] = df_solar.index
    df_solar = df_solar[['TimeStamp', 'elevation', 'zenith', 'azimuth']]

    df_solar = df_solar.rename(columns={"elevation": "Elevation","azimuth": "Azimuth", "zenith": "Zenith"})

    df_solar.head()

    # plt.figure(figsize=(8, 6), dpi=500)

    # plt.plot(df_solar["TimeStamp"], df_solar['Elevation'], 's-r', label='Elevation', ms=3)
    # plt.plot(df_solar["TimeStamp"], df_solar['Zenith'], 's-b', label='Zenith', ms=3)

    # ax=plt.gca()

    # plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
    #                 mode="expand", borderaxespad=0, ncol=4)

    # plt.show()

    scale = 1 

    walls = np.zeros((dsm.shape[0], dsm.shape[1]))
    dirwalls = np.zeros((dsm.shape[0], dsm.shape[1]))

    i = 0  #defines the exact row column (index) for which you have to generate the shadow analysis


    altitude = df_solar['Elevation'][i]
    azimuth = df_solar['Azimuth'][i]

    hour = df_solar.index[i].hour
    minute = df_solar.index[i].minute

    sh, wallsh, wallsun, facesh, facesun = shadowingfunction_wallheight_13(dsm, azimuth, altitude, scale, walls, dirwalls * np.pi / 180.)

    # f, ax = plt.subplots(dpi=500)

    # plt.imshow(sh, cmap='viridis')

    # plt.title("%2s" % str(hour).zfill(2) + ":%2s"% str(minute).zfill(2), pad =10, fontsize=15, color="black", weight='bold' )
    # # plt.savefig('./result/hour%2s'% str(hour).zfill(2) + "minute%2s"% str(minute).zfill(2) + ".png", transparent=True)

    shadow_df=pd.DataFrame(sh)

    shadow_df.columns = [str(column) for column in shadow_df.columns]

    dataframe_dict = shadow_df.to_dict(orient="records")



    try: 
        client = pymongo.MongoClient(os.getenv('MONGODB_CLIENT_URL'))
        db = client[os.getenv('MONGODB_DATABASE')]
        collection = db[os.getenv('MONGODB_COLLECTION')]

        item_id = collection.count_documents({}) + 1
        
        
        cdt_timezone = pytz.timezone('America/Chicago')
        current_datetime = datetime.datetime.now(cdt_timezone)
        pushed_timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Include milliseconds


        data_to_insert = {
            "item_id": formatted_timestamp,
            "pushed_timestamp": pushed_timestamp,
            "shadow_matrix": str(dataframe_dict).replace("'", '"')
        }

        result = collection.insert_one(data_to_insert)
        return_msg = 'Data pushed to MongoDB!'

        print(result, "Record pushed into MongoDB")
        client.close()
    except Exception as e:
        print("Error pushing data to MongoDB : {} ".format(e))
        
        return_msg = 'Error when pushing data into MongoDB!'

        print("Error when pushing data into MongoDB!")

    data = {
        'statusCode': 200,
        'body': json.dumps(return_msg)
    }
    
    return JsonResponse(data)

def visualize_shadow_matrix(request):
    
    client = pymongo.MongoClient(os.getenv('MONGODB_CLIENT_URL'))
    db = client[os.getenv('MONGODB_DATABASE')]
    collection = db[os.getenv('MONGODB_COLLECTION')]

    # Sort the collection in descending order based on a timestamp field
    # For example, assuming the field name is "timestamp"
    latest_record_cursor = collection.find().sort("pushed_timestamp", -1).limit(1)
    
    result = {}
    
    # Iterate over the cursor object
    for latest_record in latest_record_cursor:
        # Print attributes of the latest record
        print("Attributes of the latest record:")
        for key, value in latest_record.items():
            result[key] = value
            
    shadow_matrix_str = result['shadow_matrix']
    shadow_matrix_lst = json.loads(shadow_matrix_str)    
    
    year = str((str(result['item_id'].split()[0])).split('-')[0])
    month = str((str(result['item_id'].split()[0])).split('-')[1])
    day = str((str(result['item_id'].split()[0])).split('-')[2])
    
    hour = str((str(result['item_id'].split()[1])).split(':')[0])
    minute = str((str(result['item_id'].split()[1])).split(':')[1])
    second = str((str(result['item_id'].split()[1])).split(':')[2])  
    
    
    data_path = os.path.join(BASE_DIR, 'webapp', 'static', 'results',
                         str(year) + '-' +
                         str(month).zfill(2) + '-' +
                         str(day).zfill(2) + '-' +
                         str(hour).zfill(2) + '-' +
                         str(minute).zfill(2) + '-' +
                         str(second).zfill(2) + '.png')
        
    
    # Initialize an empty list to store the values
    values_list = []

    # Iterate over each entry in the list
    for entry in shadow_matrix_lst:
        # Extract the values from the dictionary and append them to the values list
        values_list.append(list(entry.values()))

    # Convert the values list into a NumPy array
    shadow_matrix = np.array(values_list)

    # Print the shape of the array
    print("Shape of the shadow_matrix array:", shadow_matrix.shape)
    
    f, ax = plt.subplots(dpi=500)

    plt.imshow(shadow_matrix, cmap='viridis')
    plt.title(str(year) + "-%2s"% str(month).zfill(2) + "-%2s"% str(day).zfill(2) + " %2s" % str(hour).zfill(2) + ":%2s"% str(minute).zfill(2) + ":%2s"% str(second).zfill(2), pad =10, fontsize=10, color="black", weight='bold' )
    plt.savefig(data_path, transparent=True)
    
    print(data_path)
    # Pass the path to the image file to the template context
    context = {
        'image_path': '/'.join(list(data_path.split('/'))[-2::])
    }

    print('/'.join(list(data_path.split('/'))[-2::]))
    # Render the template with the context
    return render(request, 'visualize.html', context)


def superimpose_shadow_matrix(request):
    
    client = pymongo.MongoClient(os.getenv('MONGODB_CLIENT_URL'))
    db = client[os.getenv('MONGODB_DATABASE')]
    collection = db[os.getenv('MONGODB_COLLECTION')]

    # Sort the collection in descending order based on a timestamp field
    # For example, assuming the field name is "timestamp"
    latest_record_cursor = collection.find().sort("pushed_timestamp", -1).limit(1)
    
    result = {}
    
    # Iterate over the cursor object
    for latest_record in latest_record_cursor:
        # Print attributes of the latest record
        print("Attributes of the latest record:")
        for key, value in latest_record.items():
            result[key] = value
            
    shadow_matrix_str = result['shadow_matrix']
    shadow_matrix_lst = json.loads(shadow_matrix_str)
    
    print(result['item_id'], len(shadow_matrix_lst), len(shadow_matrix_lst[0].items()))     
    
    year = str((str(result['item_id'].split()[0])).split('-')[0])
    month = str((str(result['item_id'].split()[0])).split('-')[1])
    day = str((str(result['item_id'].split()[0])).split('-')[2])
    
    hour = str((str(result['item_id'].split()[1])).split(':')[0])
    minute = str((str(result['item_id'].split()[1])).split(':')[1])
    second = str((str(result['item_id'].split()[1])).split(':')[2])  
    
        
    # print(shadow_matrix_lst[0], shadow_matrix_lst[1])
    
    
    # Initialize an empty list to store the values
    values_list = []

    # Iterate over each entry in the list
    for entry in shadow_matrix_lst:
        # Extract the values from the dictionary and append them to the values list
        values_list.append(list(entry.values()))

    # Convert the values list into a NumPy array
    shadow_matrix = np.array(values_list)
    
    # Flatten the arrays
    sh_values = shadow_matrix.flatten()
    latitude_values = output_latitude_array.flatten()
    longitude_values = output_longitude_array.flatten()
    sm_values = output_sm_array.flatten()

    # Create a list to store the heatmap coordinates
    heatmap_coordinates = []

    # Iterate over each value in the flattened arrays
    for sh_item, lat, lon, sm_item in zip(sh_values, latitude_values, longitude_values, sm_values):
        # Check if sm is equal to 6
        # if sm_item == 6:
            # Append the coordinate as a tuple (latitude, longitude, value) to the list
        heatmap_coordinates.append((lat, lon, sh_item, sm_item))


    elevation_map_trace = go.Scattermapbox(
        mode="markers",
        lat=[coord[0] for coord in heatmap_coordinates],  # Extract latitudes
        lon=[coord[1] for coord in heatmap_coordinates],  # Extract longitudes
        marker=dict(
            size=5,  # Adjust marker size as needed
            color=sh_values,  # Use the sh values for color
            # color=[coord[2] for coord in heatmap_coordinates],  # Use the dem values for color
            colorscale='viridis',  # Use viridis colormap
            cmin=np.min(sh_values),  # Set minimum value for color scale
            cmax=np.max(sh_values),  # Set maximum value for color scale
        )
    )

    # Create the figure with 3D Mapbox layout
    fig = go.Figure(data=elevation_map_trace)

    # Update the layout to use Mapbox in 3D
    fig.update_layout(
        mapbox=dict(
            accesstoken=os.getenv('MAPBOX_ACCESS_TOKEN'),  # Replace with your Mapbox access token
            # style="mapbox://styles/mapbox/streets-v12",  # Specify the Mapbox style URL
            style=os.getenv('MAPBOX_3D_STYLE'),  # Specify the Mapbox style URL
            zoom=16,
            center={"lat": np.mean(latitude_values), "lon": np.mean(longitude_values)},
        ),
        scene=dict(
            aspectmode="data",  # Set aspectmode to "data" for equal scaling in 3D
        )
    )
    
    # data_path = os.path.join(BASE_DIR, 'webapp', 'templates', 'hour-%2s'% str(hour).zfill(2) + "-minute-%2s"% str(minute).zfill(2) + ".html")
    
    
    data_path = os.path.join(BASE_DIR, 'webapp', 'templates',
                         str(year) + '-' +
                         str(month).zfill(2) + '-' +
                         str(day).zfill(2) + '-' +
                         str(hour).zfill(2) + '-' +
                         str(minute).zfill(2) + '-' +
                         str(second).zfill(2) + '.html')

    # Construct the timestamp string in the required format
    timestamp_heading = f"Timestamp: {year}-{month.zfill(2)}-{day.zfill(2)} {hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"

    fig.write_html(data_path)
    
    
    
    
    # Concatenate header HTML with the generated content
    header_html = """
    {% load static %}
    
    <link rel="stylesheet" type="text/css" href="{% static 'css/styles.css' %}">

    <header>
        <div class="header-content">
            <img src="{% static 'images/tamu-icon.png' %}" alt="Icon Image" width="30" height="30">
            <div>
                <div>Texas A&M University</div>
                <div>Department of Construction Science</div>
            </div>
            <a href="https://www.hamresearchgroup.com/" class="research-group">HAM Research Group @ TAMU</a>
        </div>
    </header>
    <div style="text-align: center;">
        <button onclick="window.location.href='{% url 'generate-shadow-matrix' %}'" class="button">Generate shadow matrix again</button>
    </div>
    """
    
    # Concatenate the timestamp with the header_html
    header_html_with_timestamp = f"{header_html}\n<h3 style='text-align: center;'>{timestamp_heading}</h3>\n"

    # # Replace {timestamp} with the actual timestamp value before using the header_html
    # header_html_with_timestamp = header_html.format(timestamp=timestamp_heading)
        
    # Write the concatenated HTML to the file
    with open(data_path, 'w') as file:
        file.write(header_html_with_timestamp)
        fig.write_html(file)
    
    return render(request, data_path)


def generate_shadow_matrix(request):
    
    print("output_latitude_array", output_latitude_array)
    print("output_longitude_array", output_longitude_array)

    # return render(request, 'generate_shadow_matrix.html', {
    #         'latitude_array': output_latitude_array,
    #         'longitude_array': output_longitude_array
    #         })
    
    
    latitude_list = output_latitude_array.tolist()
    longitude_list = output_longitude_array.tolist()

    # Calculate the center coordinates
    center_lat = np.mean(latitude_list)
    center_lon = np.mean(longitude_list)

    # Pass necessary parameters to the HTML template
    return render(request, 'generate_shadow_matrix.html', {
        'mapbox_access_token': os.getenv('MAPBOX_ACCESS_TOKEN'),
        'MAPBOX_3D_STYLE': os.getenv('MAPBOX_3D_STYLE'),
        'center_lat': center_lat,
        'center_lon': center_lon,
        'latitude_array':latitude_list,
        'longitude_array':longitude_list,
    })