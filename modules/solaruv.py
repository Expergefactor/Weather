import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
import matplotlib.image as mpimg
from matplotlib.lines import Line2D
import math
from helpers.utilities import load_data, copyright_text, get_station_location, contact_details
from datetime import date, datetime


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
expected_columns = {'Date (Europe/London)', 'Solar radiation (W/m²)', 'UV index'}
if not expected_columns.issubset(data.columns):
    raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

# Select columns for processing
data = data[['Date (Europe/London)', 'Solar radiation (W/m²)', 'UV index']]

data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()
data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                              errors='coerce')

data = data.sort_values(by='Date (Europe/London)')

data['Solar radiation (W/m²)'] = (data['Solar radiation (W/m²)'].astype(str).str.replace(',', '', regex=True))

data['Solar radiation (W/m²)'] = pd.to_numeric(data['Solar radiation (W/m²)'], errors='coerce')

data['UV index'] = pd.to_numeric(data['UV index'], errors='coerce')

# Print data ranges
print("\n Date range found:")
print(f"    Start: {data['Date (Europe/London)'].min().strftime('%d/%m/%Y')}")
print(f"    End:   {data['Date (Europe/London)'].max().strftime('%d/%m/%Y')}")
print("\n Solar Radiation range found:")
y_min = (data['Solar radiation (W/m²)'].min())
y_max = (data['Solar radiation (W/m²)'].max())
print(f"    {y_min} - {y_max} W/m²")
print("\n UV Index range found:")
y_min = (data['UV index'].min())
y_max = (data['UV index'].max())
print(f"    {y_min} - {y_max}")

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
# Plot the atmospheric pressure data on the primary y-axis. Label is for legend.
ax1.bar(data['Date (Europe/London)'], data['Solar radiation (W/m²)'], linestyle='solid', color='gold',
        label='Solar radiation (W/m²)')
# Create a secondary y-axis
ax2 = ax1.twinx()
# Plot the secondary y-axis
ax2.plot(data['Date (Europe/London)'], data['UV index'], label='UV Index', color='red', linewidth=0.5)

# x axis configuration
x_min = data['Date (Europe/London)'].min()
x_max = data['Date (Europe/London)'].max()
margin = (x_max - x_min) * 0.01  # 1% of the data range
# Set the x-axis limits to fit the data exactly with reduced buffer
ax1.set_xlim(x_min - margin, x_max + margin)


def round_up_nearest(value, base):
    return math.ceil(value / base) * base


# Solar Radiation (larger range, round to nearest 10)
b_min = min(0, data['Solar radiation (W/m²)'].min())
b_max = round_up_nearest(data['Solar radiation (W/m²)'].max(), 10) +50 # +5 buffer
ax1.set_ylim(b_min, b_max)
ax1.minorticks_on()

# UV Index (smaller range, round to nearest 1 or 0.5 for precision)
a_min = min(0, data['UV index'].min())

# Always round up to the nearest 1, or 0.5 for better fit
a_max_raw = data['UV index'].max()
a_max = round_up_nearest(a_max_raw, 1) if a_max_raw > 5 else round_up_nearest(a_max_raw, 0.5)

ax2.set_ylim(a_min, a_max)
ax2.minorticks_on()

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
# Set axis labels
ax1.set_xlabel('Daily date markers')  # Date label
ax1.set_ylabel('Solar radiation')  # Label for y-axis (left).
ax2.set_ylabel('UV Index')  # Label for y-axis (right).

# Set chart Titles
fig.suptitle(f"{station_location} Solar Radiation & UV Index", fontsize=20)
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
# Compute UV Index statistics
uvmin_val = data['UV index'].min()
uvmax_val = data['UV index'].max()
uvavg_val = data['UV index'].mean()
uv_stat_handles = [
    Line2D([0], [0], color='white', lw=0, label=f'{uvmin_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{uvmax_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{uvavg_val:.2f}'),
]
# Compute 'Solar radiation (W/m²)' statistics
srmin_val = data['Solar radiation (W/m²)'].min()
srmax_val = data['Solar radiation (W/m²)'].max()
sravg_val = data['Solar radiation (W/m²)'].mean()
sr_stat_handles = [
    Line2D([0], [0], color='white', lw=0, label=f'{srmin_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{srmax_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{sravg_val:.2f}'),
]

# Combine and insert legends for the three datasets
lines2, labels2 = ax1.get_legend_handles_labels()
lines, labels = ax2.get_legend_handles_labels()
ax1.legend(stat_labels + lines + uv_stat_handles + lines2 + sr_stat_handles,
           [handle.get_label() for handle in stat_labels] + labels +
           [handle.get_label() for handle in uv_stat_handles] + labels2 +
           [handle.get_label() for handle in sr_stat_handles], loc='lower center', bbox_to_anchor=(0.5, -0.6),
           ncol=3,
           edgecolor='lightgray')

# Notes
ax1.text(0.5, -0.85,
         'Solar radiation is the electromagnetic radiation power received from the Sun measured in watts '
         'per square meter.\n'
         'UV Index is a measure of ultraviolet radiation intensity from the Sun,'
         'indicating potential risk for skin damage.\n\n'
         'Potential Risk: 0-2: Low    3-5: Moderate    6-7: High    8-10: Very High    11+: Extreme',
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
                            f'{station_location}_Solar_Radiation_v_UV_Index_Report.pdf')

with PdfPages(pdf_filename) as pdf:
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()

print(f'\n    Graph created & saved: {pdf_filename}\n')
