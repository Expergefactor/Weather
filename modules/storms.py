import os
import chardet
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
import matplotlib.image as mpimg
from matplotlib.lines import Line2D
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
expected_columns = {'Date (Europe/London)', 'Atmospheric pressure (mbar)', 'Rain (mm)', 'Gust of wind (mph)'}
if not expected_columns.issubset(data.columns):
    raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

data = data[['Date (Europe/London)', 'Atmospheric pressure (mbar)', 'Rain (mm)', 'Gust of wind (mph)']]

data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()
data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                              errors='coerce')

data = data.sort_values(by='Date (Europe/London)')

data['Atmospheric pressure (mbar)'] = \
    (data['Atmospheric pressure (mbar)'].astype(str).str.replace(',', '', regex=True))
data['Atmospheric pressure (mbar)'] = pd.to_numeric(data['Atmospheric pressure (mbar)'], errors='coerce')

data['Rain (mm)'] = pd.to_numeric(data['Rain (mm)'], errors='coerce')

data['Gust of wind (mph)'] = (data['Gust of wind (mph)'].astype(str).str.replace(',', '', regex=True))
data['Gust of wind (mph)'] = pd.to_numeric(data['Gust of wind (mph)'], errors='coerce')

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
    # Plot rainfall data on the primary y-axis. Label is for legend.
ax1.bar(data['Date (Europe/London)'], data['Rain (mm)'], color='darkblue', label='Rainfall (mm)')
    # Create a third y-axis
ax2 = ax1.twinx()
    # Plot the Gust of Wind on the secondary y-axis. Label is for legend.
ax2.plot(data['Date (Europe/London)'], data['Gust of wind (mph)'], linestyle='solid', color='cornflowerblue',
         label='Wind Gust (mph)', alpha=0.5)
    # Create a secondary y-axis
ax3 = ax2.twinx()
    # Plot Air Pressure on the third y-axis. Label is for legend.
ax3.plot(data['Date (Europe/London)'], data['Atmospheric pressure (mbar)'], linestyle='solid', color='lime',
         label='Air Pressure (mbar)')

# x axis configuration
x_min = data['Date (Europe/London)'].min()
x_max = data['Date (Europe/London)'].max()
margin = (x_max - x_min) * 0.02 # 2% of the data range
    # Set the x-axis limits to fit the data exactly with reduced buffer
ax1.set_xlim(x_min - margin, x_max + margin)

    # Compute and round y-axis limits for ax1 (Gust of Wind)
buffer = 5
a_min = data['Gust of wind (mph)'].min()
a_max = data['Gust of wind (mph)'].max()
y_min = np.floor(a_min / 10) * 10
y_max = np.ceil(a_max / 10) * 10 + buffer
ax1.set_ylim(y_min, y_max)
ax1.minorticks_on()

    # Ensure ax2 mirrors ax1's scale without modifying labels or ticks
ax2.set_ylim(y_min, y_max)
ax2.yaxis.set_ticks_position('right')
ax2.set_yticks([])  # Removes y-ticks on ax2

    # Compute and round y-axis limits for ax3 (Atmospheric Pressure)
b_min = data['Atmospheric pressure (mbar)'].min()
b_max = data['Atmospheric pressure (mbar)'].max()
y3_min = np.floor(b_min / 10) * 10
y3_max = np.ceil(b_max / 10) * 10
ax3.set_ylim(y3_min, y3_max)
ax3.minorticks_on()

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
    # Date label can be added if required: ax1.set_xlabel('Date', fontsize=8)
ax1.set_ylabel('Rainfall & Wind Gust') # Label for y-axis (left).
ax3.set_ylabel('Air Pressure') # Label for y-axis (right).

# Set chart Titles
fig.suptitle(f'{station_location} Storm Analysis', fontsize=20)
ax1.set_title(f"{data['Date (Europe/London)'].min().strftime('%B %Y')} - "
             f"{data['Date (Europe/London)'].max().strftime('%B %Y')}", fontsize=12)

# Stats
   # Remove NaN or infinite values
data = data.replace([np.inf, -np.inf], np.nan).dropna()
    # Stat Labels
stat_labels = [
    Line2D([0], [0], color='white', lw=0, label=f''),
    Line2D([0], [0], color='white', lw=0, label=f'Minimum: '),
    Line2D([0], [0], color='white', lw=0, label=f'Maximum: '),
    Line2D([0], [0], color='white', lw=0, label=f'Average: '),
]
    # Compute Rain statistics
minrain_val = data['Rain (mm)'].min()
maxrain_val = data['Rain (mm)'].max()
avgrain_val = data['Rain (mm)'].mean()
rain_stat_handles = [
    Line2D([0], [0], color='white', lw=0, label=f'{minrain_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{maxrain_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{avgrain_val:.2f}'),
]
    # Compute Air Pressure stats
minair_val = data['Atmospheric pressure (mbar)'].min()
maxair_val = data['Atmospheric pressure (mbar)'].max()
avgair_val = data['Atmospheric pressure (mbar)'].mean()
air_stat_handles = [
    Line2D([0], [0], color='white', lw=0, label=f'{minair_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{maxair_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{avgair_val:.2f}'),
]
    # Compute Wind Gust stats
minwind_val = data['Gust of wind (mph)'].min()
maxwind_val = data['Gust of wind (mph)'].max()
avgwind_val = data['Gust of wind (mph)'].mean()
wind_stat_handles = [
    Line2D([0], [0], color='white', lw=0, label=f'{minwind_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{maxwind_val:.2f}'),
    Line2D([0], [0], color='white', lw=0, label=f'{avgwind_val:.2f}'),
]

# Combine and insert legends for the three datasets
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
lines3, labels3 = ax3.get_legend_handles_labels()
ax1.legend(stat_labels + lines + rain_stat_handles + lines2 + wind_stat_handles + lines3 + air_stat_handles,
           [handle.get_label() for handle in stat_labels] + labels +
           [handle.get_label() for handle in rain_stat_handles] + labels2 +
           [handle.get_label() for handle in wind_stat_handles] + labels3 +
           [handle.get_label() for handle in air_stat_handles], loc='lower center', bbox_to_anchor=(0.5, -0.55), ncol=4,
           edgecolor='lightgray')

# Notes
ax1.text(0.5, -0.6, 'Low air pressure is often linked to more turbulent weather, while higher air pressure tends to '
                    'be associated with calmer, more stable weather.', transform=ax1.transAxes, fontsize=10,
         color='black', ha='center')

# Insert logo
logo = mpimg.imread("helpers/img/logo.jpg")
logo_ax = fig.add_axes([0.47, 0.09, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
logo_ax.imshow(logo, interpolation="antialiased")
logo_ax.axis("off")  # Hide axes around the logo

# Author details
ax1.text(0.5, -1.8, copyright_text(), transform=ax1.transAxes, fontsize=7, color='black',
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
                            f'{station_location}_Storms_Report.pdf')

with PdfPages(pdf_filename) as pdf:
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()

print(f'\n    Graph created & saved: {pdf_filename}\n')
