#!/usr/bin/env bash

# delete the old services_log
rm ./services_log/*.txt

# start all the python scripts in the background and redirect their outputs in the services_log directory
python3 -u ./main.py services.automatic_speech_recognition.main > ./services_log/1_automatic_speech_recognition.txt &
python3 -u ./main.py services.natural_language_understanding.main > ./services_log/2_natural_language_understanding.txt &
python3 -u ./main.py services.manager.main > ./services_log/3_manager.txt &
python3 -u ./main.py services.camera_manager.main > ./services_log/4_0_camera_manager.txt &
python3 -u ./main.py services.webcam.main > ./services_log/4_1_webcam.txt &
python3 -u ./main.py services.webcam_bis.main > ./services_log/4_2_webcam.txt &
python3 -u ./main.py services.object_detection.main > ./services_log/5_0_object_detection.txt &
python3 -u ./main.py services.optical_character_recognition.main > ./services_log/5_0_optical_character_recognition.txt &
python3 -u ./main.py services.color_detection.main > ./services_log/5_1_color_detection.txt &
python3 -u ./main.py services.position_detection.main > ./services_log/5_1_position_detection.txt &
python3 -u ./main.py services.interpreter.main > ./services_log/6_interpreter.txt &
python3 -u ./main.py services.natural_language_generator.main > ./services_log/7_natural_language_generator.txt &
python3 -u ./main.py services.text_to_speech.main > ./services_log/8_text_to_speech.txt &
