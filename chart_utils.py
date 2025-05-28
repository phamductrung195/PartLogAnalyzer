import matplotlib.pyplot as plt
from tkinter import Toplevel, Text, Scrollbar, RIGHT, BOTTOM, X, Y, END, BOTH, font as tkFont
import pandas as pd

def create_top_10_chart(top_10_data, full_data):
    # Exclude rows with Consumption = 0 from the data used in the chart
    full_data = full_data[full_data['Consumption'] > 0]

    if not top_10_data.empty:
        fig, ax1 = plt.subplots(figsize=(12, 6))
    
        # Maximize the chart window
        fig_manager = plt.get_current_fig_manager()
        fig_manager.window.state('zoomed')
        fig_manager.set_window_title("Transtechnology Vietnam Co., Ltd. - Part Log Analyzer V1.7")
        
        # Bar chart for Total Errors
        labels = [f"{row['Parts Name']} - {row['Machine Name']}" for _, row in top_10_data.iterrows()]
        bars = ax1.bar(labels, top_10_data['Total Errors'], color='red', alpha=0.6, label='Total Errors')

        # Calculate Good Rate for each part
        good_rates = []
        for _, row in top_10_data.iterrows():
            part_name = row['Parts Name']
            machine_name = row['Machine Name']
            # Filter full_data for the specific part and machine
            filtered_full_data = full_data[(full_data['Parts Name'] == part_name) & (full_data['Machine Name'] == machine_name)]
            _, good_rate = calculate_error_and_good_rate(pd.DataFrame([row]), filtered_full_data)  # Convert row to DataFrame
            good_rates.append(good_rate)

        # Create a second y-axis for the Good Rate
        ax2 = ax1.twinx()
        line, = ax2.plot(labels, good_rates, color='blue', marker='o', linestyle='-', linewidth=2, label='Good Rate (%)')

        # Annotate each point on the line chart with its Good Rate value
        for i, good_rate in enumerate(good_rates):
            ax2.annotate(f'{good_rate:.2f}%', xy=(i, good_rate), xytext=(0, 5), 
                         textcoords="offset points", ha='center', color='blue', fontsize=9)

        # Set titles and labels dynamically based on selected Parts Name
        selected_part = full_data['Parts Name'].iloc[0] if not full_data.empty else "Unknown"
        ax1.set_title(f'Top Components by Total Errors and Good Rate for {selected_part}')
        ax1.set_xlabel('Part Name - Machine')
        ax1.set_ylabel('Total Error Count')
        ax2.set_ylabel('Good Rate (%)')

        # Customize ticks and legends
        ax1.tick_params(axis='y', labelcolor='red')
        ax2.tick_params(axis='y', labelcolor='blue')
        ax1.set_xticks(range(len(labels)))  # Set the tick positions based on the number of labels
        ax1.set_xticklabels(labels, rotation=45, ha='right')  # Apply the labels

        # Add legends
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        plt.tight_layout()
        ax1.bar_label(bars, labels=[f'{int(val)}' for val in top_10_data['Total Errors']], label_type='center')

        # Event handler for clicking on a bar
        def on_click(event):
            for i, bar in enumerate(bars):
                if bar.contains(event)[0]:
                    component_name = top_10_data.iloc[i]['Parts Name']
                    machine_name = top_10_data.iloc[i]['Machine Name']
                    create_second_chart(component_name, machine_name, full_data)
                    break  # Only create the second chart

        fig.canvas.mpl_connect('button_press_event', on_click)
        plt.show()
    else:
        print("No data available for charting.")

def calculate_error_and_good_rate(top_10_data, full_data):
    # Filter out rows with zero consumption to avoid distortion in error rate calculation
    valid_data = full_data[full_data['Consumption'] > 0]

    # Calculate total errors and total consumption for the filtered data
    total_errors = valid_data['Total Errors'].sum()
    total_consumption = valid_data['Consumption'].sum()

    if total_consumption > 0:  # Avoid division by zero
        error_rate = (total_errors / total_consumption) * 100
        good_rate = 100 - error_rate
    else:
        error_rate = 0
        good_rate = 100

    return error_rate, good_rate

def create_second_chart(part_name, machine_name, full_data):
    # Filter data to exclude rows with Consumption = 0
    filtered_data = full_data[(full_data['Parts Name'] == part_name) & (full_data['Machine Name'] == machine_name)]
    filtered_data = filtered_data[filtered_data['Consumption'] > 0]
    
    if not filtered_data.empty:
        error_columns = ['Pick Error Counter', 'Vision Error Counter', 'Nozzle Error Counter', 'Coplanarity Error Counter']
        
        if all(col in filtered_data.columns for col in error_columns):
            filtered_data.loc[:, 'Total Errors'] = filtered_data[error_columns].sum(axis=1)
        
        program_errors = filtered_data.groupby('Program Name')['Total Errors'].sum().reset_index()
        program_errors = program_errors.sort_values(by='Total Errors', ascending=False).head(20)

        fig, ax = plt.subplots(figsize=(12, 6))

        # Maximize the chart window
        fig_manager = plt.get_current_fig_manager()
        fig_manager.window.state('zoomed')
        fig_manager.set_window_title("Transtechnology Vietnam Co., Ltd. - Part Log Analyzer V1.7")

        bars = ax.bar(program_errors['Program Name'], program_errors['Total Errors'], color='blue')
        ax.bar_label(bars, label_type='center')

        plt.title(f'Top Worst by Program for {part_name} on {machine_name}')
        plt.xlabel('Program Name')
        plt.ylabel('Total Error Count')
        plt.xticks(rotation=45, ha='right')

        max_errors = int(program_errors['Total Errors'].max())
        step = max(1, max_errors // 5)
        ax.set_yticks(range(0, max_errors + step, step))

        def on_click(event):
            for i, bar in enumerate(bars):
                if bar.contains(event)[0]:
                    program_name = program_errors.iloc[i]['Program Name']
                    show_program_details(program_name, part_name, machine_name, full_data)
                    break

        fig.canvas.mpl_connect('button_press_event', on_click)
        plt.tight_layout()
        plt.show()
    else:
        print(f"No data available for {part_name} on {machine_name} to create the second chart.")

def show_program_details(program_name, part_name, machine_name, full_data):
    filtered_data = full_data[(full_data['Parts Name'] == part_name) & (full_data['Machine Name'] == machine_name) & (full_data['Program Name'] == program_name)]
    
    detail_window = Toplevel()
    detail_window.title(f"Details for Program: {program_name} on {part_name} - {machine_name}")
    detail_window.state('zoomed')  # Maximize window

    text_widget = Text(detail_window, wrap="none", undo=True)
    scroll_y = Scrollbar(detail_window, orient="vertical", command=text_widget.yview)
    scroll_x = Scrollbar(detail_window, orient="horizontal", command=text_widget.xview, width=20)

    text_widget.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    monospaced_font = tkFont.Font(family="Courier", size=10)
    text_widget.configure(font=monospaced_font)

    if not filtered_data.empty:
        header = filtered_data.columns.tolist()
        column_widths = [
            max(len(str(val)) for val in [col] + filtered_data[col].tolist()) + 2
            for col in header
        ]
        header_str = ''.join([f"{col:<{column_widths[i]}}" for i, col in enumerate(header)])
        text_widget.insert(END, header_str + "\n" + "-" * len(header_str) + "\n")
        
        for _, row in filtered_data.iterrows():
            row_str = ''.join([f"{str(val):<{column_widths[i]}}" for i, val in enumerate(row)])
            text_widget.insert(END, row_str + "\n")
    else:
        text_widget.insert(END, f"No data available for program {program_name}.\n")

    text_widget.pack(side="top", fill=BOTH, expand=True)
    scroll_y.pack(side=RIGHT, fill=Y)
    scroll_x.pack(side=BOTTOM, fill=X)

import matplotlib.pyplot as plt
from tkinter import Toplevel, Text, Scrollbar, RIGHT, BOTTOM, X, Y, END, BOTH, font as tkFont
import pandas as pd

def create_daily_error_pickup_chart(part_name, full_data):
    """Vẽ biểu đồ Total Errors (cột chồng theo máy), Pickup Rate (đường), và Valid Consumption (đường) theo ngày cho Parts Name được chọn."""
    filtered_data = full_data[(full_data['Parts Name'] == part_name) & (full_data['Consumption'] > 0)].copy()
    
    if not filtered_data.empty:
        # Các cột lỗi liên quan
        error_columns = ['Pick Error Counter', 'Vision Error Counter', 'Coplanarity Error Counter']  # Không bao gồm Nozzle Error Counter
        if all(col in filtered_data.columns for col in error_columns):
            # Tính Total Errors theo công thức yêu cầu
            filtered_data['Total Errors'] = (filtered_data['Pick Error Counter'] + 
                                            filtered_data['Vision Error Counter'] + 
                                            filtered_data['Coplanarity Error Counter'] - 
                                            filtered_data.get('No Parts Error Counter', 0))
        
        # Tính Valid Consumption
        filtered_data['Valid Consumption'] = filtered_data['Consumption'] - filtered_data.get('No Parts Error Counter', 0)
        
        # Nhóm dữ liệu theo Date và Machine Name cho Total Errors (cột chồng)
        daily_machine_data = filtered_data.groupby(['Date', 'Machine Name'])['Total Errors'].sum().unstack(fill_value=0)
        
        # Nhóm dữ liệu theo Date và tính tổng từng cột để tính Pickup Rate
        daily_data = filtered_data.groupby('Date').agg({
            'Pick Error Counter': 'sum',
            'Vision Error Counter': 'sum',
            'Coplanarity Error Counter': 'sum',
            'No Parts Error Counter': 'sum',
            'Consumption': 'sum',
            'Valid Consumption': 'sum'  # Dùng để vẽ đường Valid Consumption
        }).reset_index()
        
        # Tính Pickup Rate dựa trên tổng các cột
        daily_data['Error Sum'] = (daily_data['Pick Error Counter'] + 
                                  daily_data['Vision Error Counter'] + 
                                  daily_data['Coplanarity Error Counter'] - 
                                  daily_data['No Parts Error Counter'])
        daily_data['Pickup Rate'] = 100 - (daily_data['Error Sum'] / daily_data['Valid Consumption'] * 100)

        # Vẽ biểu đồ
        fig, ax1 = plt.subplots(figsize=(15, 6))
        fig_manager = plt.get_current_fig_manager()
        fig_manager.window.state('zoomed')
        fig_manager.set_window_title("Transtechnology Vietnam Co., Ltd. - Part Log Analyzer V1.7")

        # Biểu đồ cột chồng cho Total Errors theo máy
        daily_machine_data.plot(kind='bar', stacked=True, ax=ax1, alpha=0.6, width=0.8)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Total Error Count', color='black')
        ax1.tick_params(axis='y', labelcolor='black')

        # Thêm giá trị số lỗi vào từng phần của stack chart
        for i, (date, row) in enumerate(daily_machine_data.iterrows()):
            cumulative = 0
            for machine, errors in row.items():
                if errors > 0:
                    ax1.text(i, cumulative + errors / 2, f'{int(errors)}', 
                             ha='center', va='center', fontsize=8, color='white', weight='bold')
                    cumulative += errors

        # Trục y thứ hai: Đường Pickup Rate
        ax2 = ax1.twinx()
        ax2.plot(daily_data.index, daily_data['Pickup Rate'], color='green', marker='o', linestyle='-', linewidth=2, label='Pickup Rate (%)')
        ax2.set_ylabel('Pickup Rate (%)', color='green')
        ax2.set_ylim(0, 120)
        ax2.tick_params(axis='y', labelcolor='green')

        # Thêm chú thích giá trị cho Pickup Rate
        for i, rate in enumerate(daily_data['Pickup Rate']):
            ax2.annotate(f'{rate:.2f}%', xy=(i, rate), xytext=(0, 5), 
                         textcoords="offset points", ha='center', color='green', fontsize=9)

        # Trục y thứ ba: Đường Valid Consumption
        ax3 = ax1.twinx()
        ax3.spines['right'].set_position(('outward', 60))
        ax3.plot(daily_data.index, daily_data['Valid Consumption'], color='orange', marker='s', linestyle='--', linewidth=2, label='Valid Consumption')
        ax3.set_ylabel('Valid Consumption', color='orange')
        ax3.tick_params(axis='y', labelcolor='orange')

        # Thêm chú thích giá trị cho Valid Consumption
        for i, cons in enumerate(daily_data['Valid Consumption']):
            ax3.annotate(f'{int(cons)}', xy=(i, cons), xytext=(0, -10), 
                         textcoords="offset points", ha='center', color='orange', fontsize=9)

        # Định dạng nhãn ngày tháng
        date_labels = [date.strftime('%Y-%m-%d') for date in daily_machine_data.index]
        ax1.set_xticks(range(len(date_labels)))
        ax1.set_xticklabels(date_labels, rotation=45, ha='right', fontsize=8)

        # Tiêu đề và định dạng
        ax1.set_title(f'Daily Total Errors by Machine, Pickup Rate, and Valid Consumption for {part_name}')
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Chú thích
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines3, labels3 = ax3.get_legend_handles_labels()
        ax1.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='upper left')

        plt.tight_layout()
        plt.show()
    else:
        print(f"No data available for {part_name} to create the daily error, pickup, and consumption chart.")