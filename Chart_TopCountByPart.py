# Chart_TopCountByPart.py
from tkinter import Toplevel, Frame, Label, Entry, Button, StringVar
from datetime import datetime
import pandas as pd
from data_processing import get_top_10_worst_components, filter_data_by_date
from chart_utils import create_top_10_chart

def create_date_selection_window(merged_data):
    date_window = Toplevel()
    date_window.title("Select Date Range")
    date_window.state('zoomed')  # Maximize window

    frame = Frame(date_window)
    frame.pack(pady=20)

    Label(frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0)
    start_date_var = StringVar()
    Entry(frame, textvariable=start_date_var).grid(row=0, column=1)

    Label(frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=0)
    end_date_var = StringVar()
    Entry(frame, textvariable=end_date_var).grid(row=1, column=1)

    def on_submit():
        try:
            start_date = datetime.strptime(start_date_var.get(), '%Y-%m-%d')
            end_date = datetime.strptime(end_date_var.get(), '%Y-%m-%d')
            filtered_data = filter_data_by_date(merged_data, start_date, end_date)
            if not filtered_data.empty:
                top_10_worst_components = get_top_10_worst_components(filtered_data)
                create_top_10_chart(top_10_worst_components, filtered_data)
                date_window.destroy()  # Close the date selection window
            else:
                print("No data available for the selected date range.")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    Button(frame, text="Submit", command=on_submit).grid(row=2, columnspan=2)

# Remaining code for setting up the main application logic and launching the Tkinter main loop
