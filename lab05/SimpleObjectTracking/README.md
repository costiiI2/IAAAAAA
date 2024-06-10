# Simple Object Tracking using OpenCV

**Source Code**: [SimpleObjectTracking on Github](https://github.com/Practical-CV/Simple-object-tracking-with-OpenCV/tree/master)

### Tracks the objects given their bouding boxes
Amazing yet simple object tracker built entirely with OpenCV

### Requirements: (with versions tested by the author)

    python (3.7.3)
    opencv (4.1.0)
    numpy (1.61.4)
    imutils (0.5.2)

### Our modified version of the code
In order to count the number of objects that have been tracked, we have added a new method `object_count` to the `CentroidTracker` class. The method returns the number of objects that have been tracked.

```python
class CentroidTracker():
	...
	def object_count(self):
		# return the number of objects that have been tracked
		return self.nextObjectID
    ...