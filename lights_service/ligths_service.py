import eventlet
from RPi import GPIO
from nameko.events import event_handler
from config import FRONT_LIGHTS_PIN, ServicesNames, EventNames

eventlet.monkey_patch()


class LightsService:
    name = ServicesNames.LIGHTS_SERVICE

    @staticmethod
    def lights(status):
        if status:
            GPIO.output(FRONT_LIGHTS_PIN, GPIO.HIGH)
        else:
            GPIO.output(FRONT_LIGHTS_PIN, GPIO.LOW)

    @event_handler(ServicesNames.ULTRASOUND_SERVICE, EventNames.TRIGGER_LIGHTS)
    def handle_event(self, payload):
        self.lights(payload)
