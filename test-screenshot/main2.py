import cv2
import numpy as np
from PIL import Image
import mss

def capture_screen_and_decode():
    print("Capturing screenshot...")
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        screenshot_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    print("Decoding QR code...")
    qr_code_detector = cv2.QRCodeDetector()
    data, points, _ = qr_code_detector.detectAndDecode(screenshot_cv)

    if data:
        print("QR Code successfuly scanned.")
    else:
        print("No QR code found or could not decode.")

if __name__ == "__main__":
    capture_screen_and_decode()
