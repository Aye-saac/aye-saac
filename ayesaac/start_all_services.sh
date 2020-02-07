#!/usr/bin/env bash

# delete the old logs
rm ./logs/*.txt

# start all the python scripts in the background and redirect their outputs in the logs directory
python3 -u ./main.py services.automatic_speech_recognition.main > ./logs/1_automatic_speech_recognition.txt &
python3 -u ./main.py services.natural_language_understanding.main > ./logs/2_natural_language_understanding.txt &
python3 -u ./main.py services.manager.main > ./logs/3_manager.txt &
python3 -u ./main.py services.camera_manager.main > ./logs/4_camera_manager.txt &
python3 -u ./main.py services.object_detection.main > ./logs/5_object_detection.txt &
python3 -u ./main.py services.interpreter.main > ./logs/6_interpreter.txt &
python3 -u ./main.py services.natural_language_generator.main > ./logs/7_natural_language_generator.txt &
python3 -u ./main.py services.text_to_speech.main > ./logs/8_text_to_speech.txt &
