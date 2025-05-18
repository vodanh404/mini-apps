print("App hỏi tuổi")
while True:
    tuoi = input("Nhập tuổi của bạn (1-120): ")
    if tuoi.isdigit():
        tuoi = int(tuoi)
        if 1 <= tuoi <= 120:
            print(f"Bạn {tuoi} tuổi.")
            break
        else:
            print("Vui lòng nhập tuổi từ 1 đến 120.")
    else:
        print("Vui lòng nhập một số hợp lệ.")