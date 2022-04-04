from datetime import datetime
import time
import numpy as np
import cv2


class DummyImagePublisher():

    def __init__(self, b=0, g=0, r=255):
        self.b = b
        self.g = g
        self.r = r

    def stream(self):
        while True:
            height = 240
            width = 640
            blank = np.zeros((height, width, 3))
            blank += 128
            str = "{}".format(datetime.now().isoformat())
            # print(str)
            cv2.putText(blank, str, (30, 130), cv2.FONT_HERSHEY_PLAIN, 2, (self.b, self.g, self.r), 2, cv2.LINE_AA)
            # cv2.imwrite('debug.png',blank)
            yield blank
            time.sleep(0.0333)




if __name__ == "__main__":
    
    dImage = DummyImagePublisher(255, 0, 0)

    for img in dImage.stream():
        cv2.imshow('image',img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

