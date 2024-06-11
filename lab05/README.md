# Lab5 - Line Following Drone

## Description
This two packages contains different modules that are used to send directions to the Crazyflie 2.1 drone by following a line and track objects. This package does not include the parts of the code that are running on the drone and are used to control the drone and send the images.

## Requirements
To use this package, you need to create a virtual environment and install the required packages. You can do this by running the following commands:

```bash
conda create -n dronepilot python=3.11
conda activate dronepilot
pip install -r requirements.txt
```

## Running

To run our code, once the environment is created, run the following command:

```
python main.py --ip=192.168.4.1 --port=5000 --confidence=0.2 --max_disappeared=200
```

This command is an example. The `ip` and `port` should be adapted to the drone. `confidence` is used to set the confidence of YOLOv4 for detecting bottles in the images, and `max_disappeared` indicates the number of frames before a bottle that is out of the frame is unregistered.

## Modules

### CentroidTracker
**Source Code**: [SimpleObjectTracking on Github](https://github.com/Practical-CV/Simple-object-tracking-with-OpenCV/tree/master)

#### Tracks the objects given their bouding boxes
Amazing yet simple object tracker built entirely with OpenCV

#### Our modified version of the code
In order to count the number of objects that have been tracked, we have added a new method `object_count` to the `CentroidTracker` class. The method returns the number of objects that have been tracked.

```python
class CentroidTracker():
	...
	def object_count(self):
		# return the number of objects that have been tracked
		return self.nextObjectID
    ...
```

### BottleCounter
This module uses the `CentroidTracker` module to track the bottles in a video stream or a video file. The module uses YOLOv4 to detect the bottles in each frame.

When using in video mode, the number of bottles detected is displayed at the end. When using in stream mode, after each new frame, if a new bottle is detected, a message is displayed on the console. The number of bottles detected can also displayed at the end.

### ImageReceiver
This module is used to connect to the drone, get the images from the drone and save them into a deque. The `get()` method should be run in a separate thread because it has an infinite loop that keeps getting the images from the drone. Then, the 'stop()' method should be called to stop the `get()` method.

### PathFinder
This module uses the LineDetectionModel provided by the assistants of IAA. The module uses the model to detect the line in the image and get the coordinates of the line. Those points are then used to compute the angle to follow the line.

## Limitations
The images provided by the drone are not always clear and low resolution. This can affect the performance of the object detection and tracking algorithms and the line detection model.