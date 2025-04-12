import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
import matplotlib.image as mpimg
from helpers.utilities import load_data, copyright_text, get_station_location
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
expected_columns = {'Date (Europe/London)', 'Rain (mm)'}
if not expected_columns.issubset(data.columns):
    raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

data = data[['Date (Europe/London)', 'Average wind speed (mph)', 'Average wind direction (°)']]

data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()

data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                              errors='coerce')

data = data.sort_values(by='Date (Europe/London)')

data['Average wind direction (°)'] = (data['Average wind direction (°)'].astype(str).str.replace(',', '', regex=True))
data['Average wind direction (°)'] = pd.to_numeric(data['Average wind direction (°)'], errors='coerce')

data['Average wind speed (mph)'] = pd.to_numeric(data['Average wind speed (mph)'], errors='coerce')

# Print data ranges
print("\n Date range found:")
print(f"    Start: {data['Date (Europe/London)'].min().strftime('%d-%m-%Y %H:%M hrs')}")
print(f"    End:   {data['Date (Europe/London)'].max().strftime('%d-%m-%Y %H:%M hrs')}")

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

fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape size
ax = fig.add_subplot(111, polar=True)

bins = np.linspace(0, 360, 9)
labels = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']  # Counter-clockwise order

data['Wind Direction Group'] = pd.cut(data['Average wind direction (°)'], bins=bins, labels=labels,
                                      include_lowest=True)

wind_speed_by_direction = data.groupby('Wind Direction Group',
                                       observed=False)['Average wind speed (mph)'].mean()

angles = np.linspace(0, 2 * np.pi, len(wind_speed_by_direction), endpoint=False)

ax.bar(angles, wind_speed_by_direction, width=0.4, bottom=0, color='blue', alpha=0.6)

ax.set_xticks(angles)
ax.set_xticklabels(wind_speed_by_direction.index, fontsize=12)

ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)

ax.set_yticklabels([])
ax.grid(False)

plt.tight_layout(pad=5.0)

# Titles
fig.suptitle(f"{station_location} Wind Direction Distribution", fontsize=20, y=0.95)
ax.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
             f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12, loc='center', y=1.05)

# Insert logo
logo = mpimg.imread("helpers/img/logo.jpg")
logo_ax = fig.add_axes([0.47, 0.06, 0.07, 0.07])  # left, bottom, width, height
logo_ax.imshow(logo, interpolation="antialiased")
logo_ax.axis("off")  # Hide axes around the logo

# Author details
ax.text(0.5, -0.25, copyright_text(), transform=ax.transAxes, fontsize=6, color='black',
        ha='center')

# Save to PDF with 1 cm margins
analytics_path = os.path.join('analytics/')
if not os.path.exists(analytics_path):
    os.makedirs(analytics_path)

current_date = date.today()
current_time = datetime.now()

pdf_filename = (f'{analytics_path}{current_date.strftime('%d%m%Y')}_{current_time.strftime('%H:%M')}hrs_'
                            f'{station_location}_Wind_Distribution_Report.pdf')

with PdfPages(pdf_filename) as pdf:
    plt.subplots_adjust(left=0.2, right=0.8, top=0.85, bottom=0.2)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()

print(f'\n    Graph created & saved: {pdf_filename}\n')