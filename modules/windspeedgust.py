import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
import matplotlib.image as mpimg
from helpers.utilities import load_data, copyright_text, get_station_location, contact_details
from datetime import date, datetime
from matplotlib.lines import Line2D


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


clear_console()

try:
    station_location = get_station_location()
except Exception as exception:
    print(f"{exception}")
except KeyboardInterrupt as kbi:
    print(f"{kbi}")

data = load_data()

data.columns = [col.strip() for col in data.columns]
expected_columns = {'Date (Europe/London)', 'Gust of wind (mph)', 'Average wind speed (mph)'}
if not expected_columns.issubset(data.columns):
    raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

data = data[['Date (Europe/London)', 'Gust of wind (mph)', 'Average wind speed (mph)']]

data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()
data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                              errors='coerce')

data = data.sort_values(by='Date (Europe/London)')

data['Gust of wind (mph)'] = (data['Gust of wind (mph)'].astype(str).str.replace(',', '', regex=True))
data['Gust of wind (mph)'] = pd.to_numeric(data['Gust of wind (mph)'], errors='coerce')

data['Average wind speed (mph)'] = pd.to_numeric(data['Average wind speed (mph)'], errors='coerce')

# Print data ranges
print("\n Date range found:")
print(f"    Start: {data['Date (Europe/London)'].min().strftime('%d/%m/%Y')}")
print(f"    End:   {data['Date (Europe/London)'].max().strftime('%d/%m/%Y')}")
print("\n Wind Speed range found:")
y_min = (data['Average wind speed (mph)'].min())
y_max = (data['Average wind speed (mph)'].max())
print(f"    {y_min} - {y_max} mph")
print("\n Wind Gust range found:")
y_min = (data['Gust of wind (mph)'].min())
y_max = (data['Gust of wind (mph)'].max())
print(f"    {y_min} - {y_max} mph")

def get_user_date_range():
    while True:
        try:
            start_date = input("\n Date to run the report from? (DD-MM-YYYY): ")
            end_date = input(" Date to run the report until? (DD-MM-YYYY): ")

            start_date = pd.to_datetime(start_date, format='%d-%m-%Y')
            end_date = pd.to_datetime(end_date, format='%d-%m-%Y')

            if start_date > end_date:
                print("Start date must be before end date. Try again.")
                continue

            if start_date < data['Date (Europe/London)'].min() or end_date > data['Date (Europe/London)'].max():
                print("Date range is outside available data. Try again.")
                continue

            return start_date, end_date
        except ValueError:
            print("Invalid date format. Please use DD-MM-YYYY.")

start_date, end_date = get_user_date_range()

data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
if data.empty:
    print("\n\033[1;93m Warning: No data available for the selected date range.\n"
          " Use function 1 to check the database date range.\033[0m\n")

# Create the canvas
fig, ax1 = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

# plot the data
# Plot average wind speed on the primary y-axis
ax1.bar(data['Date (Europe/London)'], data['Average wind speed (mph)'], label='Wind speed (mph)',
        color='cornflowerblue')
# Create a secondary y-axis
ax2 = ax1.twinx()
# Plot wind gust on the secondary y-axis
ax2.plot(data['Date (Europe/London)'], data['Gust of wind (mph)'], linestyle='solid', color='darkblue',
         label='Wind Gust (mph)', alpha=0.3, linewidth=0.6)

# X-axis configuration
x_min = data['Date (Europe/London)'].min()
x_max = data['Date (Europe/London)'].max()
x_range = x_max - x_min  # Store range to avoid recomputation
margin = x_range * 0.01  # 1% of the data range

ax1.set_xlim(x_min - margin, x_max + margin)  # Apply limits with buffer

# Y-axis configuration (Gust of wind)
a_min = np.floor(data['Gust of wind (mph)'].min())
a_max = np.ceil(data['Gust of wind (mph)'].max() / 5) * 5

ax1.set_ylim(a_min, a_max)
ax2.set_ylim(a_min, a_max)  # Keep y-axis scale consistent
ax1.minorticks_on()

# Hide ticks on the right ax2
ax2.tick_params(axis='y', which='both', left=False, right=False, labelleft=False, labelright=False)

# Format the chart
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
# Minor ticks for every day
ax1.xaxis.set_minor_locator(mdates.DayLocator(interval=1))

# Enable grid
ax1.grid(which='both', linestyle=':', linewidth=0.5, color='gainsboro')
ax1.tick_params(axis='x', which='major', length=10, width=1, pad=5)
ax1.tick_params(axis='x', which='minor', length=5, width=1, labelbottom=False)
ax2.tick_params(axis='x', which='major', length=10, width=1, pad=5)
ax2.tick_params(axis='x', which='minor', length=5, width=1)
# Set y axis labels
ax1.set_xlabel('Daily date markers')  # Date label
ax1.set_ylabel('Wind')  # Label for y-axis (left).

# Set chart Titles
fig.suptitle(f"{station_location} Wind Speed & Gusts", fontsize=20)
ax1.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
              f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12)

# Stats
# Remove NaN or infinite values
data = data.replace([np.inf, -np.inf], np.nan).dropna()
# Set Max, Min, & Avg legend labels
stat_labels = [
    Line2D([0], [0], color='white', lw=0, label=f''),
    Line2D([0], [0], color='white', lw=0, label=f'Minimum:'),
    Line2D([0], [0], color='white', lw=0, label=f'Maximum:'),
    Line2D([0], [0], color='white', lw=0, label=f'Average:'),
]
# Compute average wind speed statistics
awmin_val = data['Average wind speed (mph)'].min()
awmax_val = data['Average wind speed (mph)'].max()
awavg_val = data['Average wind speed (mph)'].mean()
aw_stat_handles = [
    Line2D([0], [0], color='white', lw=0, label=f'{awmin_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{awmax_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{awavg_val:.2f}'),
]
# Compute wind gust statistics
wgmin_val = data['Gust of wind (mph)'].min()
wgmax_val = data['Gust of wind (mph)'].max()
wgavg_val = data['Gust of wind (mph)'].mean()
wg_stat_handles = [
    Line2D([0], [0], color='white', lw=0, label=f'{wgmin_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{wgmax_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{wgavg_val:.2f}'),
]

# Combine and insert legends for the three datasets
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(stat_labels + lines + aw_stat_handles + lines2 + wg_stat_handles,
           [handle.get_label() for handle in stat_labels] + labels +
           [handle.get_label() for handle in aw_stat_handles] + labels2 +
           [handle.get_label() for handle in wg_stat_handles], loc='lower center', bbox_to_anchor=(0.5, -0.6),
           ncol=3,
           edgecolor='lightgray')

# Notes
ax1.text(0.5, -0.65, '"Wind Speed" is the average wind speed measured over short intervals while "Wind Gust" is the '
                     'biggest gust of wind during each interval.',
         transform=ax1.transAxes, fontsize=10, color='black', ha='center')

# Insert logo
logo = mpimg.imread("helpers/img/logo.jpg")
logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
logo_ax.imshow(logo, interpolation="antialiased")
logo_ax.axis("off")  # Hide axes around the logo

# Author details
ax1.text(0.5, -1.8, copyright_text(), transform=ax1.transAxes, fontsize=6, color='black',
         ha='center')

ax1.annotate(contact_details(), xy=(0.5, -1.83), ha='center', va='center', fontsize=7,
             color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

# Save to PDF with 1 cm margins
analytics_path = os.path.join('analytics/')
if not os.path.exists(analytics_path):
    os.makedirs(analytics_path)

current_date = date.today()
current_time = datetime.now()

pdf_filename = (f'{analytics_path}{current_date.strftime('%d%m%Y')}_{current_time.strftime('%H:%M')}hrs_'
                            f'{station_location}_Wind_Speed_v_Gust_Report.pdf')

with PdfPages(pdf_filename) as pdf:
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()

print(f'\n    Graph created & saved: {pdf_filename}\n')