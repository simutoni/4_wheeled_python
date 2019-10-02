import base64
import time

import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray

from config import rpc_proxy, ServicesNames

def image_to_base64(image):
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(buffer)
    return jpg_as_text.decode("utf-8")

camera = PiCamera()
time.sleep(2)
camera.resolution = (512, 384)

try:
    with rpc_proxy(ServicesNames.CAMERA_SERVICE) as rpc:
        while True:
            rawCapture = PiRGBArray(camera, size=(512, 384))
            camera.capture(rawCapture, format='bgr')
            camera.capture('image_3.jpg')
            image = rawCapture.array
            image_str = image_to_base64(image)
            rpc.run(image_str)
finally:
    camera.close()

