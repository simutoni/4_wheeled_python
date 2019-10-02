import cv2
import io

import base64

import eventlet
import numpy as np
from PIL import Image
from nameko.events import EventDispatcher
from nameko.rpc import rpc
from nameko_redis import Redis
from config import ServicesNames, REDIS_NAME, EventNames
from senses_service.vision_service.lane_recognition import LaneRecognition

eventlet.monkey_patch()


class CameraService:
    name = ServicesNames.CAMERA_SERVICE
    dispatch = EventDispatcher()
    redis = Redis(REDIS_NAME)

    @classmethod
    def string_base64_to_image(cls, base64_string):
        imgdata = base64.b64decode(base64_string)
        return cv2.cvtColor(np.array(Image.open(io.BytesIO(imgdata))), cv2.COLOR_RGB2BGR)

    @rpc
    def run(self, image):
        steering_angle = LaneRecognition.process_image(self.string_base64_to_image(image))
        print(steering_angle)
        self.dispatch(EventNames.TRIGGER_ENGINES, {'steering_angle': steering_angle})
