# Ver1.0: 20241104 First released
# Ver1.1: 20241105 Add ERROR-BY-RATE line chart
# Ver1.2: 20250304 Add Parts Name selection with enable/disable option
# Ver1.3: 20250305 Add Daily Error and Pickup Rate chart when filtering by Parts Name
# Ver1.4: 20250306 Replace Combobox with Entry for manual Parts Name input
# Ver1.5: 20250312 Debug; Add stack bar chart to see which machine affect to a filtered Part Name
# Ver1.6: 20250319 Correct formula to calculate Pickup Rate/ Error Count in case Filter by Part Name
# Ver1.7: 20250319 Add advance filter. Change better GUI (theme)

from FileHandler import get_csv_files, merge_and_clean
from Chart_TopCountByPart import create_top_10_chart, get_top_10_worst_components
from chart_utils import create_daily_error_pickup_chart
import os
import sys
import pandas as pd
from tkinter import Tk, Frame, Label, Button, StringVar, BooleanVar, Entry, ttk
from tkcalendar import DateEntry
from datetime import datetime

def read_folders_from_file(file_path="FolderAddress.txt"):
    folder_info = []
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)
    full_path = os.path.join(base_path, file_path)
    try:
        with open(full_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and ' ' in line:
                    address, machine_name = line.rsplit(' ', 1)
                    folder_info.append((address, machine_name))
                else:
                    print(f"Skipping invalid line in {file_path}: '{line}'")
        return folder_info
    except FileNotFoundError:
        print(f"Error: {full_path} not found.")
        return []

def get_available_dates(folder_paths):
    available_dates = set()
    for folder, _ in folder_paths:
        for root, _, files in os.walk(folder):
            for file in files:
                if file.startswith("PartsLog_") and file.endswith(".csv"):
                    file_date_str = file.split('_')[-1][:8]
                    try:
                        file_date = datetime.strptime(file_date_str, '%Y%m%d').date()
                        available_dates.add(file_date)
                    except ValueError:
                        print(f"Skipping file with unexpected date format: {file}")
    return sorted(available_dates)

def load_initial_data(folder_paths, start_date, end_date):
    all_files = []
    for folder, machine_name in folder_paths:
        files = get_csv_files([(folder, machine_name)], start_date, end_date)
        all_files.extend(files)
    
    if all_files:
        merged_data = merge_and_clean(all_files)
        merged_data['Date'] = pd.to_datetime(merged_data['File Name'].apply(lambda x: x.split('_')[-1][:8]), format='%Y%m%d')
        filtered_data = merged_data[(merged_data['Date'] >= start_date) & (merged_data['Date'] <= end_date)]
        return filtered_data
    return pd.DataFrame()

def main():
    root = Tk()
    root.title("Transtechnology Vietnam Co., Ltd. - Part Log Analyzer V1.7")
    root.state('zoomed')
    root.configure(bg='#000000')  # Nền đen theo yêu cầu

    # Sử dụng ttk Style để giao diện đẹp hơn
    style = ttk.Style()
    style.theme_use('clam')  # Theme clam để màu sắc áp dụng đúng
    style.configure('TButton', font=('Segoe UI', 12, 'bold'), padding=10, background='#1abc9c', foreground='white')
    style.map('TButton', background=[('active', '#16a085')], foreground=[('active', 'white')])
    style.configure('TLabel', font=('Segoe UI', 12), background='#000000', foreground='#ffffff')
    style.configure('TCheckbutton', font=('Segoe UI', 12), background='#000000', foreground='#ffffff')
    style.configure('TEntry', font=('Segoe UI', 12), relief='flat', background='#ffffff', foreground='#000000')
    # Cấu hình màu khi disabled
    style.configure('TEntry.Disabled', background='#666666', foreground='#999999')

    # Frame chính với padding
    main_frame = Frame(root, bg='#000000')
    main_frame.pack(pady=40, padx=40, fill='both', expand=True)

    # Frame cho bộ lọc với viền cong
    filter_frame = ttk.LabelFrame(main_frame, text=" Filter Settings ", padding=20, style='Custom.TLabelframe')
    style.configure('Custom.TLabelframe', background='#1a1a1a', foreground='#ffffff', font=('Segoe UI', 14, 'bold'))
    style.configure('Custom.TLabelframe.Label', background='#1a1a1a', foreground='#ffffff')
    filter_frame.pack(fill='x', pady=15)

    # Variables
    folder_paths = read_folders_from_file()
    available_dates = get_available_dates(folder_paths)

    if available_dates:
        start_date_var = StringVar(value=available_dates[0].strftime('%Y-%m-%d'))
        end_date_var = StringVar(value=available_dates[-1].strftime('%Y-%m-%d'))
        part_name_var = StringVar()
        filter_part_var = BooleanVar(value=False)
        machine_name_var = StringVar()
        program_name_var = StringVar()

        # Date selection
        ttk.Label(filter_frame, text="Start Date:").grid(row=0, column=0, padx=15, pady=15, sticky='e')
        start_date_entry = DateEntry(filter_frame, textvariable=start_date_var, width=15, background='#1abc9c', 
                                     foreground='white', borderwidth=0, mindate=available_dates[0], maxdate=available_dates[-1])
        start_date_entry.grid(row=0, column=1, padx=15, pady=15)

        ttk.Label(filter_frame, text="End Date:").grid(row=0, column=2, padx=15, pady=15, sticky='e')
        end_date_entry = DateEntry(filter_frame, textvariable=end_date_var, width=15, background='#1abc9c', 
                                   foreground='white', borderwidth=0, mindate=available_dates[0], maxdate=available_dates[-1])
        end_date_entry.grid(row=0, column=3, padx=15, pady=15)

        # Parts Name filter
        def toggle_part_name_entry():
            state = "normal" if filter_part_var.get() else "disabled"
            part_name_entry.config(state=state)
            # Trực tiếp áp dụng màu khi disabled
            if state == "disabled":
                part_name_entry.configure(background='#666666', foreground='#999999')
            else:
                part_name_entry.configure(background='#ffffff', foreground='#000000')

        ttk.Checkbutton(filter_frame, text="Filter by Parts Name", variable=filter_part_var, 
                        command=toggle_part_name_entry).grid(row=1, column=0, padx=15, pady=15, sticky='e')
        part_name_entry = ttk.Entry(filter_frame, textvariable=part_name_var, width=30, state="disabled")
        part_name_entry.grid(row=1, column=1, padx=15, pady=15)
        # Đảm bảo màu ban đầu khi disabled
        part_name_entry.configure(background='#666666', foreground='#999999')

        # Machine Name filter
        ttk.Label(filter_frame, text="Machine Name:").grid(row=1, column=2, padx=15, pady=15, sticky='e')
        machine_name_entry = ttk.Entry(filter_frame, textvariable=machine_name_var, width=30)
        machine_name_entry.grid(row=1, column=3, padx=15, pady=15)

        # Program Name filter
        ttk.Label(filter_frame, text="Program Name:").grid(row=2, column=0, padx=15, pady=15, sticky='e')
        program_name_entry = ttk.Entry(filter_frame, textvariable=program_name_var, width=30)
        program_name_entry.grid(row=2, column=1, padx=15, pady=15)

        # Frame cho nút
        button_frame = Frame(main_frame, bg='#000000')
        button_frame.pack(pady=30)

        # Tải dữ liệu ban đầu
        initial_start_date = pd.to_datetime(start_date_var.get())
        initial_end_date = pd.to_datetime(end_date_var.get())
        initial_data = load_initial_data(folder_paths, initial_start_date, initial_end_date)

        def process_data():
            start_date = pd.to_datetime(start_date_var.get())
            end_date = pd.to_datetime(end_date_var.get())
            selected_part = part_name_var.get().strip()
            filter_by_part = filter_part_var.get()
            selected_machine = machine_name_var.get().strip()
            selected_program = program_name_var.get().strip()

            all_files = []
            for folder, machine_name in folder_paths:
                files = get_csv_files([(folder, machine_name)], start_date, end_date)
                all_files.extend(files)

            if all_files:
                merged_data = merge_and_clean(all_files)
                merged_data['Date'] = pd.to_datetime(merged_data['File Name'].apply(lambda x: x.split('_')[-1][:8]), format='%Y%m%d')
                filtered_data = merged_data[(merged_data['Date'] >= start_date) & (merged_data['Date'] <= end_date)]

                # Áp dụng bộ lọc nâng cao
                if filter_by_part and selected_part:
                    filtered_data = filtered_data[filtered_data['Parts Name'] == selected_part]
                if selected_machine:
                    filtered_data = filtered_data[filtered_data['Machine Name'] == selected_machine]
                if selected_program:
                    filtered_data = filtered_data[filtered_data['Program Name'] == selected_program]

                # Hiển thị biểu đồ
                if not filtered_data.empty:
                    if filter_by_part and selected_part:
                        create_daily_error_pickup_chart(selected_part, filtered_data)
                    else:
                        top_10_worst_components = get_top_10_worst_components(filtered_data)
                        create_top_10_chart(top_10_worst_components, filtered_data)
                else:
                    print("No data found after applying filters.")
            else:
                print("No CSV files found in the specified folders for the selected date range.")

        def reset_filters():
            start_date_var.set(available_dates[0].strftime('%Y-%m-%d'))
            end_date_var.set(available_dates[-1].strftime('%Y-%m-%d'))
            part_name_var.set("")
            filter_part_var.set(False)
            machine_name_var.set("")
            program_name_var.set("")
            toggle_part_name_entry()  # Gọi lại để cập nhật trạng thái và màu sắc

        # Nút Process và Reset
        ttk.Button(button_frame, text="Process Data", command=process_data).pack(side='left', padx=15)
        ttk.Button(button_frame, text="Reset Filters", command=reset_filters).pack(side='left', padx=15)

    else:
        print("No available dates found. Please ensure there are CSV files in the specified folders.")

    root.mainloop()

if __name__ == "__main__":
    main()