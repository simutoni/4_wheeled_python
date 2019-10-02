#until nc -z rabbitmq-server 5672; do
#    echo "$(date) - waiting for rabbitmq..."
#    sleep 1
#done
cd /home/pi/ || exit
source venv/bin/activate
cd 4_wheels_python || exit
python3 run_temperature_service.py &
python3 run_ultrasound_service.py &
python3 run_camera_service.py &
