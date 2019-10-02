import collections
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library

GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BCM)   # Use physical pin numbering
from gpiozero import PWMOutputDevice
from nameko.standalone.rpc import ServiceRpcProxy


class EventNames:
    TRIGGER_ENGINES = 'trigger_engines'
    TEMPERATURE = 'temperature'
    TRIGGER_LIGHTS = 'trigger_lights'
    REQUEST_TEMPERATURE = 'request_temperature'


class ServicesNames:
    CAMERA_SERVICE = 'camera_service'
    ENGINES_SERVICE = 'engines_service'
    TEMPERATURE_SERVICE = 'temperature_service'
    ULTRASOUND_SERVICE = 'ultrasound_service'
    LIGHTS_SERVICE = 'lights_service'

REDIS_NAME = '4_wheeled_python'
redis_config = {REDIS_NAME: 'redis://localhost:6379/0'}
rabbit_config = {'AMQP_URI': "amqp://guest:guest@localhost:5672", 'REDIS_URIS': redis_config}

UltrasoundSensorPins = collections.namedtuple('UltrasoundSensorPins', 'trigger_pin echo_pin')
EnginePins = collections.namedtuple('EnginePins', 'forward_pin backward_pin pwm_pin')


# LIGHTS
FRONT_LIGHTS_PIN = 21
GPIO.setup(FRONT_LIGHTS_PIN, GPIO.OUT, initial=GPIO.LOW)

# TEMPERATURE SENSOR
TEMPERATURE_SENSOR_PIN = 8

# ULTRASOUND SENSORS
ULTRA_SOUND_SENSOR_RIGHT = UltrasoundSensorPins(16, 20)
GPIO.setup(ULTRA_SOUND_SENSOR_RIGHT.trigger_pin, GPIO.OUT)
GPIO.setup(ULTRA_SOUND_SENSOR_RIGHT.echo_pin, GPIO.IN)

ULTRA_SOUND_SENSOR_MIDDLE = UltrasoundSensorPins(19, 26)
GPIO.setup(ULTRA_SOUND_SENSOR_MIDDLE.trigger_pin, GPIO.OUT)
GPIO.setup(ULTRA_SOUND_SENSOR_MIDDLE.echo_pin, GPIO.IN)

ULTRA_SOUND_SENSOR_LEFT = UltrasoundSensorPins(6, 13)
GPIO.setup(ULTRA_SOUND_SENSOR_LEFT.trigger_pin, GPIO.OUT)
GPIO.setup(ULTRA_SOUND_SENSOR_LEFT.echo_pin, GPIO.IN)

# ENGINES
ENGINE_FRONT = EnginePins(7, 5, 12)
ENGINE_BACK = EnginePins(27, 22, 17)
ENGINE_DIRECTION = EnginePins(9, 11, 10)

ENGINE_BACK_PWM = PWMOutputDevice(ENGINE_BACK.pwm_pin, True, 0, 1000)
ENGINE_FRONT_PWM = PWMOutputDevice(ENGINE_FRONT.pwm_pin, True, 0, 1000)
ENGINE_DIRECTION_PWM = PWMOutputDevice(ENGINE_DIRECTION.pwm_pin, True, 0, 1000)

GPIO.setup(ENGINE_BACK.forward_pin, GPIO.OUT)
GPIO.setup(ENGINE_BACK.backward_pin, GPIO.OUT)

GPIO.setup(ENGINE_FRONT.forward_pin, GPIO.OUT)
GPIO.setup(ENGINE_FRONT.backward_pin, GPIO.OUT)

GPIO.setup(ENGINE_DIRECTION.backward_pin, GPIO.OUT)
GPIO.setup(ENGINE_DIRECTION.forward_pin, GPIO.OUT)


def rpc_proxy(service):
    return ServiceRpcProxy(service, rabbit_config)
