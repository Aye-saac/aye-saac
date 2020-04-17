#!/usr/bin/env bash


# start all the python scripts in the background and redirect their outputs in the services_log directory
echo "Starting all services"

#python3 -m ayesaac.services.automatic_speech_recognition.main > ayesaac/services_log/1_automatic_speech_recognition.txt &
python3 -m ayesaac.services.natural_language_understanding.main > ayesaac/services_log/2_natural_language_understanding.txt &
python3 -m ayesaac.services.manager.main > ayesaac/services_log/3_manager.txt &
python3 -m ayesaac.services.camera_manager.main > ayesaac/services_log/4_0_camera_manager.txt &
#python3 -m ayesaac.services.webcam.main > ayesaac/services_log/4_1_webcam.txt &
#python3 -m ayesaac.services.webcam_bis.main > ayesaac/services_log/4_2_webcam.txt &
python3 -m ayesaac.services.object_detection.main > ayesaac/services_log/5_0_object_detection.txt &
python3 -m ayesaac.services.optical_character_recognition.main > ayesaac/services_log/5_0_optical_character_recognition.txt &
python3 -m ayesaac.services.color_detection.main > ayesaac/services_log/5_1_color_detection.txt &
python3 -m ayesaac.services.position_detection.main > ayesaac/services_log/5_1_position_detection.txt &
python3 -m ayesaac.services.interpreter.main > ayesaac/services_log/6_interpreter.txt &
python3 -m ayesaac.services.natural_language_generator.main > ayesaac/services_log/7_natural_language_generator.txt &
#python3 -m ayesaac.services.text_to_speech.main > ayesaac/services_log/8_text_to_speech.txt &
python3 -m ayesaac.services.external_interface_bot.main > ayesaac/services_log/9_external_interface &

echo "Start flask server"
flask run --host=0.0.0.0