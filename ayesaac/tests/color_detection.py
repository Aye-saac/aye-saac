
import cv2
from ayesaac.services.colour_detection.main import ColourDetection

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    _, image = cap.read()
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    colour_detect = ColourDetection()
    colour_detect.detect_colours(image)

