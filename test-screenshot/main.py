import cv2
import numpy as np
from PIL import Image
import mss
from pynput import mouse
import tkinter as tk

# Global variables to store the start and end coordinates
x_start, y_start, x_end, y_end = 0, 0, 0, 0
selecting = False
root = None

def on_click(x, y, button, pressed):
    global x_start, y_start, x_end, y_end, selecting
    if pressed:
        x_start, y_start = x, y
        selecting = True
    else:
        x_end, y_end = x, y
        selecting = False
        root.quit()

def on_move(x, y):
    global root, x_start, y_start, selecting
    if selecting:
        canvas.delete("selection")
        x_end, y_end = x, y
        width = x_end - x_start
        height = y_end - y_start
        canvas.create_rectangle(x_start, y_start, x_end, y_end, outline="cyan", width=2, tags="selection")

def capture_screen_and_decode():
    global root, canvas

    # Create a minimal tkinter window for selection
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.3)  # Semi-transparent
    root.overrideredirect(True)  # Remove window decorations
    root.config(cursor="cross")  # Crosshair cursor

    # Create a canvas to draw the selection rectangle
    canvas = tk.Canvas(root, bg="#FFFF00", cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)

    print("Please select the area where the QR code is located...")

    # Collect mouse events
    with mouse.Listener(on_click=on_click, on_move=on_move) as listener:
        root.mainloop()

    # Ensure the coordinates are correct if user drags from bottom-right to top-left
    x1, y1 = min(x_start, x_end), min(y_start, y_end)
    x2, y2 = max(x_start, x_end), max(y_start, y_end)
    width, height = x2 - x1, y2 - y1

    print("Capturing selected screen area...")
    with mss.mss() as sct:
        monitor = {"top": y1, "left": x1, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        screenshot_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    print("Decoding QR code...")
    qr_code_detector = cv2.QRCodeDetector()
    data, points, _ = qr_code_detector.detectAndDecode(screenshot_cv)

    if data:
        print("QR Code content:", data)
    else:
        print("No QR code found or could not decode.")

if __name__ == "__main__":
    capture_screen_and_decode()
