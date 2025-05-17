import cv2

def tim_id_webcam():
    """Tìm kiếm và in ra các ID webcam có thể. Báo nếu không tìm thấy."""
    index = 0
    found_camera = False
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            cap.release()
            if index == 0 and not found_camera:
                print("Không tìm thấy webcam nào.")
            break
        else:
            print(f"Tìm thấy webcam tại ID: {index}")
            found_camera = True
            cap.release()
        index += 1

if __name__ == "__main__":
    tim_id_webcam()
