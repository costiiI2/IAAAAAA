import cv2
import cvlib
from cvlib.object_detection import draw_bbox
import matplotlib.pyplot as plt
from .centroid_tracker import CentroidTracker
from tqdm import tqdm

class BottleCounter():
    def __init__(self, confidence=0.2, max_disappeared=200) -> None:
        self.max_disappeared = max_disappeared # Number of frames to keep an object in memory before deregistering
        self.ct = None
        self.confidence = confidence # Confidence threshold for object detection
        self.object_count = 0


    # Extract frames from a video
    def _get_video_as_frames(self, video_path) -> list:
        cap = cv2.VideoCapture(video_path)
        if cap is None:
            raise('Video not found')
    
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        return frames


    # Detect bottles with YOLOv4 in a frame and return the bounding boxes, labels and confidence scores
    def _get_bottles(self, frame):
        bbox, label, conf = cvlib.detect_common_objects(frame, confidence=self.confidence, model='yolov4')

        bottle_bbox = []
        bottle_label = []
        bottle_conf = []

        # Only keep the bounding boxes with label 'bottle'
        for i in range(len(label)):
            if label[i] == 'bottle':
                bottle_bbox.append(bbox[i])
                bottle_label.append(label[i])
                bottle_conf.append(conf[i])

        return bottle_bbox, bottle_label, bottle_conf


    # Detect bottles in a frame and track them using the CentroidTracker
    def _detect_bottles(self, frame, show=False):
        bbox, label, conf = self._get_bottles(frame)
        output_frame = draw_bbox(frame, bbox, label, conf)

        if self.ct is None:
            raise ValueError('CentroidTracker not initialized.')

        # Update the centroid tracker using the detected bounding boxes
        objects = self.ct.update(bbox)
        for (objectID, centroid) in objects.items():
            text = "{}".format(objectID)
            cv2.putText(output_frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(output_frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

        if show:
            plt.imshow(output_frame)
            plt.show()

        return output_frame


    # Count the number of bottles in a video
    def count_bottles_video(self, input_video_path, output_video_name=None) -> None:
        frames = self._get_video_as_frames(input_video_path)
        if frames is None:
            raise ValueError('No frames found in video')

        if output_video_name is not None:
            video = cv2.VideoWriter(output_video_name, cv2.VideoWriter_fourcc(*'mp4v'), 10, (frames[0].shape[1], frames[0].shape[0]))

        # Process all the frames in the video
        self.ct = CentroidTracker(maxDisappeared=self.max_disappeared)
        for frame in tqdm(frames, desc='Processing frames'):
            output_frame = self._detect_bottles(frame)
            if output_video_name is not None:
                video.write(output_frame)

        if output_video_name is not None:
            video.release()

        print(f'Number of bottles counted: {self.ct.object_count()}')


    # Initialize the CentroidTracker and object count for a stream of frames
    def start_stream_bottle_count(self) -> None:
        self.ct = CentroidTracker(maxDisappeared=self.max_disappeared)
        self.object_count = 0


    # Add a frame to the stream and update the object count if a new bottle is detected
    def update_stream(self, new_frame) -> None:
        previous_object_count = self.object_count
        self._detect_bottles(new_frame)
        if self.ct.object_count() > previous_object_count:
            self.object_count = self.ct.object_count()
            print(f"New bottle detected. Total bottles: {self.object_count}")


    # Get the total number of bottles detected in the stream
    def get_bottle_counter(self) -> None:
        print(f'Total bottles detected: {self.object_count}')