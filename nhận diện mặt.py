import cv2

# Khởi tạo bộ nhận diện khuôn mặt Haar Cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Mở camera (0 là camera mặc định)
cap = cv2.VideoCapture(0)

print("🎥 Đang mở camera, nhấn 'q' để thoát...")
while True:
    # Đọc từng khung hình từ camera
    ret, frame = cap.read()
    if not ret:
        break

    # Chuyển khung hình sang xám để xử lý nhanh hơn
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Phát hiện khuôn mặt
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Vẽ hình chữ nhật quanh khuôn mặt
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Hiển thị khung hình
    cv2.imshow("Face Detection", frame)

    # Thoát chương trình khi nhấn 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Giải phóng camera và đóng cửa sổ
cap.release()
cv2.destroyAllWindows()