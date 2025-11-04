import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
import matplotlib.image as mpimg
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
expected_columns = {'Date (Europe/London)', 'Average wind speed (mph)'}
if not expected_columns.issubset(data.columns):
    raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

data = data[['Date (Europe/London)', 'Average wind speed (mph)']]

data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()

data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                              errors='coerce')

data = data.sort_values(by='Date (Europe/London)')

data['Average wind speed (mph)'] = (data['Average wind speed (mph)'].astype(str).str.replace(',', '', regex=True))

data['Average wind speed (mph)'] = pd.to_numeric(data['Average wind speed (mph)'], errors='coerce')

# Print data ranges
print("\n Date range found:")
print(f"    Start: {data['Date (Europe/London)'].min().strftime('%d/%m/%Y')}")
print(f"    End:   {data['Date (Europe/London)'].max().strftime('%d/%m/%Y')}")
print("\n Wind Speed range found:")
y_min = (data['Average wind speed (mph)'].min())
y_max = (data['Average wind speed (mph)'].max())
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
fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

# plot the data
ax.plot(data['Date (Europe/London)'], data['Average wind speed (mph)'], linestyle='solid', color='darkblue',
        label='Average wind speed') # Label for legend

# X-axis configuration
x_min = data['Date (Europe/London)'].min()
x_max = data['Date (Europe/London)'].max()
margin = (x_max - x_min) * 0.01  # 1% buffer
ax.set_xlim(x_min - margin, x_max + margin)

# Y-axis configuration with buffer
# Get min and max values from the dataset
a_min = data['Average wind speed (mph)'].min()
a_max = data['Average wind speed (mph)'].max()
# Round down min to the nearest 10, and up max to the nearest 10
y_min = np.floor(a_min / 5) * 5
y_max = np.ceil(a_max / 5) * 5
# Apply the new limits to the y-axis
ax.set_ylim(y_min, y_max)
ax.minorticks_on()

# Format the chart
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))
# Minor ticks for every day
ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))

# Enable grid
ax.grid(which='both', linestyle=':', linewidth=0.5, color='gainsboro')
ax.tick_params(axis='x', which='major', length=10, width=1, pad=5)
ax.tick_params(axis='x', which='minor', length=5, width=1, labelbottom=False)
# Set axis labels
ax.set_ylabel('Wind Speed')  # Label for y-axis (left).
ax.set_xlabel('Daily date markers')  # Date label

# Set chart Titles
fig.suptitle(f"{station_location} Wind Speed", fontsize=20)
ax.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
              f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12)

# Stats
# Remove NaN or infinite values
data = data.replace([np.inf, -np.inf], np.nan).dropna()
# Compute statistics
min_val = data['Average wind speed (mph)'].min()
max_val = data['Average wind speed (mph)'].max()
avg_val = data['Average wind speed (mph)'].mean()
# Superimpose Min, Max, and Avg lines
ax.axhline(min_val, color='lightblue', linestyle='--', label=f'Min: {min_val:.2f} mph')
ax.axhline(max_val, color='darkblue', linestyle='--', label=f'Max: {max_val:.2f} mph')
ax.axhline(avg_val, color='aqua', linestyle='--', label=f'Average: {avg_val:.2f} mph')
# Insert the legend
ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.35), ncol=4, edgecolor='lightgray', )  # show legend

# Notes
ax.text(0.5, -0.4, '"Wind Speed" is the average wind speed measured over short intervals.',
        transform=ax.transAxes, fontsize=10, color='black', ha='center')

# Insert logo
logo = mpimg.imread("helpers/img/logo.jpg")
logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
logo_ax.imshow(logo, interpolation="antialiased")
logo_ax.axis("off")  # Hide axes around the logo

# Author details
ax.text(0.5, -1.8, copyright_text(), transform=ax.transAxes, fontsize=6, color='black',
         ha='center')

ax.annotate(contact_details(), xy=(0.5, -1.83), ha='center', va='center', fontsize=7,
             color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

# Save to PDF with 1 cm margins
analytics_path = os.path.join('analytics/')
if not os.path.exists(analytics_path):
    os.makedirs(analytics_path)

current_date = date.today()
current_time = datetime.now()

pdf_filename = (f'{analytics_path}{current_date.strftime('%d%m%Y')}_{current_time.strftime('%H:%M')}hrs_'
                            f'{station_location}_Wind_Speed.pdf')

with PdfPages(pdf_filename) as pdf:
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()

print(f'\n    Graph created & saved: {pdf_filename}\n')
