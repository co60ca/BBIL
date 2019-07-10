
# BLE Beacon Indoor Localization Dataset (BBIL Dataset)
# Introduction
This dataset was created to facilitate reasearch into indoor localization with BLE beacons. Data was collected from September 2018 to May 2019 in two seperate locations.
Several participants assisted with the experiment each carrying 
This dataset is released in hope that researchers will use it as a 
We initially collected this dataset noting a lack of available indoor localization datasets with labeled data. The dataset is being utilized by the authors for an upcoming paper that can be found here < insert link here >.

The authoritative location of this dataset is < insert data repo >.

## Data Links
< Include links here >

### Citation
Please cite < give citation here > if you choose to use this dataset in your experiments.

## Performance
If you wish to compare prediction results please calculate using absolute error (i.e. the L2 distance from your predictions). In our experiments we compare the 90th percentile or the distance which 90% of errors are less than.

1. For each row in `experiment<n>/test/<stamp>_data_wide.csv` calculate the l2 distance between your prediction and the realx, realy values 
2. Concatenate this list of errors into a vector for all trials/files the test directory
3. On this vector find the 90th percentile and mean and report those

Our best results are as follows: < Include paper link >
| Experiment | Model | Mean | 90th Percentile |
| - | - | - | - |
| 1 | LSTM | 1.5399 | 2.3059 |
| 2 | Elman Network | 0.9620 | 1.3792 |



## Deployment
Our implementation uses the fixed-receiver moving-transmitter method of indoor localization. We use Raspberry Pis and BLE beacons as our receivers and transmitters respectively. The two seperate locations are as follows:
< Include the two diagrams here > 
We used the following equipment, configuration and software for the experiment.
| | |
| - | - |
| Android Minimum Version | 4.4 | 
| Beacon Type | Gimbal Series 10 |
| Beacon Profile | iBeacon |
| Beacon Transmit Power | 0 dbm |
| Beacon Transmission Interval | 10 Hz |
| Beacon Calibrated Power | Unused | 
| Edge Type | Raspberry Pi 3 |
| Raspberry Pi OS | Raspbian Jessie Lite |
| Raspberry Pi Software | [Beaconpi](https://github.com/co60ca/beaconpi) |
| Edge Placement Height | 1.6 Metres |

We use Raspberry Pis and BLE beacons as our receivers and 
For brevity we subsequently use edge and beacon' to refer to these.

The data recording was done via the [Beaconpi](https://github.com/co60ca/beaconpi) software. Beaconpi runs both on the edges and a centralized server which communicates bidirectionally between the two main 
The edges and server components sync to the same clock to 
The frame records the fingerprint and the Received Signal 
The edge then stamps the frame with a timestamp based on its local synced clock.

To validate our methods we also collect ground truths via an [Android application](https://github.com/peterspenler/MapTracker) as the 
The Android application records the location of the wearer via self reporting and also collects the accelerometer and gyroscope data for the participant. The participants were asked to randomly walk around the room for around 3 minutes at least 3 times a day. This varied as is evident from the dataset which was expected. The participants walked in straight lines between landmarks that were placed frequently in the space.

**Note**: data.csv, and data_wide.csv files which contain RSSI data contain interpolated true locations based on interpolating linearly between the last landmark presses in accordance to the descrete timesteps.

This chart gives the minimum, max, and average distances between a landmark and their nearests neighbour across the landmark set. We also include the raw landmark data in the dataset at the root of each experiment.

| Distance | Experiment 1 | Experiment 2 |
| - | - | - |
| Minimum | 0.66 | 0.3 |
| Max | 2.0 | 1.33 | 
| Average | 1.33 | 0.88 |


# Data Format
The data is formatted into training, validation, and testing sets for each of the two rooms. Models trained against this dataset should be reported against the testing set **without** using the testing set for model selection or training (such as SGD in Neural Network training).
The directory layout is as follows:
	
	experiment1/
	  room-data.json
	  room.png
	  train/
	    edges.csv
	    2018-09-18T17-58-09-000000_9_acc.csv
	    2018-09-18T17-58-09-000000_9_com.csv
	    2018-09-18T17-58-09-000000+0000_9_data_wide.csv
	    2018-09-18T17-58-09-000000_9_data.csv
	    2018-09-18T17-58-09-000000_9_pos.csv
	    2018-09-18T17-58-09-000000_9.cfg
	    ...
	  valid/
	    ...
	  test/
	    ...
	experiment2/
	  ...

Each of the bottom level directories contain all of the data.

### Files
In this section I describe how the data is formatted into flat files in case there is ambiguity or it is not clear what each value represents.

The prefix for each filename follows the strftime format `%Y-%m-%dT%H-%M-%S-%f` which is a RFC3339 datetime with all separators replaced with dashes for compatibility with Windows file systems, this is mostly to keep filenames unique. 

The number between the timestamp and file type is the beacons unique identifier.

All CSV file were formatted with comma seperated fields with new records indicated with the new line character. This is the default Python pandas format.
Comments in this document are depicted with the # symbol and are not present in the files.


    # .cfg
    # stored in JSON format
	{
	    "Beacon Height": 109.0, # Listed in centimeters
	    "Beacon Label": "k",
	}
###
	# data.csv
    Datetime:   datetime of landmark press or
	            interpolated location
	beaconid:   integer that uniquely identifys a beacon
	edgenodeid: integer that uniquely identifies the
	            edge recieving this rssi in this record
	rssi:  float of the averaged RSSI from that period 
	realx: float of true x beacon location in this period 
	realy: float of true y location as above
###
    # data_wide.csv
    # Similar to data.csv but pivots all edgenodeid to 
    # separate columns
    Datetime: datetime of landmark press or
	            interpolated location
	beaconid:   integer that uniquely identifys a beacon
	realx: float of true x beacon location in this period 
	realy: float of true y location as above
	edge_<n>: float of rssi for that edge or NaN
	# edgenodeid is removed as it was the pivot column
###
	# pos.csv
	Datetime: datetime of landmark press
	realx: True X location based on the room
	       coordinate system
	realy: True Y location as above
###
    # com.csv
    Datetime: datetime of compass event in Android
    azimuth: This is the angle between the device's 
             current compass direction and
             magnetic north as Android API
### 
    # acc.csv
    Datetime: datetime of acceleration event in Android
    accx:     x acceleration from Android
    accy:     y acceleration
    accz:     z acceleration

###

    # edges.csv
    # contains trained gamma and bias parameters
    # for pathloss curve as below for each pair
    of edge/beacons in the experiment
    beaconid: beacon for this pair
    edgenodeid: edge for this pair
    gamma: gamma parameter
    bias: bias parameter in dbm
    edge_x: x coordinate of room location in meters
    edge_y: y coordinate
    edge_z: z coordinate
    
$$d = 10^{\frac{b-Pr}{10\gamma}}$$
$Pr$ is Power Received in dbm at edge
$b$ is a bias term
$\gamma$ is a room constant
Values were trained from training data using an optimizer.

    # room-data.json
    # json file of landmarks
    {"Landmarks": [
         {
            "Label": "AR",        # Floor Label
            "XDisplayLoc": 429.0, # Pixel X location
            "XLoc": 20.88,        # Room Space X Location Metres
            "YDisplayLoc": 692.0, # Pixel Y location
            "YLoc": 4.874         # Room Space Y Location Metres
        },
        ...
     ]}

For specifics on Android data collection see our app:
[MapTracker](https://github.com/peterspenler/MapTracker). Items from `acc.csv` were renamed.


#### Datetime format
All date time formats are saved in [RFC3339](https://tools.ietf.org/html/rfc3339) with microsecond precision.

# Python
All python files are in `py/`
We provide requirements with`pip install -r requirements.txt`alternatively consider a conda environment. We only require pandas for csv reading and datetime parsing. This will pull other requirements.

    # Gives you a dictionary with train, valid, test and other data
    ds = packageutils.unpackage_datasets(dirname, dataobject_format=False)
    
