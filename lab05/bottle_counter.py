import cv2
import cvlib
from cvlib.object_detection import draw_bbox
import matplotlib.pyplot as plt
from SimpleObjectTracking import CentroidTracker
from tqdm import tqdm
import argparse

def get_video_as_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    if cap is None:
        print('Video not found')
        return None
    
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    return frames

def get_bottles(frame, confidence=0.2):
    bbox, label, conf = cvlib.detect_common_objects(frame, confidence=confidence, model='yolov4')

    bottle_bbox = []
    bottle_label = []
    bottle_conf = []

    for i in range(len(label)):
        if label[i] == 'bottle':
            bottle_bbox.append(bbox[i])
            bottle_label.append(label[i])
            bottle_conf.append(conf[i])

    return bottle_bbox, bottle_label, bottle_conf

def detect_bottles(frame, ct, confidence=0.2, show=False):
    bbox, label, conf = get_bottles(frame, confidence=confidence)
    output_frame = draw_bbox(frame, bbox, label, conf)

    objects = ct.update(bbox)
    for (objectID, centroid) in objects.items():
        text = "{}".format(objectID)
        cv2.putText(output_frame, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(output_frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

    if show:
        plt.imshow(output_frame)
        plt.show()

    return output_frame
    

def count_bottles(input_video_path, output_video_name=None, confidence=0.2, max_disappeared=200):
    frames = get_video_as_frames(input_video_path)
    if frames is None:
        return None
    
    if output_video_name is not None:
        video = cv2.VideoWriter(output_video_name, cv2.VideoWriter_fourcc(*'mp4v'), 10, (frames[0].shape[1], frames[0].shape[0]))

    ct = CentroidTracker(maxDisappeared=max_disappeared)
    for frame in tqdm(frames, desc='Processing frames'):
        output_frame = detect_bottles(frame, ct, confidence=confidence, show=False)
        if output_video_name is not None:
            video.write(output_frame)

    if output_video_name is not None:
        video.release()

    print(f'Number of bottles counted: {ct.object_count()}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_video', type=str, help='Path to the input video')
    parser.add_argument('output_video', type=str, help='Path to the output video', default=None, nargs='?')
    parser.add_argument('--confidence', type=float, default=0.2, help='Confidence threshold')
    parser.add_argument('--max_disappeared', type=int, default=200, help='Max disappeared frames')
    args = parser.parse_args()

    count_bottles(args.input_video, args.output_video, confidence=args.confidence, max_disappeared=args.max_disappeared)
