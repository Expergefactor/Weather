import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
import matplotlib.image as mpimg
from matplotlib.lines import Line2D
from datetime import date, datetime
from helpers.utilities import load_data, copyright_text, get_user_date_range, get_station_location, contact_details

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
expected_columns = {'Date (Europe/London)', 'Inside humidity (%)', 'Inside temperature (°C)'}
if not expected_columns.issubset(data.columns):
    raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

data = data[['Date (Europe/London)', 'Inside humidity (%)', 'Inside temperature (°C)']]

data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()
data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                              errors='coerce')

data = data.sort_values(by='Date (Europe/London)')

data['Inside humidity (%)'] = (data['Inside humidity (%)'].astype(str).str.replace(',', '', regex=True))
data['Inside humidity (%)'] = pd.to_numeric(data['Inside humidity (%)'], errors='coerce')

data['Inside temperature (°C)'] = pd.to_numeric(data['Inside temperature (°C)'], errors='coerce')

print("\n Date range found:")
print(f"    Start: {data['Date (Europe/London)'].min().strftime('%d/%m/%Y')}")
print(f"    End:   {data['Date (Europe/London)'].max().strftime('%d/%m/%Y')}")
print("\n Inside Humidity range found:")
y_min = (data['Inside humidity (%)'].min())
y_max = (data['Inside humidity (%)'].max())
print(f"    {y_min} - {y_max} %")
print("\n Inside Temperature range found:")
y_min = (data['Inside temperature (°C)'].min())
y_max = (data['Inside temperature (°C)'].max())
print(f"    {y_min} - {y_max} °C")

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
ax1.bar(data['Date (Europe/London)'], data['Inside temperature (°C)'], label='Indoor temperature',
        color='darkkhaki')
# Create a secondary y-axis
ax2 = ax1.twinx()
# Plot the secondary y-axis
ax2.plot(data['Date (Europe/London)'], data['Inside humidity (%)'], linestyle='solid', color='blue',
         label='Indoor humidity', alpha=0.7)

# x axis configuration
x_min = data['Date (Europe/London)'].min()
x_max = data['Date (Europe/London)'].max()
margin = (x_max - x_min) * 0.01  # 1% of the data range
# Set the x-axis limits to fit the data exactly with reduced buffer
ax1.set_xlim(x_min - margin, x_max + margin)

# y axis configuration
# Get y ax1 limits
y_min, y_max = ax1.get_ylim()
a_min = (data['Inside temperature (°C)'].min())
a_max = (data['Inside temperature (°C)'].max())
ax1.set_ylim(a_min, a_max)
# Round y_min down to the nearest 10 and y_max up to the next 10
y_min = np.floor(y_min / 10) * 10
y_max = np.ceil(y_max / 10) * 10
# Apply rounded limits to y ax1 both axes
ax1.set_ylim(y_min, y_max)
ax1.minorticks_on()

# Get y ax2 limits
y2_min, y2_max = ax2.get_ylim()
b_min = (data['Inside humidity (%)'].min())
b_max = (data['Inside humidity (%)'].max())
ax2.set_ylim(b_min, b_max)
# Round y2_min down to the nearest 10 and y2_max up to the next 10
y2_min = np.floor(y2_min / 5) * 5
y2_max = np.ceil(y2_max / 5) * 5
# Apply rounded limits to y ax3 both axes
ax2.set_ylim(y2_min, y2_max)
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
ax1.set_ylabel('Indoor Temperature (°C)')  # Label for y-axis (left).
ax2.set_ylabel('Indoor Humidity (%)')  # Label for y-axis (right).

# Set chart Titles
fig.suptitle("Indoor Temperature & Humidity", fontsize=20)
ax1.set_title(f"{data['Date (Europe/London)'].min().strftime('%B %Y')} - "
              f"{data['Date (Europe/London)'].max().strftime('%B %Y')}", fontsize=12)

# Stats
# Remove NaN or infinite values
data = data.replace([np.inf, -np.inf], np.nan).dropna()
# Set Max, Min, & Avg legend labels
stat_labels = [
    Line2D([0], [0], color='white', lw=0, label=f''),
    Line2D([0], [0], color='white', lw=0, label=f'Minimum: '),
    Line2D([0], [0], color='white', lw=0, label=f'Maximum: '),
    Line2D([0], [0], color='white', lw=0, label=f'Average: '),
]
# Compute Indoor temperature statistics
rmin_val = data['Inside temperature (°C)'].min()
rmax_val = data['Inside temperature (°C)'].max()
ravg_val = data['Inside temperature (°C)'].mean()
rain_stat_handles = [
    Line2D([0], [0], color='white', lw=0, label=f'{rmin_val:.2f} °C'),
    Line2D([0], [0], color='white', lw=0, label=f'{rmax_val:.2f} °C'),
    Line2D([0], [0], color='white', lw=0, label=f'{ravg_val:.2f} °C'),
]
# Compute Indoor humidity (%) statistics
apmin_val = data['Inside humidity (%)'].min()
apmax_val = data['Inside humidity (%)'].max()
apavg_val = data['Inside humidity (%)'].mean()
ap_stat_handles = [
    Line2D([0], [0], color='white', lw=0, label=f'{apmin_val:.2f} %'),
    Line2D([0], [0], color='white', lw=0, label=f'{apmax_val:.2f} %'),
    Line2D([0], [0], color='white', lw=0, label=f'{apavg_val:.2f} %'),
]

# Combine and insert legends for the three datasets
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(stat_labels + lines + rain_stat_handles + lines2 + ap_stat_handles,
           [handle.get_label() for handle in stat_labels] + labels +
           [handle.get_label() for handle in rain_stat_handles] + labels2 +
           [handle.get_label() for handle in ap_stat_handles], loc='lower center', bbox_to_anchor=(0.5, -0.6),
           ncol=3,
           edgecolor='lightgray')

# Notes
ax1.text(0.5, -0.65,
        'Humidity is a measure of moisture in the air. 100% means fully saturated and cannot hold any more.',
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
                            f'{station_location}_Indoor_Humidity_Report.pdf')

with PdfPages(pdf_filename) as pdf:
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()

print(f'\n    Graph created & saved: {pdf_filename}\n')