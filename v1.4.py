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
                     Menu,Frame, Button, DISABLED, NORMAL, WORD, BOTH)
import periodictable as pt
from datetime import datetime, date
from tkcalendar import Calendar 
from ttkthemes import ThemedTk, ThemedStyle
import gzip 
import json
import requests
from unidecode import unidecode
import psutil
import platform
import subprocess
import re
import folium
import pygame
from googletrans import Translator, LANGUAGES
import asyncio 
import sys
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
    tinh_nang_1.title("1.Đổng hồ và lịch")
    tinh_nang_1.resizable(False, False)
    try:
        tinh_nang_1.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
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

    # Thêm Label để hiển thị thông báo trạng thái
    status_label = ttk.Label(frame_left, text="", font=("Helvetica", 10), foreground="green")
    status_label.grid(column=0, row=2, pady=2, sticky="w")

    def save_note():
        selected_date = cal.get_date()
        note_text = note_entry.get("1.0", tk.END).strip()
        save_notes(selected_date, note_text)
        print(f"Ghi chú cho {selected_date}: {note_text}")
        status_label.config(text=f"Đã lưu ghi chú cho ngày {selected_date}!") # Cập nhật thông báo
        # Xóa thông báo sau vài giây
        tinh_nang_1.after(3000, lambda: status_label.config(text=""))


    ttk.Button(frame_left, text="Lưu ghi chú", command=save_note).grid(column=0, row=3, pady=10) # Thay đổi row của nút

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
        status_label.config(text="") # Xóa thông báo khi chọn ngày khác

    cal.bind("<<CalendarSelected>>", lambda event: update_note())

    update_clock_in_toplevel()
    open_toplevels.append(tinh_nang_1)
    tinh_nang_1.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_1))
###################################################################################
recording = False
video_writer = None
status_label = None
def camera(): # Tính năng 2: Máy ảnh
    global recording, video_writer
    if not root:
        return
    # Tạo cửa sổ phụ cho tính năng 1
    tinh_nang_2 = tk.Toplevel(root)
    tinh_nang_2.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_2))
    tinh_nang_2.title("2. Máy ảnh")
    try:
        tinh_nang_2.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
    tinh_nang_2.resizable(False, False)
    # Áp dụng chủ đề cho cửa sổ Toplevel
    style = ThemedStyle(tinh_nang_2)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_2.config(bg=theme_bg_color)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        # Nếu camera không mở được, hiển thị lỗi và đóng cửa sổ
        messagebox.showerror("Lỗi Camera", "Không thể mở camera. Vui lòng kiểm tra kết nối hoặc quyền truy cập.", parent=tinh_nang_2)
        tinh_nang_2.destroy()
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frame_container = ttk.Frame(tinh_nang_2, padding=20)
    frame_container.grid(row=0, column=0, columnspan=2)

    label = ttk.Label(frame_container)
    label.grid(column=0, row=0, columnspan=2, sticky="ew")

    # Tạo thanh trạng thái và đặt nó ngay dưới label hiển thị video (row=1)
    status_label = ttk.Label(tinh_nang_2, text="Sẵn sàng", anchor="w", font=("Segoe UI", 10), background=theme_bg_color)
    status_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

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
        
        if tinh_nang_2.winfo_exists():
            tinh_nang_2.after(10, update_frame)
        else:
            cap.release()
            if video_writer is not None:
                video_writer.release()

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
            status_label.config(text=f"Ảnh đã được lưu: {filename}", foreground="green")
            tinh_nang_2.after(3000, lambda: status_label.config(text="")) # Xóa thông báo sau 3 giây
            print(f"Ảnh đã được lưu: {filename}")

    def quay_video():
        global recording, video_writer
        if not recording:
            recording = True
            filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            
            video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (frame_width, frame_height))
            
            if not video_writer.isOpened():
                status_label.config(text="Lỗi: Không thể tạo file ghi video. Kiểm tra quyền truy cập.", foreground="red")
                tinh_nang_2.after(3000, lambda: status_label.config(text=""))
                recording = False
                video_writer = None
                return

            video_button.config(text="Dừng quay") # Thay đổi tên nút
            # Không hiển thị thông báo trên status bar khi quay video
            print(f"Bắt đầu quay video: {filename}")
        else:
            recording = False
            if video_writer is not None:
                video_writer.release()
                # Không hiển thị thông báo trên status bar khi dừng quay video
                print("Dừng quay video")
            video_writer = None
            video_button.config(text="Quay video") # Thay đổi tên nút về trạng thái ban đầu

    def mo_kho_luu_tru():
        try:
            path = os.getcwd()
            os.startfile(path)
            status_label.config(text=f"Đang mở kho lưu trữ: {path}", foreground="black")
            tinh_nang_2.after(3000, lambda: status_label.config(text=""))
        except Exception as e:
            status_label.config(text=f"Lỗi: Không thể mở kho lưu trữ: {e}", foreground="red")
            tinh_nang_2.after(3000, lambda: status_label.config(text=""))

    ttk.Button(tinh_nang_2, text="Chụp ảnh", command=chup_anh).grid(column=0, row=2, columnspan=2, sticky="ew", padx=10, pady=2)
    video_button = ttk.Button(tinh_nang_2, text="Quay video", command=quay_video)
    video_button.grid(column=0, row=3, columnspan=2, sticky="ew", padx=10, pady=2)
    ttk.Button(tinh_nang_2, text="Kho lưu trữ", command=mo_kho_luu_tru).grid(column=0, row=4, columnspan=2, sticky="ew", padx=10, pady=2) # Thay đổi row của nút kho lưu trữ

    # tinh_nang_2.winfo_toplevel().protocol("WM_DELETE_WINDOW", on_closing)
    update_frame()
    open_toplevels.append(tinh_nang_2)
    tinh_nang_2.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_2))
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
    try:
        tinh_nang_3.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
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
    open_toplevels.append(tinh_nang_3)
    tinh_nang_3.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_3))
###################################################################################
def doc_dien_tro():
    if not root: # 2 Dòng này nhằm đảm bảo của sổ chính tồn tại 
        return
    # Tạo cửa sổ phụ cho tính năng 11     
    tinh_nang_4 = tk.Toplevel(root) # liên kết với của sổ chính bằng root
    tinh_nang_4.title("4.Đọc giá trị điện trở ")
    try:
        tinh_nang_4.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
    tinh_nang_4.resizable(False, False)
    # Đoạn này dùng để thay đổi giao diện 
    style = ThemedStyle(tinh_nang_4)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_4.config(bg=theme_bg_color)
    tinh_nang_4.title("4.Đọc giá trị điện trở ")
    tinh_nang_4.resizable(False, False)

    # Cấu hình grid cho cửa sổ Toplevel chính
    # Tạo 3 cột: 0 (label), 1 (combobox), 2 (button, but for frames only 1 wide)
    tinh_nang_4.columnconfigure(0, weight=1) # Cột duy nhất để các frame trải dài

    # Bảng giá trị màu cho điện trở
    color_codes = {
        "Đen": 0, "Nâu": 1, "Đỏ": 2, "Cam": 3, "Vàng": 4,
        "Lục": 5, "Lam": 6, "Tím": 7, "Xám": 8, "Trắng": 9
    }

    multiplier_codes = {
        "Đen": 1, "Nâu": 10, "Đỏ": 100, "Cam": 1000, "Vàng": 10000,
        "Lục": 100000, "Lam": 1000000, "Tím": 10000000,
        "Vàng Kim loại": 0.1, "Bạc Kim loại": 0.01
    }

    tolerance_codes = {
        "Nâu": "±1%", "Đỏ": "±2%", "Lục": "±0.5%", "Lam": "±0.25%",
        "Tím": "±0.1%", "Xám": "±0.05%",
        "Vàng Kim loại": "±5%", "Bạc Kim loại": "±10%"
    }

    # Tạo các biến lưu trữ lựa chọn màu
    band1_var = tk.StringVar(tinh_nang_4)
    band2_var = tk.StringVar(tinh_nang_4)
    band3_var = tk.StringVar(tinh_nang_4) # Dùng cho điện trở 5 vòng
    multiplier_var = tk.StringVar(tinh_nang_4)
    tolerance_var = tk.StringVar(tinh_nang_4)
    num_bands_var = tk.StringVar(tinh_nang_4, value="4") # Mặc định 4 vòng

    # Options cho Dropdown
    band1_color_options = ["", "Nâu", "Đỏ", "Cam", "Vàng", "Lục", "Lam", "Tím", "Xám", "Trắng"]
    common_color_options = ["", "Đen", "Nâu", "Đỏ", "Cam", "Vàng", "Lục", "Lam", "Tím", "Xám", "Trắng"]
    multiplier_color_options = ["", "Đen", "Nâu", "Đỏ", "Cam", "Vàng", "Lục", "Lam", "Tím", "Vàng Kim loại", "Bạc Kim loại"]
    tolerance_color_options = ["", "Nâu", "Đỏ", "Lục", "Lam", "Tím", "Xám", "Vàng Kim loại", "Bạc Kim loại"]

    # --- Phần hiển thị kết quả ---
    result_frame = ttk.LabelFrame(tinh_nang_4, text="Kết Quả")
    result_frame.grid(row=0, column=0, padx=15, pady=10, sticky="ew") # sticky="ew" để lấp đầy theo chiều ngang
    result_frame.columnconfigure(0, weight=1) # Để label kết quả căn giữa

    result_label_text = tk.StringVar(tinh_nang_4)
    result_label_text.set("Giá trị điện trở sẽ hiển thị ở đây.")
    result_label = ttk.Label(result_frame, textvariable=result_label_text, font=("Arial", 12, "bold"))
    result_label.grid(row=0, column=0, padx=10, pady=10) # Grid trong result_frame

    # --- Phần lựa chọn số vòng ---
    band_selection_frame = ttk.LabelFrame(tinh_nang_4, text="Chọn Số Vòng Điện Trở")
    band_selection_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
    band_selection_frame.columnconfigure(0, weight=1) # Để radio buttons căn trái

    ttk.Radiobutton(band_selection_frame, text="4 Vòng (Đầu số - Đầu số - Hệ số nhân - Dung sai)",
                    variable=num_bands_var, value="4", command=lambda: update_bands_visibility("4")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
    ttk.Radiobutton(band_selection_frame, text="5 Vòng (Đầu số - Đầu số - Đầu số - Hệ số nhân - Dung sai)",
                    variable=num_bands_var, value="5", command=lambda: update_bands_visibility("5")).grid(row=1, column=0, sticky="w", padx=10, pady=5)

    # --- Phần nhập màu ---
    color_input_frame = ttk.LabelFrame(tinh_nang_4, text="Chọn Màu Sắc Các Vòng")
    color_input_frame.grid(row=2, column=0, padx=15, pady=10, sticky="ew")

    # Cấu hình grid cho color_input_frame để các cột tự co giãn
    color_input_frame.columnconfigure(0, weight=1) # Cột Label
    color_input_frame.columnconfigure(1, weight=2) # Cột Combobox lớn hơn

    # Hàm trợ giúp để tạo Label và Combobox
    def create_color_band_widgets(parent_frame, label_text, textvariable, options):
        label = ttk.Label(parent_frame, text=label_text, width=18)
        dropdown = ttk.Combobox(parent_frame, textvariable=textvariable, values=options, state="readonly")
        dropdown.set("") # Giá trị mặc định trống
        return label, dropdown

    # Tạo tất cả các widget và lưu trữ chúng (chưa grid vào đây)
    band1_label, band1_dropdown = create_color_band_widgets(color_input_frame, "Vòng 1 (Số thứ 1):", band1_var, band1_color_options)
    band2_label, band2_dropdown = create_color_band_widgets(color_input_frame, "Vòng 2 (Số thứ 2):", band2_var, common_color_options)
    band3_label, band3_dropdown = create_color_band_widgets(color_input_frame, "Vòng 3 (Số thứ 3):", band3_var, common_color_options)
    multiplier_label, multiplier_dropdown = create_color_band_widgets(color_input_frame, "Vòng Hệ số nhân:", multiplier_var, multiplier_color_options)
    tolerance_label, tolerance_dropdown = create_color_band_widgets(color_input_frame, "Vòng Dung sai:", tolerance_var, tolerance_color_options)

    # Hàm cập nhật hiển thị các vòng sử dụng grid_forget/grid
    def update_bands_visibility(selected_bands):
        # Reset tất cả các lựa chọn màu khi chuyển đổi số vòng
        band1_var.set("")
        band2_var.set("")
        band3_var.set("")
        multiplier_var.set("")
        tolerance_var.set("")
        result_label_text.set("Giá trị điện trở sẽ hiển thị ở đây.") # Reset kết quả

        # Ẩn tất cả các widget của vòng màu trước
        for widget_label, widget_dropdown in [
            (band1_label, band1_dropdown),
            (band2_label, band2_dropdown),
            (band3_label, band3_dropdown),
            (multiplier_label, multiplier_dropdown),
            (tolerance_label, tolerance_dropdown)
        ]:
            widget_label.grid_forget()
            widget_dropdown.grid_forget()

        # Sau đó hiển thị lại theo thứ tự và điều kiện mong muốn
        current_row = 0
        band1_label.grid(row=current_row, column=0, padx=5, pady=2, sticky="w")
        band1_dropdown.grid(row=current_row, column=1, padx=5, pady=2, sticky="ew")
        current_row += 1

        band2_label.grid(row=current_row, column=0, padx=5, pady=2, sticky="w")
        band2_dropdown.grid(row=current_row, column=1, padx=5, pady=2, sticky="ew")
        current_row += 1

        if selected_bands == "5":
            band3_label.grid(row=current_row, column=0, padx=5, pady=2, sticky="w")
            band3_dropdown.grid(row=current_row, column=1, padx=5, pady=2, sticky="ew")
            current_row += 1
        
        multiplier_label.grid(row=current_row, column=0, padx=5, pady=2, sticky="w")
        multiplier_dropdown.grid(row=current_row, column=1, padx=5, pady=2, sticky="ew")
        current_row += 1

        tolerance_label.grid(row=current_row, column=0, padx=5, pady=2, sticky="w")
        tolerance_dropdown.grid(row=current_row, column=1, padx=5, pady=2, sticky="ew")
        current_row += 1 # Không dùng nữa nhưng giữ cho đủ

    # Cập nhật hiển thị ban đầu dựa trên giá trị mặc định của num_bands_var
    update_bands_visibility(num_bands_var.get())

    def calculate_resistor_value():
        try:
            current_num_bands = num_bands_var.get()

            # Lấy giá trị màu
            val1_str = band1_var.get()
            val2_str = band2_var.get()
            mult_str = multiplier_var.get()
            tol_str = tolerance_var.get()

            # Kiểm tra các trường bắt buộc
            if not val1_str or not val2_str or not mult_str or not tol_str:
                messagebox.showerror("Lỗi", "Vui lòng chọn màu cho tất cả các vòng bắt buộc (Vòng 1, Vòng 2, Hệ số nhân, Dung sai).")
                result_label_text.set("Lỗi: Vui lòng hoàn tất các lựa chọn.")
                return
            
            if current_num_bands == "5" and not band3_var.get():
                messagebox.showerror("Lỗi", "Bạn đã chọn điện trở 5 vòng. Vui lòng chọn màu cho Vòng 3.")
                result_label_text.set("Lỗi: Vui lòng hoàn tất các lựa chọn.")
                return

            # Kiểm tra Vòng 1 không được là Đen
            if val1_str == "Đen":
                messagebox.showerror("Lỗi", "Vòng 1 (số thứ nhất) không thể là màu Đen.")
                result_label_text.set("Lỗi: Vòng 1 không hợp lệ.")
                return

            val1 = color_codes[val1_str]
            val2 = color_codes[val2_str]
            mult_val = multiplier_codes[mult_str]
            tol_val = tolerance_codes[tol_str]

            resistance = 0
            if current_num_bands == "4":
                resistance = (val1 * 10 + val2) * mult_val
            else: # 5 vòng
                val3_str = band3_var.get()
                val3 = color_codes[val3_str]
                resistance = (val1 * 100 + val2 * 10 + val3) * mult_val

            # Chuyển đổi sang đơn vị phù hợp
            display_value = ""
            if resistance >= 1_000_000_000: # GigaOhm
                display_value = f"{resistance / 1_000_000_000:.2f} GΩ"
            elif resistance >= 1_000_000: # MegaOhm
                display_value = f"{resistance / 1_000_000:.2f} MΩ"
            elif resistance >= 1_000: # KiloOhm
                display_value = f"{resistance / 1_000:.2f} kΩ"
            elif resistance < 1: # Để xử lý các giá trị nhỏ hơn 1 Ohm (do hệ số nhân 0.1, 0.01)
                if resistance * 1000 >= 1: # Nếu là miliOhm
                    display_value = f"{resistance * 1000:.2f} mΩ"
                elif resistance * 1_000_000 >= 1: # Nếu là microOhm
                    display_value = f"{resistance * 1_000_000:.2f} µΩ"
                else: # Giá trị quá nhỏ, vẫn hiển thị là Ohm
                    display_value = f"{resistance:.2f} Ω"
            else: # Ohm
                display_value = f"{resistance:.2f} Ω"

            result_label_text.set(f"Giá trị: {display_value}\nDung sai: {tol_val}")

        except KeyError as e:
            messagebox.showerror("Lỗi", f"Có vẻ bạn đã chọn một màu không hợp lệ hoặc thiếu. Vui lòng kiểm tra lại: {e}")
            result_label_text.set("Lỗi: Kiểm tra lại các lựa chọn màu.")
        except ValueError as e:
            messagebox.showerror("Lỗi", f"Dữ liệu nhập không hợp lệ: {e}. Vui lòng kiểm tra lại các lựa chọn.")
            result_label_text.set("Lỗi: Vui lòng thử lại.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi không mong muốn: {e}")
            result_label_text.set("Lỗi: Vui lòng thử lại.")

    # Nút tính toán
    button_frame = ttk.Frame(tinh_nang_4)
    button_frame.grid(row=3, column=0, pady=10, sticky="ew") # Grid vào cửa sổ chính, sau color_input_frame
    button_frame.columnconfigure(0, weight=1) # Để nút căn giữa

    calculate_button = ttk.Button(button_frame, text="Tính Giá Trị Điện Trở", command=calculate_resistor_value, width=25)
    calculate_button.grid(row=0, column=0, padx=10)
    open_toplevels.append(tinh_nang_4)
    tinh_nang_4.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_4))
###################################################################################
global_last_disk_io_counters = psutil.disk_io_counters()
global_last_time = time.time()
def thong_tin_va_hieu_nang():
    if not root:
        return

    # --- Thiết lập cửa sổ phụ và các widget GUI TRƯỚC HẾT ---
    tinh_nang_5 = tk.Toplevel(root)
    tinh_nang_5.title("5. Thông tin và hiệu năng máy tính")
    try:
        tinh_nang_5.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
    tinh_nang_5.resizable(False, False) # Vô hiệu hóa thay đổi kích thước

    style = ThemedStyle(tinh_nang_5)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_5.config(bg=theme_bg_color)

    notebook = ttk.Notebook(tinh_nang_5)
    notebook.pack(pady=10, fill="both", expand=True)

    static_info_tab = ttk.Frame(notebook)
    notebook.add(static_info_tab, text="Thông tin hệ thống")

    canvas_static = tk.Canvas(static_info_tab)
    scrollbar_static = ttk.Scrollbar(static_info_tab, orient="vertical", command=canvas_static.yview)
    static_info_frame = ttk.Frame(canvas_static) # Frame thực sự chứa nội dung tĩnh

    static_info_frame.bind("<Configure>", lambda e: canvas_static.configure(scrollregion=canvas_static.bbox("all")))
    canvas_static.create_window((0, 0), window=static_info_frame, anchor="nw")
    canvas_static.configure(yscrollcommand=scrollbar_static.set)
    canvas_static.pack(side="left", fill="both", expand=True)
    scrollbar_static.pack(side="right", fill="y")

    performance_tab = ttk.Frame(notebook)
    notebook.add(performance_tab, text="Hiệu năng thời gian thực")

    # Labels để hiển thị thông tin hiệu năng động (được khai báo Cục bộ trong hàm này)
    # Các biến này cần được định nghĩa TRƯỚC KHI update_performance_info được gọi
    ttk.Label(performance_tab, text="Thông số hiệu năng thời gian thực", font=("Arial", 14, "bold")).pack(pady=(10, 5))

    cpu_label = ttk.Label(performance_tab, text="Sử dụng CPU: Đang tải...", font=("Arial", 12))
    cpu_label.pack(anchor='w', padx=10, pady=5)

    ram_label = ttk.Label(performance_tab, text="Sử dụng RAM: Đang tải...", font=("Arial", 12))
    ram_label.pack(anchor='w', padx=10, pady=5)

    disk_speed_label = ttk.Label(performance_tab, text="Tốc độ ổ đĩa: Đang tải...", font=("Arial", 12))
    disk_speed_label.pack(anchor='w', padx=10, pady=5)

    cpu_temp_label = ttk.Label(performance_tab, text="Nhiệt độ CPU: Đang tải...", font=("Arial", 12))
    cpu_temp_label.pack(anchor='w', padx=10, pady=5)

    # --- Định nghĩa các hàm lấy thông tin hệ thống (Static) ---
    def get_cpu_info():
        info = {}
        info['Loại CPU'] = platform.processor()
        info['Số nhân vật lý'] = psutil.cpu_count(logical=False)
        info['Số luồng'] = psutil.cpu_count(logical=True)
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                info['Nhiệt độ CPU'] = f"{temps['coretemp'][0].current}°C"
            elif 'cpu_thermal' in temps:
                info['Nhiệt độ CPU'] = f"{temps['cpu_thermal'][0].current}°C"
            else:
                info['Nhiệt độ CPU'] = "Không khả dụng"
        except Exception:
            info['Nhiệt độ CPU'] = "Không khả dụng"
        return info

    def get_ram_static_info():
        info = {}
        svmem = psutil.virtual_memory()
        info['Tổng dung lượng RAM'] = f"{svmem.total / (1024**3):.2f} GB"
        return info

    def get_disk_static_info():
        info = {}
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info[f'Ổ đĩa {partition.device}'] = {
                    'Tổng dung lượng': f"{usage.total / (1024**3):.2f} GB",
                    'Đã sử dụng': f"{usage.used / (1024**3):.2f} GB",
                    'Còn trống': f"{usage.free / (1024**3):.2f} GB",
                    'Phần trăm sử dụng': f"{usage.percent}%"
                }
            except PermissionError:
                continue
        return info

    def get_gpu_info():
        info = {}
        if platform.system() == "Windows":
            try:
                gpu_name_cmd = "Get-WmiObject win32_VideoController | Select-Object -ExpandProperty Name"
                gpu_names = subprocess.run(["powershell", "-Command", gpu_name_cmd], capture_output=True, text=True).stdout.strip().split('\n')
                info['Loại Card đồ họa'] = ", ".join([name.strip() for name in gpu_names if name.strip()]) if gpu_names else "Không xác định"

                gpu_vram_cmd = "Get-WmiObject win32_VideoController | Select-Object -ExpandProperty AdapterRam"
                gpu_vram_raw = subprocess.run(["powershell", "-Command", gpu_vram_cmd], capture_output=True, text=True).stdout.strip().split('\n')
                gpu_vram = [int(ram) / (1024**2) for ram in gpu_vram_raw if ram.strip().isdigit()]
                info['Dung lượng Bộ nhớ GPU'] = ", ".join([f"{vram:.0f} MB" for vram in gpu_vram]) if gpu_vram else "Không xác định"

                info['Tốc độ xung nhịp GPU'] = "Không khả dụng qua PowerShell"
            except Exception as e:
                info['Lỗi lấy thông tin GPU'] = str(e)
                info['Loại Card đồ họa'] = "Không xác định"
                info['Dung lượng Bộ nhớ GPU'] = "Không xác định"
                info['Tốc độ xung nhịp GPU'] = "Không xác định"
        elif platform.system() == "Linux":
            try:
                output = subprocess.check_output("lspci | grep -i vga", shell=True).decode('utf-8')
                gpu_name_match = re.search(r': (.+ \(rev.+?\))', output)
                info['Loại Card đồ họa'] = gpu_name_match.group(1).strip() if gpu_name_match else "Không xác định"
                info['Dung lượng Bộ nhớ GPU'] = "Thường khó lấy chính xác qua lspci"
                info['Tốc độ xung nhịp GPU'] = "Không khả dụng qua lspci"
            except Exception:
                info['Loại Card đồ họa'] = "Không xác định"
                info['Dung lượng Bộ nhớ GPU'] = "Không xác định"
                info['Tốc độ xung nhịp GPU'] = "Không khả dụng"
        else: # MacOS
            info['Loại Card đồ họa'] = "Hãy kiểm tra thông tin hệ thống"
            info['Dung lượng Bộ nhớ GPU'] = "Hãy kiểm tra thông tin hệ thống"
            info['Tốc độ xung nhịp GPU'] = "Hãy kiểm tra thông tin hệ thống"
        return info

    def get_system_summary():
        summary = {}
        summary['Hệ điều hành'] = platform.system()
        summary['Phiên bản OS'] = platform.release()
        summary['Kiến trúc'] = platform.machine()
        return summary

    # --- Định nghĩa hàm cập nhật thông tin hiệu năng động ---
    def update_performance_info():
        global global_last_disk_io_counters, global_last_time
        nonlocal cpu_label, ram_label, disk_speed_label, cpu_temp_label # Khai báo nonlocal để truy cập nhãn

        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_freq = psutil.cpu_freq()
        cpu_current_freq = f"{cpu_freq.current / 1000:.2f} GHz" if cpu_freq else "N/A"
        cpu_label.config(text=f"Sử dụng CPU: {cpu_percent:.1f}% ({cpu_current_freq})")

        # RAM Usage
        svmem = psutil.virtual_memory()
        ram_used_gb = svmem.used / (1024**3)
        ram_percent = svmem.percent
        ram_label.config(text=f"Sử dụng RAM: {ram_used_gb:.2f} GB ({ram_percent:.1f}%)")

        # Disk Read/Write Speed
        current_disk_io = psutil.disk_io_counters()
        current_time = time.time()

        time_diff = current_time - global_last_time
        if time_diff > 0:
            read_bytes_diff = current_disk_io.read_bytes - global_last_disk_io_counters.read_bytes
            write_bytes_diff = current_disk_io.write_bytes - global_last_disk_io_counters.read_bytes # Lỗi đánh máy: phải là write_bytes
            # Sửa lại:
            write_bytes_diff = current_disk_io.write_bytes - global_last_disk_io_counters.write_bytes


            read_speed_mbps = (read_bytes_diff / (1024 * 1024)) / time_diff
            write_speed_mbps = (write_bytes_diff / (1024 * 1024)) / time_diff

            disk_speed_label.config(text=f"Tốc độ ổ đĩa: Đọc: {read_speed_mbps:.2f} MB/s | Ghi: {write_speed_mbps:.2f} MB/s")
        else:
            disk_speed_label.config(text="Tốc độ ổ đĩa: Đang khởi tạo...")

        global_last_disk_io_counters = current_disk_io
        global_last_time = current_time

        # Nhiệt độ CPU
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                temp_text = f"Nhiệt độ CPU: {temps['coretemp'][0].current}°C"
            elif 'cpu_thermal' in temps:
                temp_text = f"Nhiệt độ CPU: {temps['cpu_thermal'][0].current}°C"
            else:
                temp_text = "Nhiệt độ CPU: Không khả dụng"
        except Exception:
            temp_text = "Nhiệt độ CPU: Không khả dụng"
        cpu_temp_label.config(text=temp_text)

        # Lên lịch cập nhật lại sau mỗi 1 giây
        tinh_nang_5.after(1000, update_performance_info)

    # --- Định nghĩa hàm tạo/cập nhật thông tin hệ thống tĩnh ---
    def setup_static_info_display():
        # Xóa nội dung cũ trong frame thông tin tĩnh
        for widget in static_info_frame.winfo_children():
            widget.destroy()

        # Tạo tiêu đề
        ttk.Label(static_info_frame, text="Tổng quan hệ thống", font=("Arial", 14, "bold")).pack(anchor='w', pady=(10, 5))
        for k, v in get_system_summary().items():
            ttk.Label(static_info_frame, text=f"- {k}: {v}", font=("Arial", 10)).pack(anchor='w')

        ttk.Separator(static_info_frame, orient='horizontal').pack(fill='x', pady=10)

        # CPU Static Info
        ttk.Label(static_info_frame, text="Thông tin CPU", font=("Arial", 12, "bold")).pack(anchor='w', pady=(5, 5))
        cpu_info = get_cpu_info()
        for k, v in cpu_info.items():
            if k != 'Nhiệt độ CPU':
                ttk.Label(static_info_frame, text=f"- {k}: {v}", font=("Arial", 10)).pack(anchor='w')

        ttk.Separator(static_info_frame, orient='horizontal').pack(fill='x', pady=10)

        # RAM Static Info
        ttk.Label(static_info_frame, text="Thông tin RAM", font=("Arial", 12, "bold")).pack(anchor='w', pady=(5, 5))
        ram_static_info = get_ram_static_info()
        for k, v in ram_static_info.items():
            ttk.Label(static_info_frame, text=f"- {k}: {v}", font=("Arial", 10)).pack(anchor='w')

        ttk.Separator(static_info_frame, orient='horizontal').pack(fill='x', pady=10)

        # GPU Info
        ttk.Label(static_info_frame, text="Thông tin Card đồ họa (GPU)", font=("Arial", 12, "bold")).pack(anchor='w', pady=(5, 5))
        gpu_info = get_gpu_info()
        for k, v in gpu_info.items():
            ttk.Label(static_info_frame, text=f"- {k}: {v}", font=("Arial", 10)).pack(anchor='w')

        ttk.Separator(static_info_frame, orient='horizontal').pack(fill='x', pady=10)

        # Ổ đĩa Static Info
        ttk.Label(static_info_frame, text="Thông tin Ổ đĩa", font=("Arial", 12, "bold")).pack(anchor='w', pady=(5, 5))
        disk_static_info = get_disk_static_info()
        if disk_static_info:
            for disk, details in disk_static_info.items():
                ttk.Label(static_info_frame, text=f"  {disk}:", font=("Arial", 10, "italic")).pack(anchor='w')
                for k, v in details.items():
                    ttk.Label(static_info_frame, text=f"    - {k}: {v}", font=("Arial", 10)).pack(anchor='w')
        else:
            ttk.Label(static_info_frame, text="Không tìm thấy thông tin ổ đĩa.", font=("Arial", 10)).pack(anchor='w')

    # --- Gọi các hàm khởi tạo sau khi tất cả widgets và hàm con đã được định nghĩa ---
    setup_static_info_display()
    update_performance_info()
    open_toplevels.append(tinh_nang_5)
    tinh_nang_5.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_5))
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
    tinh_nang_6.title("6.Tìm kiếm thông tin (wikipedia)")
    tinh_nang_6.geometry("600x400")

    try:
        tinh_nang_6.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")

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
    open_toplevels.append(tinh_nang_6)
    tinh_nang_6.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_6))
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
    try:
        tinh_nang_7.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
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
    open_toplevels.append(tinh_nang_7)
    tinh_nang_7.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_7))
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
    try:
        tinh_nang_8.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
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
    open_toplevels.append(tinh_nang_8)
    tinh_nang_8.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_8))
###################################################################################
pygame.init() 
pygame.mixer.init()
# Biến trạng thái toàn cục cho máy phát nhạc
current_index = None
paused = False
playing = False
history = [] # Lịch sử sẽ được tải khi cửa sổ mở
SONG_END_EVENT = pygame.USEREVENT + 1
HISTORY_FILE = "history.txt"

# Hàm xử lý đóng cửa sổ Toplevel
def on_toplevel_close(toplevel_window):
    global playing, paused, current_index
    if playing:
        pygame.mixer.music.stop()
        playing = False
        paused = False
        current_index = None # Đặt lại chỉ mục khi đóng trình phát
    pygame.mixer.music.set_endevent(0) # Hủy sự kiện kết thúc bài hát
    toplevel_window.destroy()
    if toplevel_window in open_toplevels:
        open_toplevels.remove(toplevel_window)

# --- Hàm chính cho máy phát nhạc ---
def may_phat_nhac(root, current_theme, open_toplevels):
    global current_index, paused, playing, history, SONG_END_EVENT

    # Tải lịch sử khi mở cửa sổ mới
    def load_history_internal():
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding='utf-8') as f:
                return [line for line in f.read().splitlines() if line.strip()]
        return []
    
    history = load_history_internal() # Tải lịch sử vào biến global history

    def save_history():
        with open(HISTORY_FILE, "w", encoding='utf-8') as f:
            for file in history:
                f.write(file + "\n")

    def update_button_states():
        # Cập nhật trạng thái nút điều khiển phát/tạm dừng/dừng
        if playing:
            btn_pause.config(text="Tạm dừng" if not paused else "Tiếp tục", state=tk.NORMAL)
            btn_stop.config(state=tk.NORMAL)
        else:
            btn_pause.config(text="Tạm dừng", state=tk.DISABLED)
            btn_stop.config(state=tk.DISABLED)
        
        # Kích hoạt/vô hiệu hóa các nút điều hướng dựa trên lịch sử
        if len(history) > 0:
            btn_play_all.config(state=tk.NORMAL)
            # Nút Next/Previous chỉ được kích hoạt nếu có bài hát đang phát (current_index không None)
            # HOẶC nếu có lịch sử (để có thể chọn bài đầu tiên và phát)
            btn_next.config(state=tk.NORMAL) 
            btn_prev.config(state=tk.NORMAL)
        else:
            btn_play_all.config(state=tk.DISABLED)
            btn_next.config(state=tk.DISABLED)
            btn_prev.config(state=tk.DISABLED)

    def update_history_display():
        for iid in history_list.get_children():
            history_list.delete(iid)
        
        for i, file_path in enumerate(history):
            display_name = os.path.basename(file_path)
            if i == current_index and playing: # Chỉ đánh dấu khi đang phát
                history_list.insert(parent='', index='end', iid=str(i), text='', values=(display_name,), tags=('playing_song',)) 
            else:
                history_list.insert(parent='', index='end', iid=str(i), text='', values=(display_name,)) 
        
        save_history() # Đảm bảo lịch sử được lưu sau mỗi lần cập nhật Treeview
        update_button_states() # Cập nhật trạng thái nút sau khi cập nhật danh sách

    def play_audio(file_path):
        global current_index, playing, paused
        if not file_path:
            lbl_status.config(text="Chưa chọn file nhạc nào.")
            stop_audio()
            return
        
        # Thêm vào lịch sử nếu đây là bài hát mới HOẶC nếu nó không ở cuối lịch sử
        if file_path not in history:
            history.append(file_path)
        
        # Luôn tìm chỉ mục mới nhất của bài hát trong lịch sử
        # Đảm bảo bài hát được phát luôn là bài hát đang được đánh dấu
        try:
            current_index = history.index(file_path)
        except ValueError:
            # Điều này có thể xảy ra nếu file_path không có trong history
            # (ví dụ: bị xóa khỏi history nhưng vẫn được gọi để phát)
            # Trong trường hợp này, có thể thêm lại hoặc bỏ qua
            lbl_status.config(text=f"Lỗi: Không tìm thấy '{os.path.basename(file_path)}' trong lịch sử.")
            stop_audio()
            return

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(SONG_END_EVENT) # Đặt sự kiện kết thúc bài hát
        lbl_status.config(text=f"Đang phát: {os.path.basename(file_path)}")
        playing = True
        paused = False
        update_history_display() # Cập nhật hiển thị và lưu lịch sử
        update_button_states()

    def toggle_pause():
        global paused, playing
        if playing:
            if paused:
                pygame.mixer.music.unpause()
                lbl_status.config(text=f"Đang phát: {os.path.basename(history[current_index])}")
            else:
                pygame.mixer.music.pause()
                lbl_status.config(text=f"Tạm dừng: {os.path.basename(history[current_index])}")
            paused = not paused
        else:
            lbl_status.config(text="Không có bài hát đang phát!")
        update_button_states()

    def stop_audio():
        global playing, paused, current_index
        if pygame.mixer.music.get_busy(): # Chỉ dừng nếu đang có nhạc phát
            pygame.mixer.music.stop()
        lbl_status.config(text="Đã dừng phát")
        playing = False
        paused = False
        current_index = None # Đặt lại chỉ mục hiện tại khi dừng
        update_history_display() # Cập nhật hiển thị (bỏ đánh dấu bài hát)
        update_button_states()

    def play_all_from_start():
        if not history:
            lbl_status.config(text="Danh sách trống, không có bài để phát.")
            return
        global current_index
        current_index = 0
        play_audio(history[current_index])

    def play_next_song():
        """Chuyển sang và phát bài hát tiếp theo trong danh sách."""
        global current_index
        if not history:
            stop_audio()
            return
        
        if current_index is None: # Nếu chưa có gì phát, bắt đầu từ đầu
            current_index = 0
        else:
            current_index = (current_index + 1) % len(history) # Lặp lại từ đầu nếu ở cuối

        play_audio(history[current_index])

    def play_previous_song():
        """Chuyển sang và phát bài hát trước đó trong danh sách."""
        global current_index
        if not history:
            stop_audio()
            return

        if current_index is None: # Nếu chưa có gì phát, bắt đầu từ cuối
            current_index = len(history) - 1
        else:
            current_index = (current_index - 1 + len(history)) % len(history) # Lặp lại về cuối nếu ở đầu

        play_audio(history[current_index])

    def get_selected_index(event=None): # Đặt event=None để có thể gọi mà không cần sự kiện
        """Lấy chỉ mục của mục được chọn trong Treeview."""
        selected_item_ids = history_list.selection()
        if selected_item_ids and selected_item_ids[0].isdigit():
            idx = int(selected_item_ids[0])
            if 0 <= idx < len(history):
                return idx
        return None

    def play_selected(event):
        """Phát bài hát khi nhấn đúp vào danh sách Treeview."""
        selected_index = get_selected_index(event)
        if selected_index is not None:
            file_path = history[selected_index]
            play_audio(file_path)

    def remove_selected_from_history():
        """Xóa bài hát đã chọn khỏi danh sách lịch sử."""
        global history, current_index
        selected_index = get_selected_index(None) # Lấy lựa chọn hiện tại
        if selected_index is not None:
            if current_index is not None and current_index == selected_index:
                stop_audio() # Dừng phát nếu bài đang phát bị xóa
            
            # Điều chỉnh current_index nếu bài hát bị xóa ảnh hưởng đến chỉ mục
            if current_index is not None:
                if selected_index < current_index:
                    current_index -= 1
                elif selected_index == current_index: # Nếu xóa bài đang phát
                    current_index = None # Hoặc có thể chuyển sang bài tiếp theo/trước đó
            
            del history[selected_index]
            
            # Xử lý trường hợp history trở thành rỗng sau khi xóa
            if not history:
                current_index = None
            elif current_index is not None and current_index >= len(history):
                current_index = len(history) - 1 # Điều chỉnh nếu chỉ mục vượt quá giới hạn

            update_history_display()
            update_button_states() # Cập nhật lại trạng thái nút sau khi xóa
            
    def move_song_up():
        """Di chuyển bài hát được chọn lên một vị trí trong danh sách."""
        global current_index
        idx = get_selected_index(None)
        if idx is not None and idx > 0:
            song_to_move = history.pop(idx)
            history.insert(idx - 1, song_to_move)

            if current_index == idx:
                current_index -= 1
            elif current_index == idx - 1:
                current_index += 1

            update_history_display()
            history_list.selection_set(str(idx - 1)) # Giữ bài hát được chọn
            history_list.focus(str(idx - 1)) # Giữ focus

    def move_song_down():
        """Di chuyển bài hát được chọn xuống một vị trí trong danh sách."""
        global current_index
        idx = get_selected_index(None)
        if idx is not None and idx < len(history) - 1:
            song_to_move = history.pop(idx)
            history.insert(idx + 1, song_to_move)

            if current_index == idx:
                current_index += 1
            elif current_index == idx + 1:
                current_index -= 1

            update_history_display()
            history_list.selection_set(str(idx + 1)) # Giữ bài hát được chọn
            history_list.focus(str(idx + 1)) # Giữ focus

    def show_context_menu(event):
        """Hiển thị menu ngữ cảnh khi nhấn chuột phải vào Treeview."""
        context_menu = Menu(tinh_nang_9, tearoff=0) # Sử dụng tinh_nang_9 làm parent
        
        item_id_at_click = history_list.identify_row(event.y) 
        
        # Luôn xóa lựa chọn hiện tại và đặt lựa chọn mới tại vị trí click
        history_list.selection_clear()
        if item_id_at_click:
            history_list.selection_set(item_id_at_click)
            history_list.focus(item_id_at_click)

        selected_index = get_selected_index(None) # Lấy chỉ mục của mục được chọn

        if selected_index is not None:
            if selected_index > 0:
                context_menu.add_command(label="Di chuyển lên", command=move_song_up)
            if selected_index < len(history) - 1:
                context_menu.add_command(label="Di chuyển xuống", command=move_song_down)
            
            if context_menu.index("end") is not None and context_menu.index("end") > 0:
                context_menu.add_separator()

            context_menu.add_command(label="Xóa khỏi danh sách", command=remove_selected_from_history)
    
        if history: # Chỉ thêm tùy chọn xóa toàn bộ lịch sử nếu có bài hát trong lịch sử
            if context_menu.index("end") is not None and context_menu.index("end") > 0: 
                context_menu.add_separator()
            context_menu.add_command(label="Xóa toàn bộ lịch sử", command=clear_history)
        
        # Chỉ hiển thị menu nếu có ít nhất một tùy chọn
        if context_menu.index("end") is not None:
            context_menu.tk_popup(event.x_root, event.y_root)

    def open_file_from_button():
        """Mở hộp thoại chọn tệp và phát nhạc."""
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if file_path:
            play_audio(file_path)

    def clear_history():
        """Xóa toàn bộ lịch sử bài hát."""
        global history, current_index
        if playing:
            stop_audio()
        history.clear() # Dùng history.clear() thay vì gán lại danh sách trống
        current_index = None
        update_history_display()
        update_button_states() # Cập nhật lại trạng thái nút sau khi xóa

    def check_pygame_events():
        """Kiểm tra các sự kiện của Pygame, đặc biệt là sự kiện kết thúc bài hát."""
        for event in pygame.event.get():
            if event.type == SONG_END_EVENT:
                if playing and not paused: # Đảm bảo đang phát và không tạm dừng
                    play_next_song()
        # Lặp lại hàm này sau mỗi 100ms
        tinh_nang_9.after(100, check_pygame_events)

    # --- Tạo cửa sổ Tkinter Toplevel ---
    tinh_nang_9 = tk.Toplevel(root) 
    tinh_nang_9.title("9.Máy phát nhạc") 
    tinh_nang_9.geometry("700x500")
    try:
        tinh_nang_9.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")

    style = ThemedStyle(tinh_nang_9)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_9.config(bg=theme_bg_color)

    # Cấu hình grid cho cửa sổ chính
    tinh_nang_9.grid_columnconfigure(0, weight=1) 
    tinh_nang_9.grid_columnconfigure(1, weight=0) 
    tinh_nang_9.grid_rowconfigure(0, weight=1) 

    # Khung bên trái (danh sách bài hát)
    frame_left = ttk.Frame(tinh_nang_9, style='ThemedFrame.TFrame') 
    frame_left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    frame_left.grid_rowconfigure(1, weight=1)
    frame_left.grid_columnconfigure(0, weight=1)
    frame_left.grid_columnconfigure(1, weight=0)

    lbl_list = ttk.Label(frame_left, text="Danh sách file âm thanh đã nghe", font=("Arial", 12, "bold"))
    lbl_list.grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky="ew")

    history_list = ttk.Treeview(frame_left, selectmode='browse', columns=('song_name',))
    history_list.column("#0", width=0, stretch=tk.NO)
    history_list.column("song_name", anchor=tk.W, width=400)
    history_list.heading("song_name", text="Tên bài hát", anchor=tk.W) # Thêm tiêu đề cho cột

    # Cấu hình style cho bài hát đang phát
    style.configure('playing_song.Treeview', font=('Arial', 10, 'bold'), foreground='red')
    # Sửa lỗi map background cho Treeview, sử dụng theme của ttkthemes
    style.map('Treeview', background=[('selected', style.lookup('Treeview', 'fieldbackground', default='blue'))]) # Sử dụng màu nền của Treeview

    history_list.grid(row=1, column=0, sticky="nsew")
    history_list.bind("<Double-Button-1>", play_selected)
    history_list.bind("<Button-3>", show_context_menu)
    history_list.bind("<<TreeviewSelect>>", lambda e: update_button_states()) # Cập nhật trạng thái nút khi chọn

    scrollbar = ttk.Scrollbar(frame_left, orient="vertical", command=history_list.yview)
    scrollbar.grid(row=1, column=1, sticky="ns")
    history_list.config(yscrollcommand=scrollbar.set)

    # Khung bên phải (các nút điều khiển)
    frame_right = ttk.Frame(tinh_nang_9, style='ThemedFrame.TFrame') 
    frame_right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    frame_right.grid_columnconfigure(0, weight=1)

    lbl_status = ttk.Label(frame_right, text="Chưa phát file nào", wraplength=200, font=("Arial", 10))
    lbl_status.grid(row=0, column=0, pady=5, sticky="ew")

    control_buttons_frame = ttk.Frame(frame_right, style='ThemedFrame.TFrame')
    control_buttons_frame.grid(row=1, column=0, pady=5, sticky="n")

    # Các nút điều khiển
    btn_choose = ttk.Button(control_buttons_frame, text="Chọn file nhạc", command=open_file_from_button, width=15, style='TButton')
    btn_choose.grid(row=0, column=0, pady=5)
    btn_play_all = ttk.Button(control_buttons_frame, text="Phát toàn bộ list", command=play_all_from_start, width=15, style='TButton')
    btn_play_all.grid(row=1, column=0, pady=5)
    btn_prev = ttk.Button(control_buttons_frame, text="Bài trước", command=play_previous_song, width=15, style='TButton')
    btn_prev.grid(row=2, column=0, pady=5)
    btn_next = ttk.Button(control_buttons_frame, text="Bài tiếp theo", command=play_next_song, width=15, style='TButton')
    btn_next.grid(row=3, column=0, pady=5)
    btn_pause = ttk.Button(control_buttons_frame, text="Tạm dừng", command=toggle_pause, width=15, style='TButton')
    btn_pause.grid(row=4, column=0, pady=5)
    btn_stop = ttk.Button(control_buttons_frame, text="Dừng phát", command=stop_audio, width=15, style='TButton')
    btn_stop.grid(row=5, column=0, pady=5)

    # --- Khởi tạo trạng thái ban đầu ---
    update_history_display() # Cập nhật hiển thị và tải lịch sử
    update_button_states() # Đảm bảo các nút ở trạng thái đúng lúc khởi tạo

    # Bắt đầu vòng lặp sự kiện Pygame
    tinh_nang_9.after(100, check_pygame_events) 

    # Thêm cửa sổ Toplevel vào danh sách đang mở và thiết lập hành vi đóng
    open_toplevels.append(tinh_nang_9)
    tinh_nang_9.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_9))
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
        messagebox.showinfo("Thông báo", "Tệp danh sách thành phố chưa tồn tại. Đang tiến hành tải xuống")

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
    try:
        tinh_nang_10.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
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
    open_toplevels.append(tinh_nang_10)
    tinh_nang_10.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_10))
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
    tinh_nang_11.title("11.Thay đổi giao diện người dùng") # Thiết lập tên cho cửa sổ
    tinh_nang_11.geometry("300x180") # Thiết lập kích thước
    try:
        tinh_nang_11.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
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
     # tinh_nang_12.resizable(False, False) # Loại bỏ khả năng thu phóng của cửa sổ
    try:
        tinh_nang_12.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
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
    open_toplevels.append(tinh_nang_12)
    tinh_nang_12.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_12))
###################################################################################
def ban_do():
    m = folium.Map(location=[21.0285, 105.8542], zoom_start=5)
    m.save("map.html")
    import webbrowser
    webbrowser.open("map.html")
###################################################################################
def dich_thuat():
    translator = Translator()
    def translate_text_worker():
        """
        Hàm này sẽ chạy trong một luồng riêng để dịch văn bản.
        Nó sẽ thiết lập một vòng lặp asyncio để 'await' hàm dịch.
        """
        text_to_translate = input_text_area.get("1.0", tk.END).strip()
        if not text_to_translate:
            # Sử dụng root.after để hiển thị cảnh báo trên luồng chính của Tkinter
            tinh_nang_14.after(0, lambda: messagebox.showwarning("Cảnh báo", "Vui lòng nhập văn bản để dịch."))
            return

        target_lang_name = lang_combobox.get()
        
        # Tìm mã ngôn ngữ (ví dụ: 'en' cho tiếng Anh) từ tên ngôn ngữ
        target_lang_code = None
        for code, name in LANGUAGES.items():
            if name.lower() == target_lang_name.lower():
                target_lang_code = code
                break
        
        if not target_lang_code:
            # Sử dụng root.after để hiển thị lỗi trên luồng chính của Tkinter
            tinh_nang_14.after(0, lambda: messagebox.showerror("Lỗi", "Không tìm thấy mã cho ngôn ngữ đích đã chọn."))
            return

        try:
            # Tạo một vòng lặp sự kiện mới cho luồng này
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Chạy tác vụ dịch bất đồng bộ và đợi nó hoàn thành
            # translator.translate() được 'await' tại đây
            translated = loop.run_until_complete(translator.translate(text_to_translate, dest=target_lang_code, src='auto'))
            
            # Đóng vòng lặp sự kiện
            loop.close()
            
            # Cập nhật vùng hiển thị kết quả trên luồng chính của Tkinter
            tinh_nang_14.after(0, lambda: update_output_area(translated.text))

        except Exception as e:
            # Sử dụng root.after để hiển thị lỗi trên luồng chính của Tkinter
            tinh_nang_14.after(0, lambda: messagebox.showerror("Lỗi dịch thuật", f"Đã xảy ra lỗi: {e}\nVui lòng kiểm tra kết nối internet hoặc thử lại."))

    def update_output_area(text):
        """Cập nhật an toàn vùng văn bản hiển thị kết quả trên luồng chính."""
        output_text_area.config(state=tk.NORMAL) # Cho phép chỉnh sửa tạm thời
        output_text_area.delete("1.0", tk.END)
        output_text_area.insert(tk.END, text)
        output_text_area.config(state=tk.DISABLED) # Đặt lại trạng thái chỉ đọc

    def start_translation():
        """
        Bắt đầu quá trình dịch bằng cách tạo một luồng mới.
        """
        # Tạo và khởi động một luồng mới cho hàm translate_text_worker
        translation_thread = threading.Thread(target=translate_text_worker, daemon=True)
        translation_thread.start()

    # Thiết lập cửa sổ chính

    if not root: # 2 Dòng này nhằm đảm bảo của sổ chính tồn tại 
        return
    # Tạo cửa sổ phụ cho tính năng 11     
    tinh_nang_14 = tk.Toplevel(root) # liên kết với của sổ chính bằng root
    tinh_nang_14.title("2.Dịch thuật") # Thiết lập tên cho cửa sổ
    tinh_nang_14.geometry("800x600") # Thiết lập kích thước
    try:
        tinh_nang_14.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
    tinh_nang_14.resizable(True, True)
    # Đoạn này dùng để thay đổi giao diện 
    style = ThemedStyle(tinh_nang_14)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_14.config(bg=theme_bg_color)
    # Cấu hình grid layout
    tinh_nang_14.grid_rowconfigure(0, weight=1)
    tinh_nang_14.grid_rowconfigure(1, weight=0) # Hàng cho nút và combobox
    tinh_nang_14.grid_rowconfigure(2, weight=1)
    tinh_nang_14.grid_columnconfigure(0, weight=1)
    # Vùng nhập liệu
    input_frame = ttk.LabelFrame(tinh_nang_14, text="Nhập văn bản:")
    input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
    input_frame.grid_rowconfigure(0, weight=1)
    input_frame.grid_columnconfigure(0, weight=1)
    input_text_area = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=60, height=10, font=("Arial", 12))
    input_text_area.config(bg=theme_bg_color) # Đặt màu nền cho vùng nhập liệu
    input_text_area.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    # Thanh điều khiển (Combobox và Nút)
    control_frame = ttk.Frame(tinh_nang_14)
    control_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    control_frame.grid_columnconfigure(0, weight=1) # Cột cho combobox
    control_frame.grid_columnconfigure(1, weight=0) # Cột cho nút
    # Tạo danh sách các tên ngôn ngữ được hỗ trợ
    language_names = sorted([name.title() for name in LANGUAGES.values()])
    lang_combobox = ttk.Combobox(control_frame, values=language_names, state="readonly", font=("Arial", 10))
    lang_combobox.set("Vietnamese") # Ngôn ngữ mặc định
    lang_combobox.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    # Gán hàm start_translation cho nút Dịch
    translate_button = ttk.Button(control_frame, text="Dịch", command=start_translation)
    translate_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")
    # Vùng hiển thị kết quả
    output_frame = ttk.LabelFrame(tinh_nang_14, text="Văn bản đã dịch:")
    output_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
    output_frame.grid_rowconfigure(0, weight=1)
    output_frame.grid_columnconfigure(0, weight=1)
    output_text_area = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, width=60, height=10, font=("Arial", 12))
    output_text_area.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
    output_text_area.config(bg= theme_bg_color)
    output_text_area.config(state=tk.DISABLED) # Đặt trạng thái chỉ đọc
    open_toplevels.append(tinh_nang_14)
    tinh_nang_14.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_14))
###################################################################################
def doi_loi(): # Tính năng 13: Đôi lời của nhà sản xuất
    if not root: # 2 Dòng này nhằm đảm bảo cảu sổ chính tồn tại 
        return
    
    tinh_nang_15 = tk.Toplevel(root)
    tinh_nang_15.title("15. Đôi lời của nhà sản xuất")
    try:
        tinh_nang_15.iconbitmap(icon_path)
    except tk.TclError:
        print(f"Không tìm thấy hoặc không thể sử dụng icon cho Toplevel: {icon_path}")
    tinh_nang_15.resizable(False, False)
    # Áp dụng chủ đề cho cửa sổ Toplevel
    style = ThemedStyle(tinh_nang_15)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    tinh_nang_15.config(bg=theme_bg_color)
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
    ttk.Label(tinh_nang_15, text=message, wraplength=400, justify="left", font=("Arial", 10)).pack(padx=20, pady=20) 
    open_toplevels.append(tinh_nang_15)
    tinh_nang_15.protocol("WM_DELETE_WINDOW", lambda: on_toplevel_close(tinh_nang_15))
###################################################################################
def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
###################################################################################
if __name__ == "__main__":

    root = ThemedTk(theme=current_theme)
    root.title("App đa năng")
    root.resizable(False, False)
    icon_path = resource_path("logo.ico") # "logo.ico" vì bạn đã thêm nó vào thư mục gốc (.:)
    try:
        root.wm_iconbitmap(icon_path)
    except tk.TclError:
        print(f"Warning: Could not load icon from {icon_path}. Check if the file is valid or correctly bundled.")
    # Đây là nơi bạn có thể thêm một biểu tượng mặc định hoặc bỏ qua nếu không quan trọng
        pass

    root.iconbitmap(icon_path)
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    style = ThemedStyle(root)
    style.set_theme(current_theme)
    theme_bg_color = style.lookup(".", "background") or "#F0F0F0"
    root.config(bg=theme_bg_color)

    ttk.Label(frm, text="Menu", anchor="center", font=('Arial', 14, 'bold')).grid(column=0, row=0, columnspan=2, sticky="ew", pady=5) 
    ttk.Button(frm, text="1.Đồng hồ và lịch", command=clock).grid(column=0, row=1, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="2.Máy ảnh", command=camera).grid(column=0, row=2, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="3.Gửi thư", command=gui_thu).grid(column=0, row=3, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="4.Đọc điện trở", command=doc_dien_tro).grid(column=0, row=4, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="5.Thông tin và hiệu năng máy tính", command=thong_tin_va_hieu_nang).grid(column=0, row=5, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="6.Tìm kiếm thông tin (wikipedia) ", command=tim_kiem_thong_tin).grid(column=0, row=6, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="7.Đồng hồ đếm ngược", command=dem_nguoc).grid(column=0, row=7, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="8.Soạn thảo văn bản", command=van_ban).grid(column=0, row=8, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="9.Máy phát nhạc", command=lambda: may_phat_nhac(root, current_theme, open_toplevels)).grid(column=0, row=9, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="10.Thời tiết", command=thoi_tiet).grid(column=0, row=10, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="11.Thay đổi giao diện người dùng ", command=giao_dien).grid(column=0, row=11, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="12.Bảng tuần hoàn hóa học", command=bang_tuan_hoan).grid(column=0, row=12, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="13.Bản đồ", command=ban_do).grid(column=0, row=13, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="14.Dịch thuật", command=dich_thuat).grid(column=0, row=14, columnspan=2, sticky="ew", pady=2)
    ttk.Button(frm, text="15.Đôi lời của nhà sản xuất ", command=doi_loi).grid(column=0, row=15, columnspan=2, sticky="ew", pady=2)

    root.mainloop()
