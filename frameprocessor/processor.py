import time

import cv2


class FrameProcessor:
    def process(self, frames):
        print('Saving %d images...' % len(frames))
        ts = time.strftime("%Y%m%d%H%M%S")
        for i, frame in enumerate(frames):
            cv2.imwrite('image-%s-%02d.jpg' % (ts, i), frame)