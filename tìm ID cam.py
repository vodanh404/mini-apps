import cv2

def tim_id_webcam():
    """Tìm kiếm và in ra các ID webcam có thể."""
    index = 0
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            cap.release()
            break
        else:
            print(f"Tìm thấy webcam tại ID: {index}")
            cap.release()
        index += 1

if __name__ == "__main__":
    tim_id_webcam()