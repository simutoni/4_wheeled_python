import eventlet
from RPi import GPIO
from nameko.containers import ServiceContainer
from config import rabbit_config, rpc_proxy, ServicesNames
from senses_service.temperature_service import TemperatureService

eventlet.monkey_patch()

service_container = ServiceContainer(TemperatureService, config=rabbit_config)
service_container.start()
try:
    with rpc_proxy(ServicesNames.TEMPERATURE_SERVICE) as rpc:
        while True:
            rpc.update_temperature()
            eventlet.sleep(30)
except KeyboardInterrupt:
    print('KeyboardInterrupt exception')
finally:
    GPIO.cleanup()
    service_container.stop()
    print('GPIO cleanup')
    print('Stopping services')
