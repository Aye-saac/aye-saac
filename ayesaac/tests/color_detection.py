
import cv2
from ayesaac.services.color_detection.main import ColorDetection

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    _, image = cap.read()
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    color_detect = ColorDetection()
    color_detect.detect_colors(image)

