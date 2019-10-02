from RPi import GPIO
from nameko.runners import ServiceRunner

from config import rabbit_config
from lights_service.ligths_service import LightsService
from motion_service.engine_service import EnginesService
#from senses_service.vision_service import CameraService


runner = ServiceRunner(config=rabbit_config)
runner.add_service(LightsService)
runner.add_service(EnginesService)
# runner.add_service(CameraService)

runner.start()
try:
    runner.wait()
except KeyboardInterrupt:
    print('KeyboardInterrupt exception')
finally:
    GPIO.cleanup()
    runner.stop()
    print('GPIO cleanup')
    print('Stopping services')
