import requests
import datetime
import json
import os
import shutil
import time

endpoint_url = "https://api.data.gov.sg/v1/transport/traffic-images"

camera_locations_path = '../../data/raw/camera_locations.json'
images_dir = '../../data/raw/imgs/'

# Create the information on cameras if it doesn't exist
if not os.path.exists(camera_locations_path):
    if not os.path.exists(images_dir):
        os.mkdir(images_dir)
    r = requests.get(endpoint_url)
    j = r.json()['items'][0]
    camera_locations = {}
    for cam in j['cameras']:
        camera_locations[cam['camera_id']] = cam['location']
        # Create the folder also
        camera_dir = images_dir + cam['camera_id']
        if not os.path.exists(camera_dir):
            os.mkdir(camera_dir)
        
    with open(camera_locations_path, 'w') as f:
        json.dump(camera_locations, f)

#dt = datetime.datetime.now()

start_dt = datetime.datetime(2018, 10, 1)
end_dt = datetime.datetime(2018, 10, 8)

dt = start_dt
while dt < end_dt:
    print(dt.strftime("%b %d, %H:%M:%S"))
    dt_str = dt.strftime('%Y-%m-%dT%H:%M:%S')
    while True:
        r = requests.get(endpoint_url + "?date_time=" + dt_str)
        if r.status_code == 200:
            break
        else:
            print("Error with endpoint. Trying again in 5 seconds.")
            time.sleep(5)
    
    j = r.json()['items'][0]
    
    for cam in j['cameras']:
        date_str = cam['timestamp'][:10]
        time_str = cam['timestamp'][11:19].replace(":", "-")
        # Prepare paths
        cam_dir = images_dir + cam['camera_id'] + '/'
        date_dir = cam_dir + date_str + '/'
        file_path = date_dir + time_str + '.jpg'
        
        # Create folders if missing
        if not os.path.exists(cam_dir):
            os.mkdir(cam_dir)
        if not os.path.exists(date_dir):
            os.mkdir(date_dir)
            
        if not os.path.exists(file_path):
            # Download and save image
            # Only download it if we never saved it before
            while True:
                img = requests.get(cam['image'], stream=True)
                if img.status_code == 200:
                    break
                else:
                    print("Error downloading image. Trying again in 5 seconds.")
                    time.sleep(5)
                
            with open(file_path, 'wb') as f:
                img.raw.decode_content = True
                shutil.copyfileobj(img.raw, f)
    
    dt += datetime.timedelta(seconds=20)
