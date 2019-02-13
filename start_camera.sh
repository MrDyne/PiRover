screen -dmS picam mjpg_streamer -i "input_raspicam.so -x 640 -y 480 -fps 30 -quality 5 -hf -vf" -o "output_http.so -n"
