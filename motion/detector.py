import logging
import threading
import time

import cv2
import picamera
import picamera.array


class MotionDetector:
    def __init__(self, resolution=(800, 600), framerate=16, min_contour_area=6000, delta_threshold=15, logger=None):
        self.logger = logger or logging.getLogger()
        self.min_contour_area = min_contour_area
        self.resolution = resolution
        self.framerate = framerate
        self.delta_threshold = delta_threshold
        self.frames = []
        self.avg_frame = None
        self.lock = threading.RLock()
        self.task = threading.Thread(target=self.detect_motion)
        self.task.daemon = True
        self.task.start()

    def detect_motion(self):
        with picamera.PiCamera(resolution=self.resolution, framerate=self.framerate) as camera:
            with picamera.array.PiRGBArray(camera) as output:
                time.sleep(3)
                for rgb_frame in camera.capture_continuous(output, format='rgb', use_video_port=True):
                    try:
                        frame = rgb_frame.array
                        gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                        smooth_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

                        if self.avg_frame is None:
                            self.avg_frame = smooth_frame.copy().astype('float')
                            continue

                        cv2.accumulateWeighted(smooth_frame, self.avg_frame, 0.5)
                        delta_frame = cv2.absdiff(smooth_frame, cv2.convertScaleAbs(self.avg_frame))

                        thresh_frame = cv2.threshold(delta_frame, self.delta_threshold, 255, cv2.THRESH_BINARY)[1]
                        thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)
                        (_, contours, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL,
                                                            cv2.CHAIN_APPROX_SIMPLE)

                        significant_contours = list(filter(self.is_significant, contours))
                        if len(significant_contours) > 0:
                            self.logger.debug('Motion detected. Saving frame...')
                            with self.lock:
                                # todo: potential mem leak, use circular frame buffer
                                self.frames.append(frame)
                    except Exception:
                        self.logger.error('Motion detection error', exc_info=True)
                    finally:
                        output.truncate(0)

    def is_significant(self, contour):
        area = cv2.contourArea(contour)
        result = area > self.min_contour_area
        if result:
            self.logger.debug('Contour area', area)
        return result

    def is_motion_detected(self):
        with self.lock:
            return len(self.frames) > 0

    def captured_frames(self):
        with self.lock:
            results = self.frames
            # reset frames
            self.frames = []
            return results
