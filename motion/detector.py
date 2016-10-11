import threading
import sys
import time

import picamera
import picamera.array
import cv2


class MotionDetector:
    def __init__(self, min_contour_area=6000, resolution=(640, 480), framerate=16, delta_threshold=10):
        self.min_contour_area = min_contour_area
        self.resolution = resolution
        self.framerate = framerate
        self.delta_threshold = delta_threshold
        self.frames = []
        self.avg_frame = None
        self.lock = threading.RLock()
        self.task = threading.Thread(target=self.detect_motion)
        self.task.start()

    def is_significant(self, contour):
        return cv2.contourArea(contour) > self.min_contour_area

    def detect_motion(self):
        with picamera.PiCamera(resolution=self.resolution, framerate=self.framerate) as camera:
            with picamera.array.PiRGBArray(camera) as output:
                time.sleep(3)
                for rgb_frame in camera.capture_continuous(output, format='rgb', use_video_port=True):
                    try:
                        frame = rgb_frame.array
                        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

                        if self.avg_frame is None:
                            self.avg_frame = gray_frame.copy().astype('float')
                            output.truncate(0)
                            continue

                        delta_frame = cv2.absdiff(gray_frame, cv2.convertScaleAbs(self.avg_frame))
                        cv2.accumulateWeighted(gray_frame, self.avg_frame, 0.5)

                        thresh_frame = cv2.threshold(delta_frame, self.delta_threshold, 255, cv2.THRESH_BINARY)[1]
                        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
                        (contours, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL,
                                                         cv2.CHAIN_APPROX_SIMPLE)

                        significant_contours = list(filter(self.is_significant, contours))
                        if len(significant_contours) > 0:
                            print('Motion detected. Saving frame...')
                            with self.lock:
                                # todo: potential mem leak
                                self.frames.append(frame)
                    except:
                        print("Unexpected error:", sys.exc_info()[0])

    def is_motion_detected(self):
        with self.lock:
            return len(self.frames) > 0

    def captured_frames(self):
        with self.lock:
            results = self.frames
            # reset frames
            self.frames = []
            return results