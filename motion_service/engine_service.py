import eventlet
from RPi import GPIO
from nameko.events import event_handler

from config import ServicesNames, EventNames, ENGINE_BACK_PWM, ENGINE_FRONT_PWM, ENGINE_DIRECTION_PWM, ENGINE_FRONT, \
    ENGINE_BACK, ENGINE_DIRECTION

eventlet.monkey_patch()


class EnginesService:
    name = ServicesNames.ENGINES_SERVICE

    @staticmethod
    def all_stop():
        GPIO.output(ENGINE_BACK.forward_pin, GPIO.LOW)
        GPIO.output(ENGINE_BACK.backward_pin, GPIO.LOW)
        GPIO.output(ENGINE_FRONT.forward_pin, GPIO.LOW)
        GPIO.output(ENGINE_FRONT.backward_pin, GPIO.LOW)
        GPIO.output(ENGINE_DIRECTION.backward_pin, GPIO.LOW)
        GPIO.output(ENGINE_DIRECTION.forward_pin, GPIO.LOW)
        ENGINE_BACK_PWM.value = 0
        ENGINE_FRONT_PWM.value = 0
        ENGINE_DIRECTION_PWM.value = 0

    @staticmethod
    def steer(speed=0.8, time=1, direction='left'):
        GPIO.output(ENGINE_DIRECTION.forward_pin, GPIO.LOW if direction == 'left' else GPIO.HIGH)
        GPIO.output(ENGINE_DIRECTION.backward_pin, GPIO.HIGH if direction == 'left' else GPIO.LOW)
        ENGINE_DIRECTION_PWM.value = speed
        eventlet.sleep(time)
        GPIO.output(ENGINE_DIRECTION.forward_pin, GPIO.LOW)
        GPIO.output(ENGINE_DIRECTION.backward_pin, GPIO.LOW)
        ENGINE_DIRECTION_PWM.value = 0

    @staticmethod
    def move(speed=0.4, time=5, direction='forward'):
        GPIO.output(ENGINE_BACK.forward_pin, GPIO.HIGH if direction == 'forward' else GPIO.LOW)
        GPIO.output(ENGINE_BACK.backward_pin, GPIO.HIGH if direction == 'backward' else GPIO.LOW)
        GPIO.output(ENGINE_FRONT.forward_pin, GPIO.HIGH if direction == 'forward' else GPIO.LOW)
        GPIO.output(ENGINE_FRONT.backward_pin, GPIO.HIGH if direction == 'backward' else GPIO.LOW)
        if speed < 0.6:
            ENGINE_FRONT_PWM.value = 1
            ENGINE_BACK_PWM.value = 1
            eventlet.sleep(0.4)
        ENGINE_FRONT_PWM.value = speed + 0.1
        ENGINE_BACK_PWM.value = speed
        eventlet.sleep(time)

        GPIO.output(ENGINE_BACK.forward_pin, GPIO.LOW)
        GPIO.output(ENGINE_BACK.backward_pin, GPIO.LOW)
        GPIO.output(ENGINE_FRONT.forward_pin, GPIO.LOW)
        GPIO.output(ENGINE_FRONT.backward_pin, GPIO.LOW)
        ENGINE_BACK_PWM.value = 0
        ENGINE_FRONT_PWM.value = 0

    @event_handler(ServicesNames.ULTRASOUND_SERVICE, EventNames.TRIGGER_ENGINES)
    @event_handler(ServicesNames.CAMERA_SERVICE, EventNames.TRIGGER_ENGINES)
    def handle_event(self, payload):
        if 'steering_angle' in payload:
            if payload['steering_angle'] < 75:
                self.steer(speed=1, direction='left')
            if payload['steering_angle'] > 105:
                self.steer(speed=1, direction='right')
        elif 'drive' in payload:
            if payload['drive']:
                self.move(speed=0.25, direction=payload['direction'], time=1)
            else:
                self.all_stop()
