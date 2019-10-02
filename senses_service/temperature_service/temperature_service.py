import eventlet
import Adafruit_DHT as dht
from nameko.events import EventDispatcher
from nameko.rpc import rpc
from nameko_redis import Redis
from config import ServicesNames, EventNames, REDIS_NAME, TEMPERATURE_SENSOR_PIN

eventlet.monkey_patch()


class TemperatureService:
    name = ServicesNames.TEMPERATURE_SERVICE
    dispatch = EventDispatcher()
    redis = Redis(REDIS_NAME)

    @rpc
    def update_temperature(self):
        humidity, temperature = dht.read_retry(dht.DHT22, TEMPERATURE_SENSOR_PIN)
        self.redis.set('temperature', temperature)
