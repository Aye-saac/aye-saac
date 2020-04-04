
import cv2
import keras_ocr
import argparse
import matplotlib.pyplot as plt

from ayesaac.services.optical_character_recognition.bounding_box_to_phrases import bb_to_text


def take_a_picture(camera_index):
    cap = cv2.VideoCapture(camera_index)
    _, picture = cap.read()
    picture = cv2.cvtColor(picture, cv2.COLOR_RGB2BGR)
    print(picture.shape)
    return picture


def main(args):
    pipeline = keras_ocr.pipeline.Pipeline()

    if args.filepath:
        picture = keras_ocr.tools.read(args.filepath)
    else:
        picture = take_a_picture(args.camera_index)

    picture = cv2.resize(picture, (640, 480), cv2.INTER_AREA)
    predictions = pipeline.recognize([picture])[0]

    text = bb_to_text(predictions)
    print(text)

    fig, axs = plt.subplots(nrows=1, figsize=(20, 20))
    keras_ocr.tools.drawAnnotations(image=picture, predictions=predictions, ax=axs)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script for testing ocr with either the webcam \
    or an image if a filepath is given.')
    parser.add_argument('--camera-index', type=int, default=0, metavar='INT',
                        help='camera index, in case of multiple camera (default: 0)')
    parser.add_argument('--filepath', type=str, default=None, metavar='STR',
                        help='filepath of an image to be tested (default: None)')
    args = parser.parse_args()
    main(args)
