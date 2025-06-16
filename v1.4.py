# Khai báo thư viện 
import configparser
import os
import smtplib
import cv2
from PIL import Image, ImageTk
import threading
import wikipediaapi
import webbrowser 
import time
import tkinter as tk
import math
from tkinter import (ttk, scrolledtext, messagebox, Toplevel, Label, N, W, E, S, END, Entry, filedialog,
                     Frame, Button, DISABLED, NORMAL, WORD, BOTH)
import periodictable as pt
from datetime import datetime, date
from tkcalendar import Calendar 
from ttkthemes import ThemedTk, ThemedStyle
import gzip 
import json
import requests
from unidecode import unidecode
# Các tính năng của ứng dụng
du_lieu_ghi_chu = "notes.ini"
def load_notes(): # Tải ghi chú từ file ini
    config = configparser.ConfigParser()
    config.read(du_lieu_ghi_chu)
    return config
def save_notes(selected_date, note_text): # Lưu ghi chú vào file ini
    config = load_notes()
    if selected_date not in config:
        config[selected_date] = {}
    config[selected_date]['note'] = note_text.strip()

    with open(du_lieu_ghi_chu, "w") as file:
        config.write(file)
def on_toplevel_close(toplevel_window): # Xử lý việc đóng cửa sổ Toplevel
    if toplevel_window in open_toplevels:
        open_toplevels.remove(toplevel_window)
    toplevel_window.destroy()
def clock(): # Tinh năng 1: Lịch và đồng hồ
    if not root:
        return
    # Tạo cửa sổ phụ cho tính năng 1
    tinh_nang_1 = tk.Toplevel(root)
    tinh_nang_1.title("Lịch và đồng hồ")
    tinh_nang_1.resizable(False, False)
    # Áp dụng chủ đề cho cửa sổ Toplevel
    style = ThemedStyle(tinh_nang_1)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_1.config(bg=theme_bg_color)

    notes = load_notes()
    today = datetime.now().strftime("%d-%m-%Y")

    # Đặt các frame vào cửa sổ Toplevel (tinh_nang_1)
    frame_left = ttk.Frame(tinh_nang_1, padding=20)
    frame_left.grid(column=0, row=0, sticky="nw")

    frame_right = ttk.Frame(tinh_nang_1, padding=20)
    frame_right.grid(column=1, row=0, sticky="ne")

    ttk.Label(frame_left, text="Ghi chú:", font=("Helvetica", 14, "bold")).grid(column=0, row=0, pady=5, sticky="w")
    note_entry = tk.Text(frame_left, width=25, height=10, font=("Helvetica", 12))
    note_entry.config(bg=theme_bg_color)
    note_entry.grid(column=0, row=1, pady=5)

    def save_note():
        selected_date = cal.get_date()
        note_text = note_entry.get("1.0", tk.END).strip()
        save_notes(selected_date, note_text)
        print(f"Ghi chú cho {selected_date}: {note_text}")

    ttk.Button(frame_left, text="Lưu ghi chú", command=save_note).grid(column=0, row=2, pady=10)

    hom_nay = ttk.Label(frame_right, text=f"Ngày hôm nay: {today}", anchor="center", font=("Helvetica", 16))
    hom_nay.grid(column=0, row=0, columnspan=2, pady=5)

    thoi_gian = ttk.Label(frame_right, text="", anchor="center", font=("Helvetica", 24, "bold"))
    thoi_gian.grid(column=0, row=1, columnspan=2, pady=5)

    selection_color = "#09598F"  # Màu xanh lam nhạt mặc định
    cal = Calendar(frame_right, selectmode="day", year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,selectbackground=selection_color,selectforeground="white")
    cal.grid(column=0, row=2, columnspan=2, pady=10)

    # Đánh dấu ngày hôm nay
    cal.tag_config("today", background="lightblue")
    cal.calevent_create(datetime.now(), "Hôm nay", "today")

    def update_clock_in_toplevel(): # Đổi tên hàm để tránh nhầm lẫn
        thoi_gian_data = datetime.now().strftime("%H:%M:%S")
        thoi_gian.config(text=f"Thời gian: {thoi_gian_data}")
        # root.after(1000, update_clock_in_toplevel) # Dùng after của tinh_nang_1 nếu muốn nó dừng khi cửa sổ con đóng
        tinh_nang_1.after(1000, update_clock_in_toplevel) # Tốt hơn nên dùng after của cửa sổ Toplevel

    def update_note():
        selected_date = cal.get_date()
        note_entry.delete("1.0", tk.END)
        if selected_date in notes and 'note' in notes[selected_date]:
            note_entry.insert("1.0", notes[selected_date]['note'])

    cal.bind("<<CalendarSelected>>", lambda event: update_note())

    update_clock_in_toplevel()
    open_toplevels.append(tinh_nang_1)
    tinh_nang_1.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_1))
###################################################################################
recording = False
video_writer = None
def camera(): # Tính năng 2: Máy ảnh
    global recording, video_writer
    if not root:
        return
    # Tạo cửa sổ phụ cho tính năng 1
    tinh_nang_2 = tk.Toplevel(root)
    tinh_nang_2.title("2. Máy ảnh")
    tinh_nang_2.resizable(False, False)
    # Áp dụng chủ đề cho cửa sổ Toplevel
    style = ThemedStyle(tinh_nang_2)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_2.config(bg=theme_bg_color)

    cap = cv2.VideoCapture(0)

    tinh_nang_2 = ttk.Frame(tinh_nang_2, padding=20)
    tinh_nang_2.grid()
    label = Label(tinh_nang_2)
    label.grid(column=0, row=0, columnspan=2, sticky="ew")

    def update_frame():
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(image=img)
            label.img_tk = img_tk
            label.config(image=img_tk)
            if recording and video_writer is not None:
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                video_writer.write(frame_bgr)
        root.after(10, update_frame)

    def on_closing():
        cap.release()
        if video_writer is not None:
            video_writer.release()
        root.destroy()

    def chup_anh():
        ret, frame = cap.read()
        if ret:
            filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
            cv2.imwrite(filename, frame)
            print(f"Ảnh đã được lưu: {filename}")

    def quay_video():
        global recording, video_writer
        if not recording:
            recording = True
            filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
            print(f"Bắt đầu quay video: {filename}")
        else:
            recording = False
            if video_writer is not None:
                video_writer.release()
                print("Dừng quay video")
            video_writer = None

    def mo_kho_luu_tru():
        os.startfile(os.getcwd())

    ttk.Button(tinh_nang_2, text="Chụp ảnh", command=chup_anh).grid(column=0, row=1, columnspan=2, sticky="ew")
    ttk.Button(tinh_nang_2, text="Quay video", command=quay_video).grid(column=0, row=2, columnspan=2, sticky="ew")
    ttk.Button(tinh_nang_2, text="Kho lưu trữ", command=mo_kho_luu_tru).grid(column=0, row=3, columnspan=2, sticky="ew")

    root.protocol("WM_DELETE_WINDOW", on_closing)
    update_frame()

###################################################################################


    tinh_nang_4 = tk.Toplevel(root) # liên kết với của sổ chính bằng root
    tinh_nang_4.title("4. MÁy tính ") # Thiết lập tên cho cửa sổ
    tinh_nang_4.grid() # Thiết lập kích thước
    tinh_nang_4.resizable(False, False) # Loại bỏ khả năng thu phóng cảu cửa sổ
    # Đoạn này dùng để thay đổi giao diện 
    style = ThemedStyle(tinh_nang_4)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_4.config(bg=theme_bg_color)

    expression = ""  # Biến này để lưu trữ biểu thức hiện tại
    history = []     # Biến để lưu trữ lịch sử tính toán

    # Hàm cập nhật ô nhập liệu
    def update_entry(value):
        nonlocal expression
        expression += str(value)
        entry.delete(0, END)
        entry.insert(0, expression)

    # Hàm xóa toàn bộ ô nhập liệu
    def clear_entry():
        nonlocal expression
        expression = ""
        entry.delete(0, END)

    # Hàm tính toán kết quả
    def calculate_result():
        nonlocal expression, history
        try:
            # Thay thế các ký hiệu toán học với người dùng thành toán tử Python
            eval_expression = expression.replace("x", "*").replace(":", "/").replace(",", ".")
            # Đánh giá biểu thức
            result = str(eval(eval_expression))
            entry.delete(0, tk.END)
            entry.insert(0, result)
            history.append(f"{expression} = {result}") # Thêm vào lịch sử
            update_history_display() # Cập nhật hiển thị lịch sử
            expression = result  # Lưu kết quả để có thể tiếp tục tính toán
        except Exception as e:
            # Hiển thị thông báo lỗi
            messagebox.showerror("Lỗi", "Biểu thức không hợp lệ hoặc lỗi: " + str(e))
            expression = ""  # Đặt lại biểu thức khi có lỗi

    # Hàm xóa ký tự cuối cùng
    def delete_last_char():
        nonlocal expression
        expression = expression[:-1]  # Cắt bỏ ký tự cuối cùng
        entry.delete(0, tk.END)
        entry.insert(0, expression)

    # Hàm cập nhật hiển thị lịch sử
    def update_history_display():
        history_text.config(state=tk.NORMAL)
        history_text.delete(1.0, tk.END)
        for item in history:
            history_text.insert(tk.END, item + "\n")
        history_text.config(state=tk.DISABLED)

    # --- Các hàm chuyển đổi đơn vị ---
    # Ánh xạ từ tên đơn vị sang ký hiệu để hiển thị
    unit_symbols = {
        "mét": "m", "kilômét": "km", "centimét": "cm", "milimét": "mm",
        "inch": "in", "feet": "ft", "yard": "yd",
        "kilôgam": "kg", "gram": "g", "miligam": "mg", "pound": "lb", "ounce": "oz",
        "Celsius": "°C", "Fahrenheit": "°F", "Kelvin": "K"
    }

    def convert_length():
        try:
            value = float(length_input.get())
            unit_from_name = length_unit_from.get()
            unit_to_name = length_unit_to.get()

            # Chuyển đổi về mét
            if unit_from_name == "mét":
                base_value = value
            elif unit_from_name == "kilômét":
                base_value = value * 1000
            elif unit_from_name == "centimét":
                base_value = value / 100
            elif unit_from_name == "milimét":
                base_value = value / 1000
            elif unit_from_name == "inch":
                base_value = value * 0.0254
            elif unit_from_name == "feet":
                base_value = value * 0.3048
            elif unit_from_name == "yard":
                base_value = value * 0.9144
            else:
                base_value = value # fallback

            # Chuyển đổi từ mét sang đơn vị đích
            if unit_to_name == "mét":
                result = base_value
            elif unit_to_name == "kilômét":
                result = base_value / 1000
            elif unit_to_name == "centimét":
                result = base_value * 100
            elif unit_to_name == "milimét":
                result = base_value * 1000
            elif unit_to_name == "inch":
                result = base_value / 0.0254
            elif unit_to_name == "feet":
                result = base_value / 0.3048
            elif unit_to_name == "yard":
                result = base_value / 0.9144
            else:
                result = base_value # fallback


            length_result_label.config(text=f"Kết quả: {result:.4f} {unit_symbols.get(unit_to_name, unit_to_name)}")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị số hợp lệ cho chiều dài.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def convert_mass():
        try:
            value = float(mass_input.get())
            unit_from_name = mass_unit_from.get()
            unit_to_name = mass_unit_to.get()

            # Chuyển đổi về kilogram
            if unit_from_name == "kilôgam":
                base_value = value
            elif unit_from_name == "gram":
                base_value = value / 1000
            elif unit_from_name == "miligam":
                base_value = value / 1_000_000
            elif unit_from_name == "pound":
                base_value = value * 0.453592
            elif unit_from_name == "ounce":
                base_value = value * 0.0283495
            else:
                base_value = value

            # Chuyển đổi từ kilogram sang đơn vị đích
            if unit_to_name == "kilôgam":
                result = base_value
            elif unit_to_name == "gram":
                result = base_value * 1000
            elif unit_to_name == "miligam":
                result = base_value * 1_000_000
            elif unit_to_name == "pound":
                result = base_value / 0.453592
            elif unit_to_name == "ounce":
                result = base_value / 0.0283495
            else:
                result = base_value

            mass_result_label.config(text=f"Kết quả: {result:.4f} {unit_symbols.get(unit_to_name, unit_to_name)}")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị số hợp lệ cho khối lượng.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def convert_temperature():
        try:
            value = float(temp_input.get())
            unit_from_name = temp_unit_from.get()
            unit_to_name = temp_unit_to.get()

            # Chuyển đổi về độ C
            if unit_from_name == "Celsius":
                base_value = value
            elif unit_from_name == "Fahrenheit":
                base_value = (value - 32) * 5/9
            elif unit_from_name == "Kelvin":
                base_value = value - 273.15
            else:
                base_value = value

            # Chuyển đổi từ độ C sang đơn vị đích
            if unit_to_name == "Celsius":
                result = base_value
            elif unit_to_name == "Fahrenheit":
                result = (base_value * 9/5) + 32
            elif unit_to_name == "Kelvin":
                result = base_value + 273.15
            else:
                result = base_value

            temp_result_label.config(text=f"Kết quả: {result:.2f} {unit_symbols.get(unit_to_name, unit_to_name)}")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị số hợp lệ cho nhiệt độ.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    # --- Hàm tính điện trở từ vòng màu ---
    def calculate_resistor():
        colors = {
            "Đen": 0, "Nâu": 1, "Đỏ": 2, "Cam": 3, "Vàng": 4,
            "Lục": 5, "Lam": 6, "Tím": 7, "Xám": 8, "Trắng": 9
        }
        multiplier_colors = {
            "Đen": 1, "Nâu": 10, "Đỏ": 100, "Cam": 1000, "Vàng": 10000,
            "Lục": 100000, "Lam": 1000000, "Tím": 10000000,
            "Vàng kim": 0.1, "Bạc": 0.01
        }
        tolerance_values = { # Sử dụng giá trị trực tiếp để tránh lỗi làm tròn
            "Nâu": 1, "Đỏ": 2, "Lục": 0.5, "Lam": 0.25,
            "Tím": 0.1, "Xám": 0.05, "Vàng kim": 5, "Bạc": 10
        }

        try:
            band1 = resistor_band1.get()
            band2 = resistor_band2.get()
            multiplier_band = resistor_multiplier.get()
            tolerance_band = resistor_tolerance.get()

            num_bands = resistor_bands_var.get()

            value_band1 = colors[band1]
            value_band2 = colors[band2]

            if num_bands == 4: # Điện trở 4 vòng
                multiplier = multiplier_colors[multiplier_band]
                tolerance_percent = tolerance_values[tolerance_band] # Lấy giá trị phần trăm trực tiếp

                resistance = (value_band1 * 10 + value_band2) * multiplier
                resistor_result_label.config(text=f"Điện trở: {resistance:.2f} Ω ± {tolerance_percent:.2f}%")

            elif num_bands == 5: # Điện trở 5 vòng
                band3 = resistor_band3_dropdown.get() # Lấy giá trị từ dropdown
                value_band3 = colors[band3]
                multiplier = multiplier_colors[multiplier_band]
                tolerance_percent = tolerance_values[tolerance_band] # Lấy giá trị phần trăm trực tiếp

                resistance = (value_band1 * 100 + value_band2 * 10 + value_band3) * multiplier
                resistor_result_label.config(text=f"Điện trở: {resistance:.2f} Ω ± {tolerance_percent:.2f}%")
            else:
                messagebox.showerror("Lỗi", "Vui lòng chọn số vòng (4 hoặc 5).")

        except KeyError as e:
            messagebox.showerror("Lỗi", f"Màu không hợp lệ: {e}. Vui lòng chọn màu từ danh sách.")
        except Exception as e:
            messagebox.showerror("Lỗi", "Có lỗi xảy ra khi tính điện trở: " + str(e))

    def update_resistor_bands_display(*args):
        num_bands = resistor_bands_var.get()
        # Ẩn/hiện vòng 3
        if num_bands == 4:
            resistor_band3_label.grid_forget()
            resistor_band3_dropdown.grid_forget()
            # Di chuyển các thành phần dưới lên
            resistor_multiplier_label.grid(row=2, column=0, padx=5, pady=5, sticky=W)
            resistor_multiplier.grid(row=2, column=1, padx=5, pady=5, sticky=(W, E))
            resistor_tolerance_label.grid(row=3, column=0, padx=5, pady=5, sticky=W)
            resistor_tolerance.grid(row=3, column=1, padx=5, pady=5, sticky=(W, E))
        elif num_bands == 5:
            resistor_band3_label.grid(row=2, column=0, padx=5, pady=5, sticky=W) # Vòng 3 ở hàng 2
            resistor_band3_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky=(W, E))
            # Di chuyển các thành phần dưới xuống
            resistor_multiplier_label.grid(row=3, column=0, padx=5, pady=5, sticky=W) # Vòng nhân ở hàng 3
            resistor_multiplier.grid(row=3, column=1, padx=5, pady=5, sticky=(W, E))
            resistor_tolerance_label.grid(row=4, column=0, padx=5, pady=5, sticky=W) # Vòng dung sai ở hàng 4
            resistor_tolerance.grid(row=4, column=1, padx=5, pady=5, sticky=(W, E))


    # --- Giao diện người dùng ---
    # Notebook (Tabbed interface)
    notebook = ttk.Notebook(tinh_nang_4)
    notebook.grid(row=0, column=0, sticky=(N, W, E, S))
    tinh_nang_4.grid_columnconfigure(0, weight=1)
    tinh_nang_4.grid_rowconfigure(0, weight=1)

    # --- Tab 1: Máy tính cơ bản ---
    calc_frame = ttk.Frame(notebook, padding="10 10 10 10")
    notebook.add(calc_frame, text="Máy tính")

    # Chia calc_frame thành 2 cột chính: Lịch sử và Máy tính
    calc_frame.grid_columnconfigure(0, weight=1) # Cột lịch sử
    calc_frame.grid_columnconfigure(1, weight=2) # Cột máy tính (rộng hơn)
    for i in range(6): # Các hàng trong cột máy tính
        calc_frame.grid_rowconfigure(i, weight=1)


    # Lịch sử tính toán (Cột 0)
    history_frame = ttk.LabelFrame(calc_frame, text="Lịch sử tính toán", padding="10 10 10 10")
    history_frame.grid(row=0, column=0, rowspan=6, padx=10, pady=5, sticky=(N, S, W, E))
    history_frame.grid_rowconfigure(0, weight=1)
    history_frame.grid_columnconfigure(0, weight=1)

    history_text = tk.Text(history_frame, width=25, height=15, state=tk.DISABLED, wrap=tk.WORD, font=('Arial', 10))
    history_text.grid(row=0, column=0, sticky=(N, S, W, E))


    # Khung chứa các thành phần máy tính (Ô nhập liệu và các nút) (Cột 1)
    calculator_buttons_frame = ttk.Frame(calc_frame, padding="10 10 10 10")
    calculator_buttons_frame.grid(row=0, column=1, rowspan=6, padx=10, pady=5, sticky=(N, S, W, E))

    # Cấu hình grid cho calculator_buttons_frame
    calculator_buttons_frame.grid_columnconfigure(0, weight=1)
    calculator_buttons_frame.grid_columnconfigure(1, weight=1)
    calculator_buttons_frame.grid_columnconfigure(2, weight=1)
    calculator_buttons_frame.grid_columnconfigure(3, weight=1)
    calculator_buttons_frame.grid_columnconfigure(4, weight=1) # Cho nút Xóa
    for i in range(6): # 6 hàng (entry + 5 hàng nút)
        calculator_buttons_frame.grid_rowconfigure(i, weight=1)


    # Ô nhập liệu hiển thị biểu thức và kết quả
    entry = Entry(calculator_buttons_frame, font=('Arial', 18), justify='right') # Tăng font cho dễ nhìn
    entry.grid(row=0, column=0, columnspan=5, pady=10, ipadx=5, ipady=5, sticky=(W,E))

    # Định nghĩa style cho các nút (font và padding)
    button_style = ttk.Style()
    button_style.configure("TButton", font=('Arial', 12), padding=10) # Tăng font và padding mặc định

    # Nút lớn hơn cho "0"
    button_style.configure("Wide.TButton", font=('Arial', 12), padding=(20, 10)) # padding ngang lớn hơn


    # Các nút hàng 1
    ttk.Button(calculator_buttons_frame, text="AC", command=clear_entry, style="TButton").grid(column=0, row=1, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="(", command=lambda: update_entry("("), style="TButton").grid(column=1, row=1, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text=")", command=lambda: update_entry(")"), style="TButton").grid(column=2, row=1, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text=":", command=lambda: update_entry(":"), style="TButton").grid(column=3, row=1, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="Xóa", command=delete_last_char, style="TButton").grid(column=4, row=1, padx=2, pady=2, sticky=(W,E))

    # Các nút hàng 2
    ttk.Button(calculator_buttons_frame, text="7", command=lambda: update_entry("7"), style="TButton").grid(column=0, row=2, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="8", command=lambda: update_entry("8"), style="TButton").grid(column=1, row=2, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="9", command=lambda: update_entry("9"), style="TButton").grid(column=2, row=2, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="x", command=lambda: update_entry("x"), style="TButton").grid(column=3, row=2, padx=2, pady=2, sticky=(W,E))

    # Các nút hàng 3
    ttk.Button(calculator_buttons_frame, text="4", command=lambda: update_entry("4"), style="TButton").grid(column=0, row=3, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="5", command=lambda: update_entry("5"), style="TButton").grid(column=1, row=3, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="6", command=lambda: update_entry("6"), style="TButton").grid(column=2, row=3, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="-", command=lambda: update_entry("-"), style="TButton").grid(column=3, row=3, padx=2, pady=2, sticky=(W,E))

    # Các nút hàng 4
    ttk.Button(calculator_buttons_frame, text="1", command=lambda: update_entry("1"), style="TButton").grid(column=0, row=4, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="2", command=lambda: update_entry("2"), style="TButton").grid(column=1, row=4, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="3", command=lambda: update_entry("3"), style="TButton").grid(column=2, row=4, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="+", command=lambda: update_entry("+"), style="TButton").grid(column=3, row=4, padx=2, pady=2, sticky=(W,E))

    # Các nút hàng 5
    ttk.Button(calculator_buttons_frame, text="0", command=lambda: update_entry("0"), style="Wide.TButton").grid(column=0, row=5, columnspan=2, padx=2, pady=2, sticky=(W,E)) # Nút 0 dùng style riêng
    ttk.Button(calculator_buttons_frame, text=".", command=lambda: update_entry("."), style="TButton").grid(column=2, row=5, padx=2, pady=2, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="=", command=calculate_result, style="TButton").grid(column=3, row=5, padx=2, pady=2, sticky=(W,E))


    # --- Tab 2: Chuyển đổi đơn vị ---
    unit_convert_frame = ttk.Frame(notebook, padding="10 10 10 10")
    notebook.add(unit_convert_frame, text="Đổi đơn vị")

    # Cấu hình cột cho unit_convert_frame để các LabelFrame có thể căng ngang
    unit_convert_frame.grid_columnconfigure(0, weight=1)

    # Khai báo các danh sách đơn vị với ký hiệu hoặc tên đầy đủ để hiển thị trong Combobox
    # Danh sách hiển thị cho người dùng (có thể là tên đầy đủ)
    length_units_display = ["m", "km", "cm", "mn", "inch", "feet", "yard"]
    mass_units_display = ["kg", "g", "mg", "pound", "ounce"]
    temp_units_display = ["C", "F", "K"]

    # Frame cho chuyển đổi chiều dài
    length_frame = ttk.LabelFrame(unit_convert_frame, text="Chuyển đổi chiều dài", padding="10 10 10 10")
    length_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(N, W, E, S))
    length_frame.grid_columnconfigure(1, weight=1) # Cột 1 (input/combobox) căng ngang

    ttk.Label(length_frame, text="Giá trị:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
    length_input = ttk.Entry(length_frame, width=20)
    length_input.grid(row=0, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(length_frame, text="Từ:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
    length_unit_from = ttk.Combobox(length_frame, values=length_units_display, state="readonly")
    length_unit_from.set("m")
    length_unit_from.grid(row=1, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(length_frame, text="Sang:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
    length_unit_to = ttk.Combobox(length_frame, values=length_units_display, state="readonly")
    length_unit_to.set("cm")
    length_unit_to.grid(row=2, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Button(length_frame, text="Chuyển đổi", command=convert_length).grid(row=3, column=0, columnspan=2, pady=10)
    length_result_label = ttk.Label(length_frame, text="Kết quả:")
    length_result_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=W)


    # Frame cho chuyển đổi khối lượng
    mass_frame = ttk.LabelFrame(unit_convert_frame, text="Chuyển đổi khối lượng", padding="10 10 10 10")
    mass_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(N, W, E, S))
    mass_frame.grid_columnconfigure(1, weight=1)

    ttk.Label(mass_frame, text="Giá trị:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
    mass_input = ttk.Entry(mass_frame, width=20)
    mass_input.grid(row=0, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(mass_frame, text="Từ:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
    mass_unit_from = ttk.Combobox(mass_frame, values=mass_units_display, state="readonly")
    mass_unit_from.set("kg")
    mass_unit_from.grid(row=1, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(mass_frame, text="Sang:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
    mass_unit_to = ttk.Combobox(mass_frame, values=mass_units_display, state="readonly")
    mass_unit_to.set("g")
    mass_unit_to.grid(row=2, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Button(mass_frame, text="Chuyển đổi", command=convert_mass).grid(row=3, column=0, columnspan=2, pady=10)
    mass_result_label = ttk.Label(mass_frame, text="Kết quả:")
    mass_result_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=W)


    # Frame cho chuyển đổi nhiệt độ
    temp_frame = ttk.LabelFrame(unit_convert_frame, text="Chuyển đổi nhiệt độ", padding="10 10 10 10")
    temp_frame.grid(row=2, column=0, padx=5, pady=5, sticky=(N, W, E, S))
    temp_frame.grid_columnconfigure(1, weight=1)

    ttk.Label(temp_frame, text="Giá trị:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
    temp_input = ttk.Entry(temp_frame, width=20)
    temp_input.grid(row=0, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(temp_frame, text="Từ:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
    temp_unit_from = ttk.Combobox(temp_frame, values=temp_units_display, state="readonly")
    temp_unit_from.set("C")
    temp_unit_from.grid(row=1, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(temp_frame, text="Sang:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
    temp_unit_to = ttk.Combobox(temp_frame, values=temp_units_display, state="readonly")
    temp_unit_to.set("F")
    temp_unit_to.grid(row=2, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Button(temp_frame, text="Chuyển đổi", command=convert_temperature).grid(row=3, column=0, columnspan=2, pady=10)
    temp_result_label = ttk.Label(temp_frame, text="Kết quả:")
    temp_result_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=W)


    # --- Tab 3: Tính điện trở ---
    resistor_frame = ttk.Frame(notebook, padding="10 10 10 10")
    notebook.add(resistor_frame, text="Tính điện trở")

    # Cấu hình cột cho resistor_frame
    resistor_frame.grid_columnconfigure(0, weight=1) # Cột cho các frame con
    resistor_frame.grid_columnconfigure(1, weight=1) # Có thể thêm cột nếu muốn chia đôi

    resistor_color_options = [
        "Đen", "Nâu", "Đỏ", "Cam", "Vàng", "Lục", "Lam", "Tím", "Xám", "Trắng"
    ]
    multiplier_color_options = [
        "Đen", "Nâu", "Đỏ", "Cam", "Vàng", "Lục", "Lam", "Tím", "Vàng kim", "Bạc"
    ]
    tolerance_color_options = [
        "Nâu", "Đỏ", "Lục", "Lam", "Tím", "Xám", "Vàng kim", "Bạc"
    ]

    # Frame cho phần chọn số vòng
    bands_selection_frame = ttk.LabelFrame(resistor_frame, text="Chọn số vòng", padding="10 10 10 10")
    bands_selection_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=(W, E))
    bands_selection_frame.grid_columnconfigure(0, weight=1)
    bands_selection_frame.grid_columnconfigure(1, weight=1)

    resistor_bands_var = tk.IntVar(value=4)
    resistor_bands_var.trace_add("write", update_resistor_bands_display)
    ttk.Radiobutton(bands_selection_frame, text="4 Vòng", variable=resistor_bands_var, value=4).grid(row=0, column=0, padx=5, pady=5, sticky=W)
    ttk.Radiobutton(bands_selection_frame, text="5 Vòng", variable=resistor_bands_var, value=5).grid(row=0, column=1, padx=5, pady=5, sticky=W)

    # Frame cho các vòng màu
    bands_input_frame = ttk.LabelFrame(resistor_frame, text="Chọn màu vòng", padding="10 10 10 10")
    bands_input_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=(W, E))
    bands_input_frame.grid_columnconfigure(1, weight=1) # Cột 1 (combobox) căng ngang

    ttk.Label(bands_input_frame, text="Vòng 1 (Chữ số 1):").grid(row=0, column=0, padx=5, pady=5, sticky=W)
    resistor_band1 = ttk.Combobox(bands_input_frame, values=resistor_color_options, state="readonly")
    resistor_band1.set("Nâu") # Giá trị mặc định phổ biến
    resistor_band1.grid(row=0, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(bands_input_frame, text="Vòng 2 (Chữ số 2):").grid(row=1, column=0, padx=5, pady=5, sticky=W)
    resistor_band2 = ttk.Combobox(bands_input_frame, values=resistor_color_options, state="readonly")
    resistor_band2.set("Đen") # Giá trị mặc định phổ biến
    resistor_band2.grid(row=1, column=1, padx=5, pady=5, sticky=(W, E))

    # Vòng 3 (chỉ hiển thị khi chọn 5 vòng) - Định nghĩa ở đây để có thể truy cập
    resistor_band3_label = ttk.Label(bands_input_frame, text="Vòng 3 (Chữ số 3):")
    resistor_band3_dropdown = ttk.Combobox(bands_input_frame, values=resistor_color_options, state="readonly")
    resistor_band3_dropdown.set("Đen")

    resistor_multiplier_label = ttk.Label(bands_input_frame, text="Vòng nhân:")
    resistor_multiplier = ttk.Combobox(bands_input_frame, values=multiplier_color_options, state="readonly")
    resistor_multiplier.set("Đỏ") # Giá trị mặc định phổ biến (x100)

    resistor_tolerance_label = ttk.Label(bands_input_frame, text="Vòng dung sai:")
    resistor_tolerance = ttk.Combobox(bands_input_frame, values=tolerance_color_options, state="readonly")
    resistor_tolerance.set("Vàng kim") # Giá trị mặc định phổ biến (±5%)


    # Frame cho kết quả và nút tính
    result_resistor_frame = ttk.LabelFrame(resistor_frame, text="Kết quả", padding="10 10 10 10")
    result_resistor_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=(W, E))
    result_resistor_frame.grid_columnconfigure(0, weight=1)
    result_resistor_frame.grid_columnconfigure(1, weight=1)

    calculate_resistor_button = ttk.Button(result_resistor_frame, text="Tính toán điện trở", command=calculate_resistor)
    calculate_resistor_button.grid(row=0, column=0, columnspan=2, pady=5)
    resistor_result_label = ttk.Label(result_resistor_frame, text="Điện trở:")
    resistor_result_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=W)

    # Cập nhật hiển thị vòng 3 ban đầu (nếu là 4 vòng)
    update_resistor_bands_display()
###################################################################################
def gui_thu(): # Tính năng 3: Gửi thư 
    SENDER_EMAIL = "ungdungthu3@gmail.com"
    SENDER_PASSWORD = "dvmq ponq gplj awdq" # Đây là MẬT KHẨU ỨNG DỤNG, không phải mật khẩu tài khoản Gmail của bạn.

    def send_email():
        try:
            # Thiết lập máy chủ SMTP của Gmail
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls() # Bắt đầu mã hóa TLS
            server.login(SENDER_EMAIL, SENDER_PASSWORD) # Đăng nhập vào tài khoản Gmail

            # Tạo nội dung email
            subject = subject_entry.get()
            message = message_text.get('1.0', tk.END).strip() # Lấy nội dung từ Text widget, loại bỏ khoảng trắng thừa
            recipient = recipient_entry.get()

            # Kiểm tra xem người nhận có trống không
            if not recipient:
                messagebox.showerror("Lỗi", "Vui lòng nhập địa chỉ người nhận.")
                return

            email_message = f"Subject: {subject}\n\n{message}".encode("utf-8")

            # Gửi email
            server.sendmail(SENDER_EMAIL, recipient, email_message)
            server.quit() # Đóng kết nối máy chủ
            messagebox.showinfo("Thành công", "Email đã được gửi!")
            # Tùy chọn: Xóa nội dung đã nhập sau khi gửi thành công
            recipient_entry.delete(0, tk.END)
            subject_entry.delete(0, tk.END)
            message_text.delete('1.0', tk.END)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể gửi email: {e}\n\nVui lòng kiểm tra lại:\n- Kết nối internet\n- Địa chỉ email người nhận\n- Mật khẩu ứng dụng (App Password) của tài khoản Gmail của bạn (nếu chưa bật, hãy tìm kiếm 'App passwords Google' để tạo).\n- Bạn đã bật 'Less secure app access' (truy cập ứng dụng kém an toàn) cho tài khoản Gmail của mình (đây là cách cũ và không được khuyến khích, nên dùng App Password).")

    # Tạo cửa sổ Toplevel (cửa sổ con)
        if not root: # 2 Dòng này nhằm đảm bảo cảu sổ chính tồn tại 
            return
    # Tạo cửa sổ phụ cho tính năng 11     
    tinh_nang_3 = tk.Toplevel(root) # liên kết với của sổ chính bằng root
    tinh_nang_3.title("3. Gửi thư") # Thiết lập tên cho cửa sổ
    tinh_nang_3.grid() # Thiết lập kích thước
    # Đoạn này dùng để thay đổi giao diện 
    style = ThemedStyle(tinh_nang_3)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_3.config(bg=theme_bg_color)
    

    # Tạo và đặt các nhãn và ô nhập liệu
    ttk.Label(tinh_nang_3, text="Người gửi:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    ttk.Label(tinh_nang_3, text=SENDER_EMAIL).grid(row=0, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(tinh_nang_3, text="Người nhận:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    recipient_entry =tk.Entry(tinh_nang_3, width=40)
    recipient_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    recipient_entry.config(bg=theme_bg_color) # Đặt màu nền cho ô nhập liệu

    ttk.Label(tinh_nang_3, text="Chủ đề:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    subject_entry = tk.Entry(tinh_nang_3, width=40)
    subject_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    subject_entry.config(bg=theme_bg_color) # Đặt màu nền cho ô nhập liệu

    ttk.Label(tinh_nang_3, text="Nội dung:").grid(row=3, column=0, padx=5, pady=5, sticky="nw") # sticky="nw" để nhãn ở góc trên bên trái
    message_text = tk.Text(tinh_nang_3, height=10, width=50)
    message_text.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")
    message_text.config(bg=theme_bg_color) # Đặt màu nền cho Text widget

    # Thêm nút Gửi
    ttk.Button(tinh_nang_3, text="Gửi", command=send_email).grid(row=4, column=1, padx=5, pady=10, sticky="ew")

    # Cấu hình để các widget co giãn khi cửa sổ thay đổi kích thước
    tinh_nang_3.grid_rowconfigure(3, weight=1)
    tinh_nang_3.grid_columnconfigure(1, weight=1)
###################################################################################
def may_tinh(): # Tính năng 4: Máy tính

    tinh_nang_4 = tk.Toplevel(root) # liên kết với của sổ chính bằng root
    tinh_nang_4.title("4. MÁy tính ") # Thiết lập tên cho cửa sổ
    tinh_nang_4.resizable(False, False) # Loại bỏ khả năng thu phóng cảu cửa sổ
    # Đoạn này dùng để thay đổi giao diện 
    style = ThemedStyle(tinh_nang_4)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_4.config(bg=theme_bg_color)

    expression = ""  # Biến này để lưu trữ biểu thức hiện tại
    history = []     # Biến để lưu trữ lịch sử tính toán

    # Hàm cập nhật ô nhập liệu
    def update_entry(value):
        nonlocal expression
        expression += str(value)
        entry.delete(0, END)
        entry.insert(0, expression)

    # Hàm xóa toàn bộ ô nhập liệu
    def clear_entry():
        nonlocal expression
        expression = ""
        entry.delete(0, END)

    # Hàm tính toán kết quả
    def calculate_result():
        nonlocal expression, history
        try:
            # Thay thế các ký hiệu toán học với người dùng thành toán tử Python
            eval_expression = expression.replace("x", "*").replace(":", "/").replace(",", ".")
            # Đánh giá biểu thức
            result = str(eval(eval_expression))
            entry.delete(0, tk.END)
            entry.insert(0, result)
            history.append(f"{expression} = {result}") # Thêm vào lịch sử
            update_history_display() # Cập nhật hiển thị lịch sử
            expression = result  # Lưu kết quả để có thể tiếp tục tính toán
        except Exception as e:
            # Hiển thị thông báo lỗi
            messagebox.showerror("Lỗi", "Biểu thức không hợp lệ hoặc lỗi: " + str(e))
            expression = ""  # Đặt lại biểu thức khi có lỗi

    # Hàm xóa ký tự cuối cùng
    def delete_last_char():
        nonlocal expression
        expression = expression[:-1]  # Cắt bỏ ký tự cuối cùng
        entry.delete(0, tk.END)
        entry.insert(0, expression)

    # Hàm cập nhật hiển thị lịch sử
    def update_history_display():
        history_text.config(state=tk.NORMAL)
        history_text.delete(1.0, tk.END)
        for item in history:
            history_text.insert(tk.END, item + "\n")
        history_text.config(state=tk.DISABLED)

    # --- Các hàm chuyển đổi đơn vị ---
    # Ánh xạ từ tên đơn vị sang ký hiệu để hiển thị
    unit_symbols = {
        "mét": "m", "kilômét": "km", "centimét": "cm", "milimét": "mm",
        "inch": "in", "feet": "ft", "yard": "yd",
        "kilôgam": "kg", "gram": "g", "miligam": "mg", "pound": "lb", "ounce": "oz",
        "Celsius": "°C", "Fahrenheit": "°F", "Kelvin": "K"
    }

    def convert_length():
        try:
            value = float(length_input.get())
            unit_from_name = length_unit_from.get()
            unit_to_name = length_unit_to.get()

            # Chuyển đổi về mét
            if unit_from_name == "mét":
                base_value = value
            elif unit_from_name == "kilômét":
                base_value = value * 1000
            elif unit_from_name == "centimét":
                base_value = value / 100
            elif unit_from_name == "milimét":
                base_value = value / 1000
            elif unit_from_name == "inch":
                base_value = value * 0.0254
            elif unit_from_name == "feet":
                base_value = value * 0.3048
            elif unit_from_name == "yard":
                base_value = value * 0.9144
            else:
                base_value = value # fallback

            # Chuyển đổi từ mét sang đơn vị đích
            if unit_to_name == "mét":
                result = base_value
            elif unit_to_name == "kilômét":
                result = base_value / 1000
            elif unit_to_name == "centimét":
                result = base_value * 100
            elif unit_to_name == "milimét":
                result = base_value * 1000
            elif unit_to_name == "inch":
                result = base_value / 0.0254
            elif unit_to_name == "feet":
                result = base_value / 0.3048
            elif unit_to_name == "yard":
                result = base_value / 0.9144
            else:
                result = base_value # fallback


            length_result_label.config(text=f"Kết quả: {result:.4f} {unit_symbols.get(unit_to_name, unit_to_name)}")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị số hợp lệ cho chiều dài.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def convert_mass():
        try:
            value = float(mass_input.get())
            unit_from_name = mass_unit_from.get()
            unit_to_name = mass_unit_to.get()

            # Chuyển đổi về kilogram
            if unit_from_name == "kilôgam":
                base_value = value
            elif unit_from_name == "gram":
                base_value = value / 1000
            elif unit_from_name == "miligam":
                base_value = value / 1_000_000
            elif unit_from_name == "pound":
                base_value = value * 0.453592
            elif unit_from_name == "ounce":
                base_value = value * 0.0283495
            else:
                base_value = value

            # Chuyển đổi từ kilogram sang đơn vị đích
            if unit_to_name == "kilôgam":
                result = base_value
            elif unit_to_name == "gram":
                result = base_value * 1000
            elif unit_to_name == "miligam":
                result = base_value * 1_000_000
            elif unit_to_name == "pound":
                result = base_value / 0.453592
            elif unit_to_name == "ounce":
                result = base_value / 0.0283495
            else:
                result = base_value

            mass_result_label.config(text=f"Kết quả: {result:.4f} {unit_symbols.get(unit_to_name, unit_to_name)}")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị số hợp lệ cho khối lượng.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    def convert_temperature():
        try:
            value = float(temp_input.get())
            unit_from_name = temp_unit_from.get()
            unit_to_name = temp_unit_to.get()

            # Chuyển đổi về độ C
            if unit_from_name == "Celsius":
                base_value = value
            elif unit_from_name == "Fahrenheit":
                base_value = (value - 32) * 5/9
            elif unit_from_name == "Kelvin":
                base_value = value - 273.15
            else:
                base_value = value

            # Chuyển đổi từ độ C sang đơn vị đích
            if unit_to_name == "Celsius":
                result = base_value
            elif unit_to_name == "Fahrenheit":
                result = (base_value * 9/5) + 32
            elif unit_to_name == "Kelvin":
                result = base_value + 273.15
            else:
                result = base_value

            temp_result_label.config(text=f"Kết quả: {result:.2f} {unit_symbols.get(unit_to_name, unit_to_name)}")
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị số hợp lệ cho nhiệt độ.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")

    # --- Hàm tính điện trở từ vòng màu ---
    def calculate_resistor():
        colors = {
            "Đen": 0, "Nâu": 1, "Đỏ": 2, "Cam": 3, "Vàng": 4,
            "Lục": 5, "Lam": 6, "Tím": 7, "Xám": 8, "Trắng": 9
        }
        multiplier_colors = {
            "Đen": 1, "Nâu": 10, "Đỏ": 100, "Cam": 1000, "Vàng": 10000,
            "Lục": 100000, "Lam": 1000000, "Tím": 10000000,
            "Vàng kim": 0.1, "Bạc": 0.01
        }
        tolerance_values = { # Sử dụng giá trị trực tiếp để tránh lỗi làm tròn
            "Nâu": 1, "Đỏ": 2, "Lục": 0.5, "Lam": 0.25,
            "Tím": 0.1, "Xám": 0.05, "Vàng kim": 5, "Bạc": 10
        }

        try:
            band1 = resistor_band1.get()
            band2 = resistor_band2.get()
            multiplier_band = resistor_multiplier.get()
            tolerance_band = resistor_tolerance.get()

            num_bands = resistor_bands_var.get()

            value_band1 = colors[band1]
            value_band2 = colors[band2]

            if num_bands == 4: # Điện trở 4 vòng
                multiplier = multiplier_colors[multiplier_band]
                tolerance_percent = tolerance_values[tolerance_band] # Lấy giá trị phần trăm trực tiếp

                resistance = (value_band1 * 10 + value_band2) * multiplier
                resistor_result_label.config(text=f"Điện trở: {resistance:.2f} Ω ± {tolerance_percent:.2f}%")

            elif num_bands == 5: # Điện trở 5 vòng
                band3 = resistor_band3_dropdown.get() # Lấy giá trị từ dropdown
                value_band3 = colors[band3]
                multiplier = multiplier_colors[multiplier_band]
                tolerance_percent = tolerance_values[tolerance_band] # Lấy giá trị phần trăm trực tiếp

                resistance = (value_band1 * 100 + value_band2 * 10 + value_band3) * multiplier
                resistor_result_label.config(text=f"Điện trở: {resistance:.2f} Ω ± {tolerance_percent:.2f}%")
            else:
                messagebox.showerror("Lỗi", "Vui lòng chọn số vòng (4 hoặc 5).")

        except KeyError as e:
            messagebox.showerror("Lỗi", f"Màu không hợp lệ: {e}. Vui lòng chọn màu từ danh sách.")
        except Exception as e:
            messagebox.showerror("Lỗi", "Có lỗi xảy ra khi tính điện trở: " + str(e))

    def update_resistor_bands_display(*args):
        num_bands = resistor_bands_var.get()
        # Ẩn/hiện vòng 3
        if num_bands == 4:
            resistor_band3_label.grid_forget()
            resistor_band3_dropdown.grid_forget()
            # Di chuyển các thành phần dưới lên
            resistor_multiplier_label.grid(row=2, column=0, padx=5, pady=5, sticky=W)
            resistor_multiplier.grid(row=2, column=1, padx=5, pady=5, sticky=(W, E))
            resistor_tolerance_label.grid(row=3, column=0, padx=5, pady=5, sticky=W)
            resistor_tolerance.grid(row=3, column=1, padx=5, pady=5, sticky=(W, E))
        elif num_bands == 5:
            resistor_band3_label.grid(row=2, column=0, padx=5, pady=5, sticky=W) # Vòng 3 ở hàng 2
            resistor_band3_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky=(W, E))
            # Di chuyển các thành phần dưới xuống
            resistor_multiplier_label.grid(row=3, column=0, padx=5, pady=5, sticky=W) # Vòng nhân ở hàng 3
            resistor_multiplier.grid(row=3, column=1, padx=5, pady=5, sticky=(W, E))
            resistor_tolerance_label.grid(row=4, column=0, padx=5, pady=5, sticky=W) # Vòng dung sai ở hàng 4
            resistor_tolerance.grid(row=4, column=1, padx=5, pady=5, sticky=(W, E))


    # --- Giao diện người dùng ---
    # Notebook (Tabbed interface)
    notebook = ttk.Notebook(tinh_nang_4)
    notebook.grid(row=0, column=0, sticky=(N, W, E, S))
    tinh_nang_4.grid_columnconfigure(0, weight=1)
    tinh_nang_4.grid_rowconfigure(0, weight=1)

    # --- Tab 1: Máy tính cơ bản ---
    calc_frame = ttk.Frame(notebook, padding="10 10 10 10")
    notebook.add(calc_frame, text="Máy tính")

    # Chia calc_frame thành 2 cột chính: Lịch sử và Máy tính
    calc_frame.grid_columnconfigure(0, weight=1) # Cột lịch sử
    calc_frame.grid_columnconfigure(1, weight=2) # Cột máy tính (rộng hơn)
    for i in range(6): # Các hàng trong cột máy tính
        calc_frame.grid_rowconfigure(i, weight=1)


    # Lịch sử tính toán (Cột 0)
    history_frame = ttk.LabelFrame(calc_frame, text="Lịch sử tính toán", padding="10 10 10 10")
    history_frame.grid(row=0, column=0, rowspan=6, padx=10, pady=5, sticky=(N, S, W, E))
    history_frame.grid_rowconfigure(0, weight=1)
    history_frame.grid_columnconfigure(0, weight=1)

    history_text = tk.Text(history_frame, width=25, height=15, state=tk.DISABLED, wrap=tk.WORD, font=('Arial', 10))
    history_text.grid(row=0, column=0, sticky=(N, S, W, E))


    # Khung chứa các thành phần máy tính (Ô nhập liệu và các nút) (Cột 1)
    calculator_buttons_frame = ttk.Frame(calc_frame, padding="10 10 10 10")
    calculator_buttons_frame.grid(row=0, column=1, rowspan=6, padx=10, pady=5, sticky=(N, S, W, E))

    # Cấu hình grid cho calculator_buttons_frame
    calculator_buttons_frame.grid_columnconfigure(0, weight=1)
    calculator_buttons_frame.grid_columnconfigure(1, weight=1)
    calculator_buttons_frame.grid_columnconfigure(2, weight=1)
    calculator_buttons_frame.grid_columnconfigure(3, weight=1)
    calculator_buttons_frame.grid_columnconfigure(4, weight=1) # Cho nút Xóa
    for i in range(6): # 6 hàng (entry + 5 hàng nút)
        calculator_buttons_frame.grid_rowconfigure(i, weight=1)


    # Ô nhập liệu hiển thị biểu thức và kết quả
    entry = Entry(calculator_buttons_frame, font=('Arial', 18), justify='right') # Tăng font cho dễ nhìn
    entry.grid(row=0, column=0, columnspan=5, pady=10, ipadx=5, ipady=5, sticky=(W,E))
    entry.config(bg=theme_bg_color) # Đặt màu nền cho ô nhập liệu

    # Định nghĩa style cho các nút (font và padding)
    button_style = ttk.Style()
    button_style.configure("TButton", font=('Arial', 12), padding=20) # Tăng font và padding mặc định
    # Nút lớn hơn cho "0"
    button_style.configure("Wide.TButton", font=('Arial', 12), padding=(20, 10)) # padding ngang lớn hơn


    # Các nút hàng 1
    ttk.Button(calculator_buttons_frame, text="AC", command=clear_entry, style="TButton").grid(column=0, row=1, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="(", command=lambda: update_entry("("), style="TButton").grid(column=1, row=1, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text=")", command=lambda: update_entry(")"), style="TButton").grid(column=2, row=1, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text=":", command=lambda: update_entry(":"), style="TButton").grid(column=3, row=1, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="Xóa", command=delete_last_char, style="TButton").grid(column=4, row=1, padx=1, pady=1, sticky=(W,E))

    # Các nút hàng 2
    ttk.Button(calculator_buttons_frame, text="7", command=lambda: update_entry("7"), style="TButton").grid(column=0, row=2, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="8", command=lambda: update_entry("8"), style="TButton").grid(column=1, row=2, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="9", command=lambda: update_entry("9"), style="TButton").grid(column=2, row=2, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="x", command=lambda: update_entry("x"), style="TButton").grid(column=3, row=2, padx=1, pady=1, sticky=(W,E))

    # Các nút hàng 3
    ttk.Button(calculator_buttons_frame, text="4", command=lambda: update_entry("4"), style="TButton").grid(column=0, row=3, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="5", command=lambda: update_entry("5"), style="TButton").grid(column=1, row=3, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="6", command=lambda: update_entry("6"), style="TButton").grid(column=2, row=3, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="-", command=lambda: update_entry("-"), style="TButton").grid(column=3, row=3, padx=1, pady=1, sticky=(W,E))

    # Các nút hàng 4
    ttk.Button(calculator_buttons_frame, text="1", command=lambda: update_entry("1"), style="TButton").grid(column=0, row=4, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="2", command=lambda: update_entry("2"), style="TButton").grid(column=1, row=4, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="3", command=lambda: update_entry("3"), style="TButton").grid(column=2, row=4, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="+", command=lambda: update_entry("+"), style="TButton").grid(column=3, row=4, padx=1, pady=1, sticky=(W,E))

    # Các nút hàng 5
    ttk.Button(calculator_buttons_frame, text="0", command=lambda: update_entry("0"), style="Wide.TButton").grid(column=0, row=5, columnspan=2, padx=1, pady=1, sticky=(W,E)) # Nút 0 dùng style riêng
    ttk.Button(calculator_buttons_frame, text=".", command=lambda: update_entry("."), style="TButton").grid(column=2, row=5, padx=1, pady=1, sticky=(W,E))
    ttk.Button(calculator_buttons_frame, text="=", command=calculate_result, style="TButton").grid(column=3, row=5, padx=1, pady=1, sticky=(W,E))


    # --- Tab 2: Chuyển đổi đơn vị ---
    unit_convert_frame = ttk.Frame(notebook, padding="10 10 10 10")
    notebook.add(unit_convert_frame, text="Đổi đơn vị")

    # Cấu hình cột cho unit_convert_frame để các LabelFrame có thể căng ngang
    unit_convert_frame.grid_columnconfigure(0, weight=1)

    # Khai báo các danh sách đơn vị với ký hiệu hoặc tên đầy đủ để hiển thị trong Combobox
    # Danh sách hiển thị cho người dùng (có thể là tên đầy đủ)
    length_units_display = ["m", "km", "cm", "mn", "inch", "feet", "yard"]
    mass_units_display = ["kg", "g", "mg", "pound", "ounce"]
    temp_units_display = ["C", "F", "K"]

    # Frame cho chuyển đổi chiều dài
    length_frame = ttk.LabelFrame(unit_convert_frame, text="Chuyển đổi chiều dài", padding="10 10 10 10")
    length_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(N, W, E, S))
    length_frame.grid_columnconfigure(1, weight=1) # Cột 1 (input/combobox) căng ngang
    

    ttk.Label(length_frame, text="Giá trị:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
    length_input = ttk.Entry(length_frame, width=20)
    length_input.grid(row=0, column=1, padx=5, pady=5, sticky=(W, E))
    

    ttk.Label(length_frame, text="Từ:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
    length_unit_from = ttk.Combobox(length_frame, values=length_units_display, state="readonly")
    length_unit_from.set("m")
    length_unit_from.grid(row=1, column=1, padx=5, pady=5, sticky=(W, E))


    ttk.Label(length_frame, text="Sang:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
    length_unit_to = ttk.Combobox(length_frame, values=length_units_display, state="readonly")
    length_unit_to.set("cm")
    length_unit_to.grid(row=2, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Button(length_frame, text="Chuyển đổi", command=convert_length).grid(row=3, column=0, columnspan=2, pady=10)
    length_result_label = ttk.Label(length_frame, text="Kết quả:")
    length_result_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=W)


    # Frame cho chuyển đổi khối lượng
    mass_frame = ttk.LabelFrame(unit_convert_frame, text="Chuyển đổi khối lượng", padding="10 10 10 10")
    mass_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(N, W, E, S))
    mass_frame.grid_columnconfigure(1, weight=1)

    ttk.Label(mass_frame, text="Giá trị:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
    mass_input = ttk.Entry(mass_frame, width=20)
    mass_input.grid(row=0, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(mass_frame, text="Từ:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
    mass_unit_from = ttk.Combobox(mass_frame, values=mass_units_display, state="readonly")
    mass_unit_from.set("kg")
    mass_unit_from.grid(row=1, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(mass_frame, text="Sang:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
    mass_unit_to = ttk.Combobox(mass_frame, values=mass_units_display, state="readonly")
    mass_unit_to.set("g")
    mass_unit_to.grid(row=2, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Button(mass_frame, text="Chuyển đổi", command=convert_mass).grid(row=3, column=0, columnspan=2, pady=10)
    mass_result_label = ttk.Label(mass_frame, text="Kết quả:")
    mass_result_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=W)


    # Frame cho chuyển đổi nhiệt độ
    temp_frame = ttk.LabelFrame(unit_convert_frame, text="Chuyển đổi nhiệt độ", padding="10 10 10 10")
    temp_frame.grid(row=2, column=0, padx=5, pady=5, sticky=(N, W, E, S))
    temp_frame.grid_columnconfigure(1, weight=1)

    ttk.Label(temp_frame, text="Giá trị:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
    temp_input = ttk.Entry(temp_frame, width=20)
    temp_input.grid(row=0, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(temp_frame, text="Từ:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
    temp_unit_from = ttk.Combobox(temp_frame, values=temp_units_display, state="readonly")
    temp_unit_from.set("C")
    temp_unit_from.grid(row=1, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(temp_frame, text="Sang:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
    temp_unit_to = ttk.Combobox(temp_frame, values=temp_units_display, state="readonly")
    temp_unit_to.set("F")
    temp_unit_to.grid(row=2, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Button(temp_frame, text="Chuyển đổi", command=convert_temperature).grid(row=3, column=0, columnspan=2, pady=10)
    temp_result_label = ttk.Label(temp_frame, text="Kết quả:")
    temp_result_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky=W)


    # --- Tab 3: Tính điện trở ---
    resistor_frame = ttk.Frame(notebook, padding="10 10 10 10")
    notebook.add(resistor_frame, text="Tính điện trở")

    # Cấu hình cột cho resistor_frame
    resistor_frame.grid_columnconfigure(0, weight=1) # Cột cho các frame con
    resistor_frame.grid_columnconfigure(1, weight=1) # Có thể thêm cột nếu muốn chia đôi

    resistor_color_options = [
        "Đen", "Nâu", "Đỏ", "Cam", "Vàng", "Lục", "Lam", "Tím", "Xám", "Trắng"
    ]
    multiplier_color_options = [
        "Đen", "Nâu", "Đỏ", "Cam", "Vàng", "Lục", "Lam", "Tím", "Vàng kim", "Bạc"
    ]
    tolerance_color_options = [
        "Nâu", "Đỏ", "Lục", "Lam", "Tím", "Xám", "Vàng kim", "Bạc"
    ]

    # Frame cho phần chọn số vòng
    bands_selection_frame = ttk.LabelFrame(resistor_frame, text="Chọn số vòng", padding="10 10 10 10")
    bands_selection_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=(W, E))
    bands_selection_frame.grid_columnconfigure(0, weight=1)
    bands_selection_frame.grid_columnconfigure(1, weight=1)

    resistor_bands_var = tk.IntVar(value=4)
    resistor_bands_var.trace_add("write", update_resistor_bands_display)
    ttk.Radiobutton(bands_selection_frame, text="4 Vòng", variable=resistor_bands_var, value=4).grid(row=0, column=0, padx=5, pady=5, sticky=W)
    ttk.Radiobutton(bands_selection_frame, text="5 Vòng", variable=resistor_bands_var, value=5).grid(row=0, column=1, padx=5, pady=5, sticky=W)

    # Frame cho các vòng màu
    bands_input_frame = ttk.LabelFrame(resistor_frame, text="Chọn màu vòng", padding="10 10 10 10")
    bands_input_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=(W, E))
    bands_input_frame.grid_columnconfigure(1, weight=1) # Cột 1 (combobox) căng ngang

    ttk.Label(bands_input_frame, text="Vòng 1 (Chữ số 1):").grid(row=0, column=0, padx=5, pady=5, sticky=W)
    resistor_band1 = ttk.Combobox(bands_input_frame, values=resistor_color_options, state="readonly")
    resistor_band1.set("Nâu") # Giá trị mặc định phổ biến
    resistor_band1.grid(row=0, column=1, padx=5, pady=5, sticky=(W, E))

    ttk.Label(bands_input_frame, text="Vòng 2 (Chữ số 2):").grid(row=1, column=0, padx=5, pady=5, sticky=W)
    resistor_band2 = ttk.Combobox(bands_input_frame, values=resistor_color_options, state="readonly")
    resistor_band2.set("Đen") # Giá trị mặc định phổ biến
    resistor_band2.grid(row=1, column=1, padx=5, pady=5, sticky=(W, E))

    # Vòng 3 (chỉ hiển thị khi chọn 5 vòng) - Định nghĩa ở đây để có thể truy cập
    resistor_band3_label = ttk.Label(bands_input_frame, text="Vòng 3 (Chữ số 3):")
    resistor_band3_dropdown = ttk.Combobox(bands_input_frame, values=resistor_color_options, state="readonly")
    resistor_band3_dropdown.set("Đen")

    resistor_multiplier_label = ttk.Label(bands_input_frame, text="Vòng nhân:")
    resistor_multiplier = ttk.Combobox(bands_input_frame, values=multiplier_color_options, state="readonly")
    resistor_multiplier.set("Đỏ") # Giá trị mặc định phổ biến (x100)

    resistor_tolerance_label = ttk.Label(bands_input_frame, text="Vòng dung sai:")
    resistor_tolerance = ttk.Combobox(bands_input_frame, values=tolerance_color_options, state="readonly")
    resistor_tolerance.set("Vàng kim") # Giá trị mặc định phổ biến (±5%)


    # Frame cho kết quả và nút tính
    result_resistor_frame = ttk.LabelFrame(resistor_frame, text="Kết quả", padding="10 10 10 10")
    result_resistor_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=(W, E))
    result_resistor_frame.grid_columnconfigure(0, weight=1)
    result_resistor_frame.grid_columnconfigure(1, weight=1)

    calculate_resistor_button = ttk.Button(result_resistor_frame, text="Tính toán điện trở", command=calculate_resistor)
    calculate_resistor_button.grid(row=0, column=0, columnspan=2, pady=5)
    resistor_result_label = ttk.Label(result_resistor_frame, text="Điện trở:")
    resistor_result_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=W)

    # Cập nhật hiển thị vòng 3 ban đầu (nếu là 4 vòng)
    update_resistor_bands_display()
###################################################################################
wiki_page_url = None 
def tim_kiem_thong_tin(): # Tính năng 6: Tìm kiếm thông tin (wikipedia)
    global wiki_page_url 
    if not root:
        return

    wiki_wiki = wikipediaapi.Wikipedia(user_agent="MyWikipediaApp (your-email@example.com)", language="vi", extract_format=wikipediaapi.ExtractFormat.WIKI)

    def lay_thong_tin():
        global wiki_page_url 
        noi_dung_tim_kiem = o_nhap.get().strip()
        wiki_page_url = None 
        nut_mo_link.config(state=tk.DISABLED) 

        if not noi_dung_tim_kiem:
            o_ket_qua.config(state=tk.NORMAL)
            o_ket_qua.delete(1.0, tk.END)
            o_ket_qua.insert(tk.END, "Vui lòng nhập từ khóa tìm kiếm.")
            o_ket_qua.config(state=tk.DISABLED)
            return

        def tra_cuu():
            global wiki_page_url 
            o_ket_qua.config(state=tk.NORMAL)
            o_ket_qua.delete(1.0, tk.END)
            o_ket_qua.insert(tk.END, "Đang tìm kiếm...")
            o_ket_qua.config(state=tk.DISABLED)

            try:
                page_py = wiki_wiki.page(noi_dung_tim_kiem)

                if page_py.exists():
                    full_content = []
                    wiki_page_url = page_py.fullurl
                    nut_mo_link.config(state=tk.NORMAL) 
                    # Thêm tóm tắt chính trước
                    if page_py.summary:
                        full_content.append("--- Tóm tắt ---")
                        full_content.append(page_py.summary)
                        full_content.append("\n") # Thêm dòng trống cho dễ nhìn
                    # Duyệt qua các phần (sections)
                    for s in page_py.sections:
                        if s.level == 1: # Hoặc s.level <= 2 để lấy 2 cấp đầu tiên
                            full_content.append(f"--- {s.title} ---")
                            full_content.append(s.text)
                            full_content.append("\n")

                    display_text = "\n".join(full_content)

                    if not display_text.strip(): # Trường hợp không có summary hoặc sections
                        display_text = "Không tìm thấy nội dung chi tiết cho từ khóa này."


                    o_ket_qua.config(state=tk.NORMAL)
                    o_ket_qua.delete(1.0, tk.END)
                    o_ket_qua.insert(tk.END, display_text)
                    o_ket_qua.config(state=tk.DISABLED)

                else:
                    wiki_page_url = None # Reset URL if page not found
                    nut_mo_link.config(state=tk.DISABLED) # Disable the button
                    o_ket_qua.config(state=tk.NORMAL)
                    o_ket_qua.delete(1.0, tk.END)
                    o_ket_qua.insert(tk.END, f"Rất tiếc, tôi không tìm thấy thông tin về '{noi_dung_tim_kiem}'. Vui lòng thử từ khóa khác.")
                    o_ket_qua.config(state=tk.DISABLED)

            except Exception as e:
                wiki_page_url = None # Reset URL on error
                nut_mo_link.config(state=tk.DISABLED) # Disable the button
                o_ket_qua.config(state=tk.NORMAL)
                o_ket_qua.delete(1.0, tk.END)
                o_ket_qua.insert(tk.END, f"Đã xảy ra lỗi: {e}")
                o_ket_qua.config(state=tk.DISABLED)

        threading.Thread(target=tra_cuu).start()

    # Function to open the Wikipedia page URL
    def mo_trang_wiki():
        if wiki_page_url:
            webbrowser.open(wiki_page_url)
        else:
            # Optionally, you can add a message box here if no URL is available
            pass

    tinh_nang_6 = tk.Toplevel(root)
    tinh_nang_6.title("6. Tìm kiếm thông tin trên Wikipedia")
    tinh_nang_6.geometry("600x400")

    style = ThemedStyle(tinh_nang_6)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_6.config(bg=theme_bg_color)

    tinh_nang_6.grid_columnconfigure(0, weight=1)
    tinh_nang_6.grid_rowconfigure(2, weight=1)

    nhan_huong_dan = ttk.Label(tinh_nang_6, text="Nhập nội dung bạn muốn tìm hiểu:")
    nhan_huong_dan.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    o_nhap = ttk.Entry(tinh_nang_6, width=50)
    o_nhap.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    o_nhap.bind("<Return>", lambda event=None: lay_thong_tin())

    button_frame = ttk.Frame(tinh_nang_6)
    button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="e")
    button_frame.columnconfigure(0, weight=1) # Allow button frame to expand

    nut_tim_kiem = ttk.Button(button_frame, text="Tìm kiếm", command=lay_thong_tin)
    nut_tim_kiem.pack(side=tk.LEFT, padx=(0, 5))

    nut_mo_link = ttk.Button(button_frame, text="Mở trang Wikipedia", command=mo_trang_wiki, state=tk.DISABLED)
    nut_mo_link.pack(side=tk.LEFT)

    o_ket_qua = scrolledtext.ScrolledText(tinh_nang_6, wrap=tk.WORD, width=70, height=15)
    o_ket_qua.config(bg=theme_bg_color, state=tk.DISABLED)
    o_ket_qua.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
###################################################################################
FONT_DEFAULT = ("Arial", 10)
FONT_TIME_DISPLAY = ("Arial", 24, "bold")
FONT_TITLE = ("Arial", 14, "bold")

countdown_is_running = False
countdown_thread = None
countdown_initial_time = 3600
countdown_current_time = countdown_initial_time

stopwatch_is_running = False
stopwatch_elapsed_time = 0
stopwatch_thread = None

pomodoro_is_running = False
pomodoro_current_phase = "work"
pomodoro_thread = None

countdown_display = None
countdown_hr_spinbox = None
countdown_min_spinbox = None
countdown_sec_spinbox = None

countdown_hr_var = None
countdown_min_var = None
countdown_sec_var = None

start_countdown_button = None
stop_countdown_button = None
reset_countdown_button = None

stopwatch_display = None
start_stopwatch_button = None
stop_stopwatch_button = None
reset_stopwatch_button = None

pomodoro_status = None
pomodoro_display = None
start_pomodoro_button = None
stop_pomodoro_button = None
reset_pomodoro_button = None

def get_countdown_initial_seconds_from_spinboxes():
    try:
        hours = countdown_hr_var.get()
        minutes = countdown_min_var.get()
        seconds = countdown_sec_var.get()
        return hours * 3600 + minutes * 60 + seconds
    except ValueError:
        messagebox.showerror("Lỗi", "Giá trị thời gian không hợp lệ. Vui lòng nhập số nguyên.")
        return 0
def update_countdown_set_spinboxes():
    global countdown_initial_time
    h, remainder = divmod(countdown_initial_time, 3600)
    m, s = divmod(remainder, 60)
    if countdown_hr_var:
        countdown_hr_var.set(h)
    if countdown_min_var:
        countdown_min_var.set(m)
    if countdown_sec_var:
        countdown_sec_var.set(s)
def create_time_input_spinbox(parent_frame, label_text, var_obj, column_start):
    ttk.Label(parent_frame, text=label_text, font=FONT_DEFAULT).grid(row=0, column=column_start, padx=(0,2))
    spinbox = ttk.Spinbox(parent_frame, from_=0, to=59, width=3, font=FONT_DEFAULT, justify="center", textvariable=var_obj)
    spinbox.grid(row=0, column=column_start + 1, padx=(0,5))
    return spinbox
def create_control_button(parent_frame, text, command, state=tk.NORMAL, column=0):
    button = ttk.Button(parent_frame, text=text, command=command, state=state) # Removed font=FONT_DEFAULT
    button.grid(row=0, column=column, padx=5, pady=5)
    return button
def start_countdown():
    global countdown_is_running, countdown_thread, countdown_current_time, countdown_initial_time, \
           start_countdown_button, stop_countdown_button, reset_countdown_button, \
           countdown_hr_spinbox, countdown_min_spinbox, countdown_sec_spinbox

    if not countdown_is_running:
        if countdown_current_time == countdown_initial_time or countdown_current_time <= 0:
            countdown_initial_time = get_countdown_initial_seconds_from_spinboxes()
            countdown_current_time = countdown_initial_time

        t = countdown_current_time
        if t <= 0:
            messagebox.showerror("Lỗi", "Thời gian đếm ngược phải là một giá trị dương.")
            return

        countdown_is_running = True
        start_countdown_button.config(state=tk.DISABLED)
        stop_countdown_button.config(state=tk.NORMAL)
        reset_countdown_button.config(state=tk.NORMAL)
        countdown_hr_spinbox.config(state=tk.DISABLED)
        countdown_min_spinbox.config(state=tk.DISABLED)
        countdown_sec_spinbox.config(state=tk.DISABLED)

        countdown_thread = threading.Thread(target=_run_countdown, args=(t,), daemon=True)
        countdown_thread.start()
def _run_countdown(t):
    global countdown_is_running, countdown_current_time, countdown_display, root
    while t >= 0 and countdown_is_running:
        h, remainder = divmod(t, 3600)
        m, s = divmod(remainder, 60)
        countdown_display.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        root.update_idletasks()
        time.sleep(1)
        t -= 1

    countdown_current_time = t

    if not countdown_is_running and countdown_current_time < 0:
        messagebox.showinfo("Hoàn thành", "Đếm ngược đã kết thúc!")
        stop_countdown(final_reset=True)
    elif countdown_is_running and countdown_current_time < 0:
        messagebox.showinfo("Hoàn thành", "Đếm ngược đã kết thúc!")
        stop_countdown(final_reset=True)
def stop_countdown(final_reset=False):
    global countdown_is_running, start_countdown_button, stop_countdown_button, \
           countdown_display, countdown_hr_spinbox, countdown_min_spinbox, countdown_sec_spinbox, \
           countdown_current_time

    countdown_is_running = False
    start_countdown_button.config(state=tk.NORMAL)
    stop_countdown_button.config(state=tk.DISABLED)

    if final_reset:
        countdown_display.config(text="00:00:00")
        countdown_hr_spinbox.config(state=tk.NORMAL)
        countdown_min_spinbox.config(state=tk.NORMAL)
        countdown_sec_spinbox.config(state=tk.NORMAL)
        countdown_current_time = get_countdown_initial_seconds_from_spinboxes()
def reset_countdown():
    global countdown_initial_time, countdown_current_time, \
           countdown_display, reset_countdown_button
    stop_countdown(final_reset=True)
    countdown_current_time = countdown_initial_time
    update_countdown_set_spinboxes()
    h, remainder = divmod(countdown_initial_time, 3600)
    m, s = divmod(remainder, 60)
    countdown_display.config(text=f"{h:02d}:{m:02d}:{s:02d}")
    reset_countdown_button.config(state=tk.DISABLED)
def start_stopwatch():
    global stopwatch_is_running, stopwatch_thread, start_stopwatch_button, \
           stop_stopwatch_button, reset_stopwatch_button
    if not stopwatch_is_running:
        stopwatch_is_running = True
        start_stopwatch_button.config(state=tk.DISABLED)
        stop_stopwatch_button.config(state=tk.NORMAL)
        reset_stopwatch_button.config(state=tk.NORMAL)
        stopwatch_thread = threading.Thread(target=_run_stopwatch, daemon=True)
        stopwatch_thread.start()
def _run_stopwatch():
    global stopwatch_is_running, stopwatch_elapsed_time, stopwatch_display, root
    while stopwatch_is_running:
        h, r = divmod(stopwatch_elapsed_time, 3600)
        m, s = divmod(r, 60)
        stopwatch_display.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        root.update_idletasks()
        time.sleep(1)
        stopwatch_elapsed_time += 1
def stop_stopwatch():
    global stopwatch_is_running, start_stopwatch_button, stop_stopwatch_button
    stopwatch_is_running = False
    start_stopwatch_button.config(state=tk.NORMAL)
    stop_stopwatch_button.config(state=tk.DISABLED)
def reset_stopwatch():
    global stopwatch_elapsed_time, stopwatch_display, reset_stopwatch_button
    stop_stopwatch()
    stopwatch_elapsed_time = 0
    stopwatch_display.config(text="00:00:00")
    reset_stopwatch_button.config(state=tk.DISABLED)
def start_pomodoro():
    global pomodoro_is_running, pomodoro_thread, start_pomodoro_button, \
           stop_pomodoro_button, reset_pomodoro_button
    if not pomodoro_is_running:
        pomodoro_is_running = True
        start_pomodoro_button.config(state=tk.DISABLED)
        stop_pomodoro_button.config(state=tk.NORMAL)
        reset_pomodoro_button.config(state=tk.NORMAL)
        pomodoro_thread = threading.Thread(target=_run_pomodoro, daemon=True)
        pomodoro_thread.start()
def _run_pomodoro():
    global pomodoro_is_running, pomodoro_current_phase, pomodoro_status, \
           pomodoro_display, root
    work_time = 25 * 60
    break_time = 5 * 60

    while pomodoro_is_running:
        pomodoro_current_phase = "work"
        pomodoro_status.config(text="Làm việc: Tập trung!", fg="black")
        for t in range(work_time, -1, -1):
            if not pomodoro_is_running: break
            m, s = divmod(t, 60)
            pomodoro_display.config(text=f"{m:02d}:{s:02d}")
            root.update_idletasks()
            time.sleep(1)
        if not pomodoro_is_running: break
        messagebox.showinfo("Pomodoro", "Hết giờ làm việc! Đến lúc nghỉ ngơi!")

        pomodoro_current_phase = "break"
        pomodoro_status.config(text="Nghỉ ngơi: Thư giãn!", fg="black")
        for t in range(break_time, -1, -1):
            if not pomodoro_is_running: break
            m, s = divmod(t, 60)
            pomodoro_display.config(text=f"{m:02d}:{s:02d}")
            root.update_idletasks()
            time.sleep(1)
        if not pomodoro_is_running: break
        messagebox.showinfo("Pomodoro", "Hết giờ nghỉ! Quay lại làm việc!")
    stop_pomodoro()
def stop_pomodoro():
    global pomodoro_is_running, start_pomodoro_button, stop_pomodoro_button, \
           pomodoro_status, pomodoro_display
    pomodoro_is_running = False
    start_pomodoro_button.config(state=tk.NORMAL)
    stop_pomodoro_button.config(state=tk.DISABLED)
    pomodoro_status.config(text="Sẵn sàng: 25' làm việc, 5' nghỉ", fg="black")
    pomodoro_display.config(text="25:00")
def reset_pomodoro():
    global pomodoro_is_running, start_pomodoro_button, stop_pomodoro_button, \
           reset_pomodoro_button, pomodoro_status, pomodoro_display
    stop_pomodoro()
    pomodoro_status.config(text="Sẵn sàng: 25' làm việc, 5' nghỉ", fg="black")
    pomodoro_display.config(text="25:00")
    start_pomodoro_button.config(state=tk.NORMAL)
    stop_pomodoro_button.config(state=tk.DISABLED)
    reset_pomodoro_button.config(state=tk.DISABLED)
def dem_nguoc(): # Tính năng 7: Đồng hồ đếm ngược, bấm giờ và Pomodoro
    global countdown_display, countdown_hr_spinbox, countdown_min_spinbox, countdown_sec_spinbox, \
           countdown_hr_var, countdown_min_var, countdown_sec_var, \
           start_countdown_button, stop_countdown_button, reset_countdown_button, \
           stopwatch_display, start_stopwatch_button, stop_stopwatch_button, reset_stopwatch_button, \
           pomodoro_status, pomodoro_display, start_pomodoro_button, stop_pomodoro_button, reset_pomodoro_button, \
           countdown_initial_time, countdown_current_time
    if not root:
        return
    tinh_nang_7 = tk.Toplevel(root) # liên kết với của sổ chính bằng root
    tinh_nang_7.title("7. Đồng Hồ đếm ngược") # Thiết lập tên cho cửa sổ
    tinh_nang_7.resizable(False, False) # Loại bỏ khả năng thu phóng cảu cửa sổ
    # Đoạn này dùng để thay đổi giao diện 
    style = ThemedStyle(tinh_nang_7)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_7.config(bg=theme_bg_color)

    countdown_frame = ttk.LabelFrame(tinh_nang_7, text="Đếm Ngược")
    countdown_frame.grid(row=0, column=0, padx=20, pady=15, sticky="ew")
    countdown_frame.grid_columnconfigure(0, weight=1)

    countdown_adjust_all_frame = ttk.Frame(countdown_frame)
    countdown_adjust_all_frame.grid(row=0, column=0, pady=5)

    countdown_hr_var = tk.IntVar(value=countdown_initial_time // 3600)
    countdown_min_var = tk.IntVar(value=(countdown_initial_time % 3600) // 60)
    countdown_sec_var = tk.IntVar(value=countdown_initial_time % 60)

    countdown_hr_spinbox = create_time_input_spinbox(countdown_adjust_all_frame, "Giờ:", countdown_hr_var, 0)
    countdown_min_spinbox = create_time_input_spinbox(countdown_adjust_all_frame, "Phút:", countdown_min_var, 2)
    countdown_sec_spinbox = create_time_input_spinbox(countdown_adjust_all_frame, "Giây:", countdown_sec_var, 4)

    countdown_display = ttk.Label(countdown_frame, text="00:00:00", font=FONT_TIME_DISPLAY)
    countdown_display.grid(row=1, column=0, pady=10)

    countdown_buttons_frame = ttk.Frame(countdown_frame)
    countdown_buttons_frame.grid(row=2, column=0)

    start_countdown_button = create_control_button(countdown_buttons_frame, "Bắt Đầu", start_countdown, column=0)
    stop_countdown_button = create_control_button(countdown_buttons_frame, "Dừng", stop_countdown, state=tk.DISABLED, column=1)
    reset_countdown_button = create_control_button(countdown_buttons_frame, "Đặt Lại", reset_countdown, state=tk.DISABLED, column=2)

    stopwatch_frame = ttk.LabelFrame(tinh_nang_7, text="Bấm Giờ")
    stopwatch_frame.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
    stopwatch_frame.grid_columnconfigure(0, weight=1)

    stopwatch_display = ttk.Label(stopwatch_frame, text="00:00:00", font=FONT_TIME_DISPLAY)
    stopwatch_display.grid(row=0, column=0, pady=10)

    stopwatch_buttons_frame = ttk.Frame(stopwatch_frame)
    stopwatch_buttons_frame.grid(row=1, column=0)

    start_stopwatch_button = create_control_button(stopwatch_buttons_frame, "Bắt Đầu", start_stopwatch, column=0)
    stop_stopwatch_button = create_control_button(stopwatch_buttons_frame, "Dừng", stop_stopwatch, state=tk.DISABLED, column=1)
    reset_stopwatch_button = create_control_button(stopwatch_buttons_frame, "Đặt Lại", reset_stopwatch, state=tk.DISABLED, column=2)

    pomodoro_frame = ttk.LabelFrame(tinh_nang_7, text="Pomodoro")
    pomodoro_frame.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
    pomodoro_frame.grid_columnconfigure(0, weight=1)

    pomodoro_status = ttk.Label(pomodoro_frame, text="Sẵn sàng: 25' làm việc, 5' nghỉ", font=FONT_DEFAULT)
    pomodoro_status.grid(row=0, column=0, pady=5)

    pomodoro_display = ttk.Label(pomodoro_frame, text="25:00", font=FONT_TIME_DISPLAY)
    pomodoro_display.grid(row=1, column=0, pady=10)

    pomodoro_buttons_frame = ttk.Frame(pomodoro_frame)
    pomodoro_buttons_frame.grid(row=2, column=0, pady=5)

    start_pomodoro_button = create_control_button(pomodoro_buttons_frame, "Bắt Đầu", start_pomodoro, column=0)
    stop_pomodoro_button = create_control_button(pomodoro_buttons_frame, "Dừng", stop_pomodoro, state=tk.DISABLED, column=1)
    reset_pomodoro_button = create_control_button(pomodoro_buttons_frame, "Đặt Lại", reset_pomodoro, state=tk.DISABLED, column=2)

    update_countdown_set_spinboxes()
    h, remainder = divmod(countdown_initial_time, 3600)
    m, s = divmod(remainder, 60)
    countdown_display.config(text=f"{h:02d}:{m:02d}:{s:02d}")
###################################################################################
current_file = None
last_saved_content = ""
text_widget = None
tinh_nang_8 = None 

# --- Các hàm tiện ích ---
def get_content() -> str:
    """Lấy nội dung hiện tại từ widget văn bản và loại bỏ ký tự xuống dòng thừa."""
    content = text_widget.get(1.0, tk.END)
    # Loại bỏ ký tự xuống dòng thừa do widget scrolledtext tự động thêm vào
    if content.endswith('\n'):
        content = content[:-1]
        return content
def set_content(content: str) -> None:
    """Đặt nội dung vào widget văn bản."""
    text_widget.delete(1.0, tk.END)
    text_widget.insert(tk.END, content)
def has_unsaved_changes() -> bool:
    """Kiểm tra xem có thay đổi nào chưa lưu hay không."""
    return last_saved_content != get_content()
def clear_unsaved_changes() -> None:
    """Cập nhật nội dung đã lưu cuối cùng và tiêu đề cửa sổ."""
    global last_saved_content
    last_saved_content = get_content()
    update_title()
def update_title() -> None:
    """Cập nhật tiêu đề cửa sổ hiển thị tên file và trạng thái lưu."""
    global tinh_nang_8
    file_name = current_file.split('/')[-1] if current_file else 'Không có tên file'
    unsaved_indicator = '*' if has_unsaved_changes() else ''
    if tinh_nang_8: # Đảm bảo cửa sổ đã được tạo trước khi cập nhật tiêu đề
        tinh_nang_8.title(f"8.Soạn thảo văn bản - {file_name}{unsaved_indicator}")
def set_current_file(file_path: str|None) -> None:
    """Đặt file hiện tại và xóa các thay đổi chưa lưu."""
    global current_file
    current_file = file_path
    clear_unsaved_changes()
def show_unsaved_changes_warning(action: str) -> bool:
    """Hiển thị cảnh báo nếu có thay đổi chưa lưu và trả về True nếu người dùng muốn tiếp tục."""
    if has_unsaved_changes():
        result = messagebox.askyesnocancel("Thay Đổi Chưa Lưu", f"Các thay đổi sẽ bị mất nếu bạn {action}. Tiếp tục?")
        return result is True
    return True # Không có thay đổi chưa lưu, có thể tiếp tục
# --- Các chức năng chỉnh sửa ---
def undo(event=None):
    text_widget.event_generate("<<Undo>>")
    return "break"
def redo(event=None):
    text_widget.event_generate("<<Redo>>")
    return "break"
def cut(event=None):
    text_widget.event_generate("<<Cut>>")
    return "break"
def copy(event=None):
    text_widget.event_generate("<<Copy>>")
    return "break"
def paste(event=None):
    text_widget.event_generate("<<Paste>>")
    return "break"
def select_all(event=None):
    text_widget.tag_add(tk.SEL, 1.0, tk.END)
    return "break"
# --- Các chức năng quản lý file ---
def new_file(event=None):
    """Tạo một file mới, hỏi người dùng nếu có thay đổi chưa lưu."""
    if not show_unsaved_changes_warning("tạo file mới"):
        return
    set_content("")
    set_current_file(None)
def open_file(event=None):
    """Mở một file, hỏi người dùng nếu có thay đổi chưa lưu."""
    if not show_unsaved_changes_warning("mở file mới"):
        return
    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Tệp văn bản", "*.txt"), ("Tất cả tệp", "*.*")])
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as file: # Thêm encoding
                content = file.read()
                set_content(content)
                set_current_file(file_path)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở tệp: {e}")
def close_file(event=None):
    """Đóng file hiện tại hoặc thoát ứng dụng nếu không có file nào đang mở."""
    if not show_unsaved_changes_warning("đóng file"):
        return
    global tinh_nang_8
    if current_file is None: # Nếu đang ở trạng thái Untitled và người dùng chọn đóng
        if tinh_nang_8: # Đảm bảo cửa sổ tồn tại trước khi destroy
            tinh_nang_8.destroy() # Đóng cửa sổ nếu không có file nào đang mở
    else: # Nếu có file đang mở
        set_content("")
        set_current_file(None)
def save_file(event=None):
    """Lưu file hiện tại. Nếu chưa có file, sẽ gọi hàm lưu như."""
    if current_file is None:
        save_as_file()
    else:
        try:
            with open(current_file, "w", encoding="utf-8") as file: # Thêm encoding
                content = get_content() # Sử dụng hàm get_content để loại bỏ ký tự xuống dòng thừa
                file.write(content)
            clear_unsaved_changes()
            messagebox.showinfo("Đã Lưu", "Tệp đã được lưu thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu tệp: {e}")
def save_as_file(event=None):
    """Lưu file với tên mới."""
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Tệp văn bản", "*.txt"), ("Tất cả tệp", "*.*")])
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as file: # Thêm encoding
                content = get_content() # Sử dụng hàm get_content để loại bỏ ký tự xuống dòng thừa
                file.write(content)
            set_current_file(file_path)
            messagebox.showinfo("Đã Lưu", "Tệp đã được lưu thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu tệp: {e}")
def on_closing():
    """Hỏi người dùng trước khi đóng cửa sổ nếu có thay đổi chưa lưu."""
    global tinh_nang_8
    if has_unsaved_changes():
        result = messagebox.askyesnocancel("Thoát", "Bạn có muốn lưu các thay đổi trước khi thoát không?")
        if result is True:
            save_file()
            # Kiểm tra lại sau khi save_file để đảm bảo việc lưu đã thành công (người dùng không hủy Save As)
            if has_unsaved_changes():
                return # Nếu vẫn còn thay đổi chưa lưu, không đóng cửa sổ
            else:
                if tinh_nang_8: # Đảm bảo cửa sổ tồn tại trước khi destroy
                    tinh_nang_8.destroy()
        elif result is False: # Người dùng chọn không lưu
            if tinh_nang_8: # Đảm bảo cửa sổ tồn tại trước khi destroy
                tinh_nang_8.destroy()
        # Nếu result là None (Cancel), thì không làm gì cả
    else: # Không có thay đổi chưa lưu, đóng cửa sổ
        if tinh_nang_8: # Đảm bảo cửa sổ tồn tại trước khi destroy
            tinh_nang_8.destroy()
def van_ban(): # Tính năng 8: Trình soạn thảo văn bản
    global tinh_nang_8, text_widget # Khai báo các biến toàn cục sẽ được sử dụng
    if not root: # Đảm bảo cửa sổ chính root tồn tại
        return

    # Tạo cửa sổ phụ cho tính năng trình soạn thảo
    tinh_nang_8 = tk.Toplevel(root) # liên kết với cửa sổ chính bằng root
    tinh_nang_8.title("8.Soạn thảo văn bản") # Thiết lập tên cho cửa sổ ban đầu (tôi đã đổi tên hiển thị cho phù hợp hơn)
    # Kích thước cửa sổ ban đầu có thể nhỏ, sau đó sẽ được điều chỉnh bởi pack/grid
    tinh_nang_8.geometry("800x600") # Kích thước mặc định hợp lý hơn
    tinh_nang_8.protocol("WM_DELETE_WINDOW", on_closing) # Xử lý sự kiện đóng cửa sổ

    # Đoạn này dùng để thay đổi giao diện
    style = ThemedStyle(tinh_nang_8)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_8.config(bg=theme_bg_color)

    text_widget = scrolledtext.ScrolledText(tinh_nang_8, wrap=tk.WORD, undo=True, maxundo=-1,bg=theme_bg_color)
    text_widget.pack(expand=True, fill='both')

    set_current_file(None) # Khởi tạo file là Untitled
    text_widget.bind("<KeyRelease>", lambda event: update_title())

    # Gán phím tắt
    tinh_nang_8.bind("<Control-z>", undo)
    tinh_nang_8.bind("<Control-y>", redo)
    tinh_nang_8.bind("<Control-x>", cut)
    tinh_nang_8.bind("<Control-c>", copy)
    tinh_nang_8.bind("<Control-v>", paste)
    tinh_nang_8.bind("<Control-a>", select_all)
    tinh_nang_8.bind("<Control-n>", new_file)
    tinh_nang_8.bind("<Control-o>", open_file)
    tinh_nang_8.bind("<Control-w>", close_file)
    tinh_nang_8.bind("<Control-s>", save_file)
    tinh_nang_8.bind("<Control-S>", save_as_file) # Ctrl+Shift+S

    # Menu Bar
    menu_bar = tk.Menu(tinh_nang_8)
    tinh_nang_8.config(menu=menu_bar)

    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Tệp", menu=file_menu)
    file_menu.add_command(label="Mới", command=new_file, accelerator="Ctrl+N")
    file_menu.add_command(label="Mở", command=open_file, accelerator="Ctrl+O")
    file_menu.add_command(label="Lưu", command=save_file, accelerator="Ctrl+S")
    file_menu.add_command(label="Lưu Như...", command=save_as_file, accelerator="Ctrl+Shift+S")
    file_menu.add_separator()
    file_menu.add_command(label="Đóng", command=close_file, accelerator="Ctrl+W")
    file_menu.add_command(label="Thoát", command=on_closing)

    edit_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Chỉnh Sửa", menu=edit_menu)
    edit_menu.add_command(label="Hoàn Tác", command=undo, accelerator="Ctrl+Z")
    edit_menu.add_command(label="Làm Lại", command=redo, accelerator="Ctrl+Y")
    edit_menu.add_separator()
    edit_menu.add_command(label="Cắt", command=cut, accelerator="Ctrl+X")
    edit_menu.add_command(label="Sao Chép", command=copy, accelerator="Ctrl+C")
    edit_menu.add_command(label="Dán", command=paste, accelerator="Ctrl+V")
    edit_menu.add_separator()
    edit_menu.add_command(label="Chọn Tất Cả", command=select_all, accelerator="Ctrl+A")
###################################################################################
VALID_CITIES_FILE = "valid_cities.txt"
CITY_LIST_GZ_FILE = "city.list.json.gz"
CITY_LIST_DOWNLOAD_URL = "http://bulk.openweathermap.org/sample/city.list.json.gz"
API_KEYS = [
    "383c5c635c88590b37c698bc100f6377",
    "fe8d8c65cf345889139d8e545f57819a",
    "68c51539817878022c5315a3b403165c"]
VIETNAM_LOCATIONS = [] # Sẽ được điền dữ liệu sau khi khởi tạo
# --- Hàm hỗ trợ dữ liệu (Data Utility Functions) ---
def download_city_list_file(url, file_path):
    try:
        print(f"Đang tải tệp danh sách thành phố từ: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status() # Kiểm tra lỗi HTTP (ví dụ: 404 Not Found)

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Tệp '{file_path}' đã được tải xuống thành công.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tải tệp danh sách thành phố: {e}")
        return False
    except Exception as e:
        print(f"Đã xảy ra lỗi không mong muốn khi tải tệp: {e}")
        return False
def extract_vietnam_cities(file_path=CITY_LIST_GZ_FILE):
    vietnam_cities = []
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            data = json.load(f)
            for city_info in data:
                if city_info.get('country') == 'VN':
                    vietnam_cities.append(city_info.get('name'))
        return sorted(list(set(vietnam_cities)))
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy tệp '{file_path}'. Vui lòng đảm bảo tệp đã được tải xuống hoặc thử tải lại.")
        return []
    except Exception as e:
        print(f"Đã xảy ra lỗi khi xử lý tệp '{file_path}': {e}")
        return []
def load_valid_cities():
    """Tải danh sách các thành phố đã tìm kiếm thành công từ file."""
    if os.path.exists(VALID_CITIES_FILE):
        with open(VALID_CITIES_FILE, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file if line.strip())
    return set()
def save_valid_city(city_name):
    """Lưu tên thành phố vào danh sách các thành phố hợp lệ nếu chưa có."""
    cities = load_valid_cities()
    if city_name not in cities:
        with open(VALID_CITIES_FILE, 'a', encoding='utf-8') as file:
            file.write(f"{city_name}\n")
def get_weather_data(city_name, api_keys):
    city_for_api = unidecode(city_name) + ",VN"
    ow_url = "http://api.openweathermap.org/data/2.5/weather?"

    for api_key in api_keys:
        call_url = f"{ow_url}appid={api_key}&q={city_for_api}&units=metric&lang=vi"
        try:
            response = requests.get(call_url)
            data = response.json()

            if data["cod"] == 200:
                save_valid_city(city_name)
                return f"""
--- Thời tiết hiện tại ---
🌡️ Nhiệt độ: {data['main']['temp']}°C
Cảm giác như: {data['main']['feels_like']}°C
💦 Độ ẩm: {data['main']['humidity']}%
☁️ Thời tiết: {data['weather'][0]['description'].capitalize()}
💨 Tốc độ gió: {data['wind']['speed']} m/s
"""
            elif data["cod"] == 404:
                continue
            else:
                print(f"Lỗi API ({data['cod']}): {data['message']}")
                continue
        except requests.exceptions.ConnectionError:
            print("Lỗi kết nối mạng khi gọi API.")
            continue
        except Exception as e:
            print(f"Đã xảy ra lỗi không mong muốn: {e}")
            continue

    return f"Không thể tìm thấy thông tin thời tiết hiện tại cho '{city_name}' hoặc tất cả các khóa API đã hết hạn/lỗi. Vui lòng thử lại."
def get_forecast_data(city_name, api_keys):
    city_for_api = unidecode(city_name) + ",VN"
    ow_forecast_url = "http://api.openweathermap.org/data/2.5/forecast?"

    for api_key in api_keys:
        call_url = f"{ow_forecast_url}appid={api_key}&q={city_for_api}&units=metric&lang=vi"
        try:
            response = requests.get(call_url)
            data = response.json()

            if data["cod"] == "200":
                forecast_text = f"\n--- Dự báo 5 ngày cho {city_name} ---\n\n" # Thêm dấu cách và tiêu đề

                daily_forecasts = {}
                for item in data['list']:
                    date_time = item['dt_txt']
                    date = date_time.split(' ')[0]

                    if date not in daily_forecasts:
                        daily_forecasts[date] = []
                    daily_forecasts[date].append(item)

                for date, forecasts in daily_forecasts.items():
                    forecast_text += f"Ngày {date}:\n"
                    min_temp = float('inf')
                    max_temp = float('-inf')
                    descriptions = set()

                    for f_item in forecasts:
                        min_temp = min(min_temp, f_item['main']['temp_min'])
                        max_temp = max(max_temp, f_item['main']['temp_max'])
                        descriptions.add(f_item['weather'][0]['description'].capitalize())

                    forecast_text += f"   Nhiệt độ: {min_temp:.1f}°C - {max_temp:.1f}°C\n"
                    forecast_text += f"   Thời tiết: {', '.join(descriptions)}\n\n"

                return forecast_text
            elif data["cod"] == "404":
                continue
            else:
                print(f"Lỗi API dự báo ({data['cod']}): {data['message']}")
                continue
        except requests.exceptions.ConnectionError:
            print("Lỗi kết nối mạng khi gọi API dự báo.")
            continue
        except Exception as e:
            print(f"Đã xảy ra lỗi không mong muốn khi lấy dự báo: {e}")
            continue

    return f"Không thể lấy dữ liệu dự báo cho '{city_name}'. Vui lòng thử lại."
def initialize_app_data():
    global VIETNAM_LOCATIONS # Khai báo để có thể gán giá trị cho biến toàn cục

    if not os.path.exists(CITY_LIST_GZ_FILE):
        messagebox.showinfo("Thông báo", "Tệp danh sách thành phố chưa tồn tại. Đang tiến hành tải xuống...")
        if not download_city_list_file(CITY_LIST_DOWNLOAD_URL, CITY_LIST_GZ_FILE):
            messagebox.showerror("Lỗi tải tệp", "Không thể tải tệp danh sách thành phố. Vui lòng kiểm tra kết nối internet hoặc thử lại sau.")

    VIETNAM_LOCATIONS = extract_vietnam_cities()
    if not VIETNAM_LOCATIONS:
        messagebox.showwarning("Cảnh báo", f"Không thể tải danh sách các tỉnh/thành phố của Việt Nam từ '{CITY_LIST_GZ_FILE}'. "
                                         "Vui lòng kiểm tra file đã tải xuống hoặc thử tải lại.")
# --- Biến UI toàn cục (sẽ được khởi tạo trong create_weather_window) ---
city_entry = None
combined_weather_text_widget = None # Đã đổi tên và chức năng
show_weather_button = None
city_listbox = None
province_listbox = None
tinh_nang_10 = None # Cửa sổ Toplevel
# --- Hàm xử lý sự kiện UI (di chuyển ra ngoài create_weather_window) ---
def update_ui_with_all_results(current_weather_info, forecast_info):
    global combined_weather_text_widget, show_weather_button, city_entry, city_listbox, province_listbox

    full_output = f"{current_weather_info}\n{forecast_info}" # Gộp cả hai thông tin

    combined_weather_text_widget.config(state=tk.NORMAL)
    combined_weather_text_widget.delete(1.0, tk.END)
    combined_weather_text_widget.insert(tk.END, full_output)
    combined_weather_text_widget.config(state=tk.DISABLED)
 
    show_weather_button.config(state=tk.NORMAL)
    city_entry.config(state=tk.NORMAL)
    city_listbox.config(state=tk.NORMAL)
    province_listbox.config(state=tk.NORMAL)
def fetch_and_update(city_name):
    global root # Cần truy cập root cho after()
    current_weather = get_weather_data(city_name, API_KEYS)
    forecast_data = get_forecast_data(city_name, API_KEYS)
    root.after(0, update_ui_with_all_results, current_weather, forecast_data)
def show_all_weather_data_async():
    global city_entry, combined_weather_text_widget, show_weather_button, city_listbox, province_listbox

    city_name = city_entry.get().strip()
    if not city_name:
        messagebox.showwarning("Lỗi", "Vui lòng nhập tên thành phố.")
        return

    # Hiển thị thông báo đang tải trong ô kết hợp
    combined_weather_text_widget.config(state=tk.NORMAL)
    combined_weather_text_widget.delete(1.0, tk.END)
    combined_weather_text_widget.insert(tk.END, "Đang tải thời tiết hiện tại và dữ liệu dự báo...")
    combined_weather_text_widget.config(state=tk.DISABLED)

    show_weather_button.config(state=tk.DISABLED)
    city_entry.config(state=tk.DISABLED)
    city_listbox.config(state=tk.DISABLED)
    province_listbox.config(state=tk.DISABLED)
    
    thread = threading.Thread(target=fetch_and_update, args=(city_name,))
    thread.start()
def select_from_list(event, listbox_widget):
    global city_entry
    selected_indices = listbox_widget.curselection()
    if selected_indices:
        selected_item = listbox_widget.get(selected_indices[0])
        city_entry.delete(0, tk.END)
        city_entry.insert(0, selected_item)
        show_all_weather_data_async() # Tự động tìm kiếm khi chọn
def clear_search_history():
    global city_listbox
    if os.path.exists(VALID_CITIES_FILE):
        os.remove(VALID_CITIES_FILE)
        city_listbox.delete(0, tk.END)
        messagebox.showinfo("Thông báo", "Lịch sử tìm kiếm đã được xóa.")
    else:
        messagebox.showinfo("Thông báo", "Không có lịch sử tìm kiếm để xóa.")
# --- Hàm tạo cửa sổ chính ---
def create_weather_window(root):
    """Tạo cửa sổ ứng dụng thời tiết."""
    global city_entry, combined_weather_text_widget, show_weather_button
    global city_listbox, province_listbox, tinh_nang_10

    tinh_nang_10 = tk.Toplevel(root)
    tinh_nang_10.title("10. Thời tiết")
    tinh_nang_10.geometry("900x600") # Kích thước mặc định
    tinh_nang_10.resizable(True, True) # Cho phép thay đổi kích thước

    # Áp dụng theme từ ttkthemes cho cửa sổ con
    style = ThemedStyle(tinh_nang_10)
    style.set_theme(current_theme)

    # Đặt màu nền cho cửa sổ dựa trên theme
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_10.config(bg=theme_bg_color)

    # Cấu hình grid cho cửa sổ con
    tinh_nang_10.grid_rowconfigure(0, weight=1)
    tinh_nang_10.grid_columnconfigure(0, weight=1) # Cột bên trái (danh sách)
    tinh_nang_10.grid_columnconfigure(1, weight=2) # Cột bên phải (hiển thị thời tiết)

    # --- Panel bên trái (Lịch sử và Tỉnh/TP Việt Nam) ---
    left_panel = ttk.Frame(tinh_nang_10, padding="10", style='TFrame')
    left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    left_panel.grid_rowconfigure(1, weight=1) # Cho listbox chiếm không gian
    left_panel.grid_rowconfigure(4, weight=1) # Cho listbox chiếm không gian
    left_panel.grid_columnconfigure(0, weight=1)

    ttk.Label(left_panel, text="Lịch sử tìm kiếm:", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5, sticky="ew")
    city_listbox = tk.Listbox(left_panel, height=8, font=("Arial", 10), selectmode=tk.SINGLE)
    city_listbox.grid(row=1, column=0, pady=5, sticky="nsew")
    for city in load_valid_cities():
        city_listbox.insert(tk.END, city)
    city_listbox.bind("<<ListboxSelect>>", lambda event: select_from_list(event, city_listbox))

    ttk.Button(left_panel, text="Xóa Lịch sử", command=clear_search_history, style='TButton').grid(row=2, column=0, pady=5, sticky="ew")

    ttk.Label(left_panel, text="Tỉnh/thành phố Việt Nam:", font=("Arial", 12, "bold")).grid(row=3, column=0, pady=10, sticky="ew")
    province_listbox = tk.Listbox(left_panel, height=8, font=("Arial", 10), selectmode=tk.SINGLE)
    province_listbox.grid(row=4, column=0, pady=5, sticky="nsew")
    for province in VIETNAM_LOCATIONS:
        province_listbox.insert(tk.END, province)
    province_listbox.bind("<<ListboxSelect>>", lambda event: select_from_list(event, province_listbox))

    # --- Panel bên phải (Nhập liệu và Hiển thị Thời tiết) ---
    right_panel = ttk.Frame(tinh_nang_10, padding="10", style='TFrame')
    right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    right_panel.grid_rowconfigure(2, weight=1) # Cho ô hiển thị thời tiết tổng hợp
    right_panel.grid_columnconfigure(0, weight=1)

    # Khung chứa thanh tìm kiếm và nút tìm kiếm
    input_frame = ttk.Frame(right_panel, style='TFrame')
    input_frame.grid(row=0, column=0, pady=10, sticky="ew")
    input_frame.grid_columnconfigure(0, weight=3) # Cho thanh nhập liệu chiếm nhiều không gian hơn
    input_frame.grid_columnconfigure(1, weight=1) # Cho nút tìm kiếm

    ttk.Label(input_frame, text="Nhập tên thành phố:", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,5), sticky="ew")
    city_entry = ttk.Entry(input_frame, font=("Arial", 12))
    city_entry.grid(row=1, column=0, pady=5, padx=(0, 5), sticky="ew")
    city_entry.bind("<Return>", lambda event: show_all_weather_data_async()) # Cho phép Enter để tìm

    show_weather_button = ttk.Button(input_frame, text="Xem Thời tiết", command=show_all_weather_data_async,
                                     style='TButton', cursor="hand2")
    show_weather_button.grid(row=1, column=1, pady=5, sticky="ew")

    # Ô hiển thị kết hợp thời tiết hiện tại và dự báo
    combined_weather_frame = ttk.Frame(right_panel, relief="solid", borderwidth=1)
    combined_weather_frame.grid(row=2, column=0, pady=10, sticky="nsew")
    combined_weather_frame.grid_rowconfigure(0, weight=1)
    combined_weather_frame.grid_columnconfigure(0, weight=1)

    combined_weather_text_widget = tk.Text(combined_weather_frame, font=("Arial", 10), wrap=tk.WORD,
                                   padx=10, pady=10, state=tk.DISABLED)
    combined_weather_text_widget.grid(row=0, column=0, sticky="nsew")

    combined_weather_scrollbar = ttk.Scrollbar(combined_weather_frame, orient="vertical", command=combined_weather_text_widget.yview)
    combined_weather_scrollbar.grid(row=0, column=1, sticky="ns")
    combined_weather_text_widget.config(yscrollcommand=combined_weather_scrollbar.set)
def thoi_tiet():
    if root is None:
        return 
    initialize_app_data()
    create_weather_window(root)
###################################################################################
CONFIG_FILE = "thiet_lap_giao_dien.ini"
available_themes = ["equilux", "radiance", "arc", "breeze", "ubuntu", "yaru", "plastik",
                    "clam", "alt", "default", "classic", "adapta", "aquativo", "clearlooks",
                    "elegance", "itft1", "keramik", "kroc", "nutmeg", "smog", "winnative", "xpnative"] # Các chủ đề có sẵn của ttkthemes
def load_theme_setting(): # Đọc chủ đề hiện tại trong file
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if 'Settings' in config and 'theme' in config['Settings']:
        return config['Settings']['theme']
    return available_themes[0] # Chủ đề mặc định nếu chưa có
def save_theme_setting(theme): # Lưu chủ để hiện tại 
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE) # Đọc các cài đặt hiện có
    if 'Settings' not in config:
        config['Settings'] = {}
    config['Settings']['theme'] = theme
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
current_theme = load_theme_setting() # Nơi chứa chủ đề đang được sử dụng
open_toplevels = []  # Nơi chứa các toplevel đang hoạt động 
def apply_theme(theme): # Áp dụng chủ đề cho cửa sổ root và tất cả cửa sổ con.
    global current_theme, root # Khai báo nó sẽ sử dụng và thay đổi các biến toàn cục và root (cái này để sau đi lười giải thích -___-)
    current_theme = theme  # Cập nhập biến theme bằng current_theme đã chọn
    if root:
        style = ThemedStyle(root)  # Tạo 1 đối tượng "ThemedStyle" để liên kết với root
        style.set_theme(theme) # Áp dụng chủ đề được truyền vào (theme) cho cửa sổ root

        theme_bg_color = style.lookup(".", "background") or "#F0F0F0" # Dùng màu của chủ đề để làm màu nền nếu không tìm đc thì dùng màu #F0F0F0 màu nàu cố thể thay đỏi tùy theo nhu cầu
        root.config(bg=theme_bg_color) # Đặt màu nền cho cửa sổ chính

        for top in open_toplevels[:]: # Lặp lại danh sách để tăng độ an toàn và ổn định (1 bộ phận quan trọng đó, xóa đi thì...)
            if top.winfo_exists(): #  Kiểm tra xem cửa sổ phụ top có còn tồn tại (chưa bị đóng) hay không
                top_style = ThemedStyle(top) # Tạo một đối tượng ThemedStyle riêng cho từng cửa sổ phụ
                top_style.set_theme(theme) #  Áp dụng chủ đề cho cửa sổ phụ hiện tại
                top.config(bg=theme_bg_color) # Đặt màu nền cho cửa sổ phụ
            else: 
                open_toplevels.remove(top) # Xóa cửa sộ phụ đã đóng hoặc không tồn tại ra khỏi danh sách
    save_theme_setting(theme) # Lưu chủ đề sau khi áp dụng thành công
def giao_dien (): # Tính năng 11: Giao diện
    if not root: # 2 Dòng này nhằm đảm bảo của sổ chính tồn tại 
        return
    # Tạo cửa sổ phụ cho tính năng 11     
    tinh_nang_11 = tk.Toplevel(root) # liên kết với của sổ chính bằng root
    tinh_nang_11.title("Chọn chủ đề") # Thiết lập tên cho cửa sổ
    tinh_nang_11.geometry("300x180") # Thiết lập kích thước
    tinh_nang_11.resizable(False, False) # Loại bỏ khả năng thu phóng của cửa sổ
    # Đoạn này dùng để thay đổi giao diện 
    style = ThemedStyle(tinh_nang_11)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_11.config(bg=theme_bg_color)

    ttk.Label(tinh_nang_11, text="Chọn chế độ giao diện:", font=("Arial", 12, "bold")).pack(pady=10)

    theme_combobox = ttk.Combobox(tinh_nang_11, values=available_themes, state="readonly")
    theme_combobox.pack(pady=5, padx=10)
    theme_combobox.set(current_theme)
    # dùng để tạo 1 ô để hiển thị thông báo 
    status_label = ttk.Label(tinh_nang_11, text="", font=("Arial", 10), foreground="green") 
    status_label.pack(pady=5)

    def apply_and_confirm(): # Dùng để thông báo đã thay đổi thành công
        new_theme = theme_combobox.get()
        apply_theme(new_theme)
        status_label.config(text="Đã áp dụng chủ đề!")
        tinh_nang_11.after(2000, lambda: status_label.config(text=""))

    ttk.Button(tinh_nang_11, text="Áp dụng", command=apply_and_confirm).pack(pady=10) # Tạo 1 cái nút

    open_toplevels.append(tinh_nang_11)
    tinh_nang_11.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_11))
def on_toplevel_close(window): # Xử lý khi một cửa sổ Toplevel bị đóng.
    if window in open_toplevels:
        open_toplevels.remove(window)
    window.destroy()
###################################################################################
loading_frame = None
loading_label = None
cache_file = "periodic_table_data.json"
periodic_elements = []
periodic_table_frame = None
info_frame = None
info_text_area = None
def get_color_by_category(category):
    """Trả về mã màu HEX dựa trên loại nguyên tố."""
    colors = {
        "alkali metal": "#FF9999",         # Kim loại kiềm (Đỏ nhạt)
        "alkaline earth metal": "#FFCC99", # Kim loại kiềm thổ (Cam nhạt)
        "metalloid": "#FFFF99",            # Á kim (Vàng nhạt)
        "nonmetal": "#CCFFCC",             # Phi kim (Xanh lá nhạt)
        "noble gas": "#99CCFF",            # Khí hiếm (Xanh dương nhạt)
        "halogen": "#CC99FF",              # Halogen (Tím nhạt)
        "transition metal": "#FFCCCC",     # Kim loại chuyển tiếp (Hồng)
        "post-transition metal": "#CCCCFF", # Kim loại sau chuyển tiếp (Oải hương)
        "lanthanide": "#FFCCFF",           # Lanthanide (Hồng cánh sen nhạt)
        "actinide": "#FF99FF",             # Actinide (Hồng đậm hơn)
        # Các loại "unknown" được gán cùng một màu xám nhạt để nhất quán
        "unknown, probably transition metal": "#D3D3D3",
        "unknown, probably post-transition metal": "#D3D3D3",
        "unknown, probably metalloid": "#D3D3D3",
        "unknown, predicted to be noble gas": "#D3D3D3"}
    global theme_bg_color
    return colors.get(category,theme_bg_color) 
def display_element_info(element):
    """Hiển thị thông tin chi tiết của một nguyên tố trong info_text_area."""
    info_text = (
        f"Tên: {element.get('name', 'N/A')}\n"
        f"Ký hiệu: {element.get('symbol', 'N/A')}\n"
        f"Số Nguyên Tử: {element.get('number', 'N/A')}\n"
        f"Khối Lượng Nguyên Tử: {element.get('atomic_mass', 'N/A')} u\n"
        f"Loại: {element.get('category', 'N/A').replace('_', ' ').title()}\n"
        f"Chu Kỳ: {element.get('period', 'N/A')}\n"
        f"Nhóm: {element.get('group', 'N/A')}\n"
        f"Điện Âm (Pauling): {element.get('electronegativity_pauling', 'N/A')}\n"
        f"Mật Độ: {element.get('density', 'N/A')} g/cm³\n"
        f"Điểm Nóng Chảy: {element.get('melt', 'N/A')} K\n"
        f"Điểm Sôi: {element.get('boil', 'N/A')} K\n"
        f"Người Phát Hiện: {element.get('discovered_by', 'N/A')}"
    )

    info_text_area.config(state=NORMAL) # Cho phép chỉnh sửa tạm thời để cập nhật nội dung
    info_text_area.delete(1.0, END)      # Xóa nội dung cũ
    info_text_area.insert(END, info_text) # Chèn thông tin mới
    info_text_area.config(state=DISABLED) # Khóa lại sau khi cập nhật
def add_category_legend():
    """Thêm chú giải màu sắc cho các loại nguyên tố."""
    global theme_bg_color
    legend_frame = Frame(info_frame, bg= theme_bg_color, pady=10)
    legend_frame.grid(row=2, column=0, sticky="ew")

    Label(legend_frame, text="Chú Giải Màu Sắc:", font=("Arial", 11, "bold"), bg="#E0E0E0").grid(row=0, column=0, columnspan=2, pady=5, sticky="w")

    # Định nghĩa các loại nguyên tố và tên hiển thị tiếng Việt
    categories = {
        "kim loại kiềm": "alkali metal",
        "kim loại kiềm thổ": "alkaline earth metal",
        "á kim": "metalloid",
        "phi kim": "nonmetal",
        "khí hiếm": "noble gas",
        "halogen": "halogen",
        "kim loại chuyển tiếp": "transition metal",
        "kim loại sau chuyển tiếp": "post-transition metal",
        "lanthanide": "lanthanide",
        "actinide": "actinide",
        "không xác định": "unknown, probably transition metal" # Dùng một màu đại diện cho unknown
    }

    row_idx = 1
    for display_name, category_key in categories.items():
        color = get_color_by_category(category_key)
        
        # Ô màu sắc
        Label(legend_frame, bg=color, width=3, height=1, bd=1, relief="solid").grid(row=row_idx, column=0, padx=5, pady=1, sticky="w")
        # Nhãn văn bản
        Label(legend_frame, text=display_name.title(), font=("Arial", 9), bg= theme_bg_color).grid(row=row_idx, column=1, padx=0, pady=1, sticky="w")
        row_idx += 1

    legend_frame.grid_columnconfigure(1, weight=1)
def display_periodic_table():
    """Hiển thị các nút nguyên tố lên bảng tuần hoàn."""
    min_cell_size = 50 
    for i in range(10): # Có thể cần nhiều hàng hơn cho lanthanides/actinides
        periodic_table_frame.grid_rowconfigure(i, weight=1, minsize=min_cell_size)
    for i in range(18): # 18 cột cho các nhóm
        periodic_table_frame.grid_columnconfigure(i, weight=1, minsize=min_cell_size)

    # Định nghĩa vị trí bắt đầu cho Lanthanides và Actinides nếu hiển thị riêng
    lant_row_start = 8
    act_row_start = 9
    lant_act_col_offset = 3 # Cột bắt đầu tương đối (cột 3 là cột f-block đầu tiên)

    for element in periodic_elements:
        symbol = element['symbol']
        atomic_number = element['number']
        category = element['category']
        xpos = element['xpos']
        ypos = element['ypos']

        background_color = get_color_by_category(category)

        # Điều chỉnh vị trí cho Lanthanides và Actinides
        if category in ["lanthanide", "actinide"]:
            if category == "lanthanide":
                row = lant_row_start
                col = lant_act_col_offset + (atomic_number - 57) 
            else: # actinide
                row = act_row_start
                col = lant_act_col_offset + (atomic_number - 89)
        else:
            row = ypos - 1
            col = xpos - 1
        element_button = Button(periodic_table_frame,
                                text=f"{atomic_number}\n{symbol}",
                                command=lambda e=element: display_element_info(e),
                                bg=background_color,
                                fg="black",
                                font=("Arial", 9, "bold"),
                                bd=1, relief="raised")
        element_button.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

    # Thêm các nút giữ chỗ cho Lanthanides và Actinides ở vị trí ban đầu (nếu cần)
    placeholder_la_button = Button(periodic_table_frame, text="57-71\nLa-Lu", bg="#D0D0D0", fg="black",
                                   font=("Arial", 9, "bold"),
                                   bd=1, relief="raised")
    placeholder_la_button.grid(row=5, column=2, padx=1, pady=1, sticky="nsew")

    placeholder_ac_button = Button(periodic_table_frame, text="89-103\nAc-Lr", bg="#D0D0D0", fg="black",
                                   font=("Arial", 9, "bold"),
                                   bd=1, relief="raised")
    placeholder_ac_button.grid(row=6, column=2, padx=1, pady=1, sticky="nsew")
def load_or_restore_element_data(url, current_loading_label, current_root):

    global periodic_elements

    if os.path.exists(cache_file):
        try:
            current_loading_label.config(text="Đang tải dữ liệu từ cache...")
            current_root.update_idletasks()
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'elements' in data and isinstance(data['elements'], list):
                periodic_elements = sorted(data['elements'], key=lambda x: x['number'])
                current_loading_label.config(text="Đã tải dữ liệu từ cache.")
                return True
            else:
                print("Dữ liệu cache không hợp lệ, sẽ tải lại.")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Lỗi khi đọc file cache: {e}. Sẽ thử tải lại từ internet.")

    current_loading_label.config(text="Đang tải dữ liệu từ internet...")
    current_root.update_idletasks()
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        json_data_chunks = []
        for chunk in response.iter_content(chunk_size=8192):
            json_data_chunks.append(chunk)

        data = json.loads(b''.join(json_data_chunks).decode('utf-8'))
        periodic_elements = sorted(data['elements'], key=lambda x: x['number'])

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Đã lưu dữ liệu vào cache: {cache_file}")
        except IOError as e:
            print(f"Lỗi khi lưu dữ liệu vào cache: {e}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi tải dữ liệu từ internet: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"Lỗi giải mã JSON từ internet: {e}")
        return False
def create_widgets(current_root, current_loading_frame):
    """Tạo và bố trí các widget chính của ứng dụng."""
    global periodic_table_frame, info_frame, info_text_area, theme_bg_color

    current_loading_frame.destroy()

    current_root.grid_rowconfigure(0, weight=1)
    current_root.grid_columnconfigure(0, weight=4)
    current_root.grid_columnconfigure(1, weight=1)

    periodic_table_frame = Frame(current_root, padx=10, pady=10) 
    periodic_table_frame.config(bg = theme_bg_color) # Đặt màu nền cho khung bảng tuần hoàn
    periodic_table_frame.grid(row=0, column=0, sticky="nsew")

    info_frame = Frame(current_root, width=300, padx=10, pady=10, bd=2, relief="groove")
    info_frame.config(bg=theme_bg_color) # Đặt màu nền cho khung thông tin
    info_frame.grid(row=0, column=1, sticky="nsew")
    info_frame.grid_propagate(False)

    info_frame.grid_rowconfigure(1, weight=1)
    info_frame.grid_columnconfigure(0, weight=1)

    # Label và ScrolledText có thể không cần đặt bg/fg nếu muốn theme kiểm soát hoàn toàn
    info_label = Label(info_frame, text="Thông tin Nguyên tố", font=("Arial", 14, "bold"))
    info_label.config(bg=theme_bg_color, fg=style.lookup("TLabel", "foreground")) # Đặt màu nền và chữ cho nhãn
    info_label.grid(row=0, column=0, pady=10)

    info_text_area = scrolledtext.ScrolledText(info_frame, wrap=WORD, font=("Arial", 10), width=35, height=25,
                                             bd=1, relief="solid", padx=5, pady=5)
    info_text_area.grid(row=1, column=0, pady=5, sticky="nsew")
    info_text_area.config(bg=style.lookup("TText", "background"), fg=style.lookup("TText", "foreground")) # Lấy màu nền và chữ từ theme cho Text
    info_text_area.config(state=DISABLED)

    display_periodic_table()
    add_category_legend()
def bang_tuan_hoan():
    global loading_frame, loading_label, root, theme_bg_color, style
    if not root: # 2 Dòng này nhằm đảm bảo của sổ chính tồn tại 
        return
    # Tạo cửa sổ phụ cho tính năng 11     
    tinh_nang_12 = tk.Toplevel(root) # liên kết với của sổ chính bằng root
    tinh_nang_12.title("12. Bảng tuần hoàn hóa học") # Thiết lập tên cho cửa sổ
    tinh_nang_12.resizable(False, False) # Loại bỏ khả năng thu phóng của cửa sổ
    # Đoạn này dùng để thay đổi giao diện 
    style = ThemedStyle(tinh_nang_12)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_12.config(bg=theme_bg_color)

    loading_frame = Frame(tinh_nang_12)
    loading_frame.config(bg=theme_bg_color) # Đặt màu nền cho khung tải 
    loading_frame.pack(expand=True, fill=BOTH)

    loading_label = Label(loading_frame, text="Đang khởi tạo...", font=("Arial", 16, "bold"))
    loading_label.config(bg=theme_bg_color, fg=style.lookup("TLabel", "foreground"))
    loading_label.pack(pady=50)

    tinh_nang_12.update_idletasks()

    data_loaded_successfully = load_or_restore_element_data(
        "https://raw.githubusercontent.com/Bowserinator/Periodic-Table-JSON/master/PeriodicTableJSON.json",
        loading_label, tinh_nang_12
    )

    if not data_loaded_successfully:
        messagebox.showerror("Lỗi", "Không thể tải hoặc khôi phục dữ liệu bảng tuần hoàn. Vui lòng kiểm tra kết nối internet hoặc file cache.")
        tinh_nang_12.destroy()
        return
    
    create_widgets(tinh_nang_12, loading_frame)
###################################################################################
def doi_loi(): # Tính năng 13: Đôi lời của nhà sản xuất
    if not root: # 2 Dòng này nhằm đảm bảo cảu sổ chính tồn tại 
        return
    
    tinh_nang_13 = tk.Toplevel(root)
    tinh_nang_13.title("13. Đôi lời của nhà sản xuất")
    tinh_nang_13.resizable(False, False)
    # Áp dụng chủ đề cho cửa sổ Toplevel
    style = ThemedStyle(tinh_nang_13)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_13.config(bg=theme_bg_color)
    # Nội dung thông điệp
    message = (
        "Chào mừng bạn đến với ứng dụng của chúng tôi!\n\n" # Thêm dòng trống để dễ đọc
        "Chúng tôi đã tạo ra ứng dụng này với mong muốn mang lại những tính năng hữu ích "
        "và trải nghiệm thú vị cho bạn.\n\n" # Ngắt dòng hợp lý
        "Nếu bạn có bất kỳ câu hỏi, góp ý, hoặc cần hỗ trợ, "
        "xin đừng ngần ngại liên hệ với chúng tôi.\n\n" # Lời kêu gọi hành động rõ ràng
        "Chân thành cảm ơn bạn đã tin tưởng và sử dụng ứng dụng!\n\n"
        "Trân trọng,\n\n"
        "Đội ngũ sản xuất và phát triển: Đinh Viết Phúc và Ngô Văn Anh Khoa." 
    )
    ttk.Label(tinh_nang_13, text=message, wraplength=400, justify="left", font=("Arial", 10)).pack(padx=20, pady=20) 
###################################################################################
if __name__ == "__main__":

    root = ThemedTk(theme=current_theme)
    root.title("App đa năng")
    root.resizable(False, False)
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    style = ThemedStyle(root)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    root.config(bg=theme_bg_color)

    ttk.Label(frm, text="Menu", anchor="center", font=('Arial', 14, 'bold')).grid(column=0, row=0, columnspan=2, sticky="ew", pady=5) 
    ttk.Button(frm, text="1.Đồng hồ và lịch", command=clock).grid(column=0, row=1, columnspan=2, sticky="ew", pady=2)
  #  ttk.Button(frm, text="2.Máy ảnh", command=camera).grid(column=0, row=2, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="3.Gửi thư", command=gui_thu).grid(column=0, row=3, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="4.Máy tính", command=may_tinh).grid(column=0, row=4, columnspan=2, sticky="ew", pady=2)
  #  ttk.Button(frm, text="5.Chuyển âm thanh thành văn bản", command=chuyen_am_thanh_thanh_van_ban).grid(column=0, row=5, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="6. Tìm kiếm thông tin (wikipedia) ", command=tim_kiem_thong_tin).grid(column=0, row=6, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="7. Đồng hồ đếm ngược", command=dem_nguoc).grid(column=0, row=7, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="8. Soạn thảo văn bản", command=van_ban).grid(column=0, row=9, columnspan=2, sticky="ew", pady=2)
 #   ttk.Button(frm, text="9. Máy phát nhạc và video ", command=may_phat_nhac_va_video).grid(column=0, row=8, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="10. Thời tiết", command=thoi_tiet).grid(column=0, row=10, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="11.Thay đổi giao diện người dùng ", command=giao_dien).grid(column=0, row=11, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="12.Bảng tuần hoàn hóa học", command=bang_tuan_hoan).grid(column=0, row=12, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="13. Đôi lời của nhà sản xuất ", command=doi_loi).grid(column=0, row=13, columnspan=2, sticky="ew", pady=2)

    root.mainloop()
