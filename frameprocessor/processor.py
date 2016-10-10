import cv2


class FrameProcessor:
    def process(self, frames):
        for i, frame in enumerate(frames):
            cv2.imwrite('image%02d.jpg' % i, frame)