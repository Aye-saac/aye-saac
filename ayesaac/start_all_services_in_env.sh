#!/usr/bin/env bash

# delete the old services_log
rm -f ayesaac/services_log/*.txt

# start all the python scripts in the background and redirect their outputs in the services_log directory
conda run -n aye-saac python -u -m ayesaac.services.external_interface_bot.bot > ayesaac/services_log/0_webserver.txt &
conda run -n aye-saac python -u -m ayesaac.services.automatic_speech_recognition.main > ayesaac/services_log/1_automatic_speech_recognition.txt &
conda run -n aye-saac python -u -m ayesaac.services.natural_language_understanding.main > ayesaac/services_log/2_natural_language_understanding.txt &
conda run -n aye-saac python -u -m ayesaac.services.manager.main > ayesaac/services_log/3_manager.txt &
conda run -n aye-saac python -u -m ayesaac.services.camera_manager.main > ayesaac/services_log/4_0_camera_manager.txt &
conda run -n aye-saac python -u -m ayesaac.services.webcam.main > ayesaac/services_log/4_1_webcam.txt &
conda run -n aye-saac python -u -m ayesaac.services.webcam_bis.main > ayesaac/services_log/4_2_webcam.txt &
conda run -n aye-saac python -u -m ayesaac.services.object_detection.main > ayesaac/services_log/5_object_detection.txt &
conda run -n aye-saac python -u -m ayesaac.services.interpreter.main > ayesaac/services_log/6_interpreter.txt &
conda run -n aye-saac python -u -m ayesaac.services.natural_language_generator.main > ayesaac/services_log/7_natural_language_generator.txt &
conda run -n aye-saac python -u -m ayesaac.services.text_to_speech.main > ayesaac/services_log/8_text_to_speech.txt &
