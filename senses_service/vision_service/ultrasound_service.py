import time

import eventlet
from RPi import GPIO
from nameko.events import EventDispatcher, event_handler, SINGLETON
from nameko.rpc import rpc
from nameko_redis import Redis

from config import ServicesNames, EventNames, REDIS_NAME, ULTRA_SOUND_SENSOR_LEFT, ULTRA_SOUND_SENSOR_RIGHT, \
    ULTRA_SOUND_SENSOR_MIDDLE

eventlet.monkey_patch()
class UltrasoundService:
    name = ServicesNames.ULTRASOUND_SERVICE
    dispatch = EventDispatcher()
    redis = Redis(REDIS_NAME)

    @staticmethod
    def distance(ultrasound_sensor, temperature):
        GPIO.output(ultrasound_sensor.trigger_pin, True)
        time.sleep(0.00001)
        GPIO.output(ultrasound_sensor.trigger_pin, False)
        StartTime = time.time()
        StopTime = time.time()

        # save StartTime
        while GPIO.input(ultrasound_sensor.echo_pin) == 0:
            StartTime = time.time()
        # save time of arrival
        while GPIO.input(ultrasound_sensor.echo_pin) == 1:
            StopTime = time.time()
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime

        # distance = (TimeElapsed * 34300*(1+float(temperature)/273)) / 2
        distance = (TimeElapsed * 34300) / 2

        return distance

    @rpc
    def run(self):
        temperature = self.redis.get('temperature')
        if not temperature:
            temperature = 25
        right_front_distance = self.distance(ULTRA_SOUND_SENSOR_RIGHT, temperature)
        left_front_distance = self.distance(ULTRA_SOUND_SENSOR_LEFT, temperature)
        middle_front_distance = self.distance(ULTRA_SOUND_SENSOR_MIDDLE, temperature)
        if right_front_distance < 15 or middle_front_distance < 15 or left_front_distance < 15:
            self.dispatch(EventNames.TRIGGER_LIGHTS, True)
            self.dispatch(EventNames.TRIGGER_ENGINES, {'drive': False})
        else:
            self.dispatch(EventNames.TRIGGER_LIGHTS, False)
            self.dispatch(EventNames.TRIGGER_ENGINES, {'drive': True, 'direction': 'forward'})
