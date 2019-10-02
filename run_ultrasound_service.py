import eventlet
from RPi import GPIO
from nameko.containers import ServiceContainer
from config import rabbit_config, rpc_proxy, ServicesNames
from senses_service.vision_service import UltrasoundService

eventlet.monkey_patch()

service_container = ServiceContainer(UltrasoundService, config=rabbit_config)
service_container.start()
try:
    with rpc_proxy(ServicesNames.ULTRASOUND_SERVICE) as rpc:
        #while True:
        rpc.run()
        service_container.wait()
except KeyboardInterrupt:
    print('KeyboardInterrupt exception')
finally:
    service_container.stop()
    # GPIO.cleanup()
    # print('GPIO cleanup')
    print('Stopping services')

