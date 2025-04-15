import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from datetime import date, datetime
from helpers.utilities import (load_data, copyright_text, get_user_date_range, get_station_location, contact_details)


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def title(pdf, start_date, end_date):

    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

    data = data[['Date (Europe/London)']]

    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()
    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                                  errors='coerce')

    data = data.sort_values(by='Date (Europe/London)')

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    fig, ax = plt.subplots(figsize=(11.69, 8.27))

    fig.text(0.5, 0.55, station_location + ' Weather Report', fontsize=35, color='black', ha='center')

    fig.text(0.5, 0.45, f'{data['Date (Europe/London)'].min().strftime('%d %B %Y')}' + ' - ' +
             f'{data['Date (Europe/London)'].max().strftime('%d %B %Y')}',
             fontsize=30, color='black', ha='center')

    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")

    fig.text(0.5, 0.05, copyright_text(), fontsize=6, color='black', ha='center')

    ax.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')
    ax.axis('off')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Title Page")


def storms(pdf, start_date, end_date):
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

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    # Create the canvas
    fig, ax1 = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

    # plot the data
    # Plot rainfall data on the primary y-axis. Label is for legend.
    ax1.bar(data['Date (Europe/London)'], data['Rain (mm)'], color='darkblue', label='Rainfall')
    # Create a third y-axis
    ax2 = ax1.twinx()
    # Plot the Gust of Wind on the secondary y-axis. Label is for legend.
    ax2.plot(data['Date (Europe/London)'], data['Gust of wind (mph)'], linestyle='solid', color='cornflowerblue',
             label='Wind Gust', alpha=0.5)
    # Create a secondary y-axis
    ax3 = ax2.twinx()
    # Plot Air Pressure on the third y-axis. Label is for legend.
    ax3.plot(data['Date (Europe/London)'], data['Atmospheric pressure (mbar)'], linestyle='solid', color='lime',
             label='Air Pressure')

    # x axis configuration
    x_min = data['Date (Europe/London)'].min()
    x_max = data['Date (Europe/London)'].max()
    margin = (x_max - x_min) * 0.02  # 2% of the data range
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
    ax1.set_xlabel('Daily date markers')  # Date label
    ax1.set_ylabel('Rainfall (mm) & Wind Gust (mph)')  # Label for y-axis (left).
    ax3.set_ylabel('Air Pressure')  # Label for y-axis (right).

    # Set chart Titles
    fig.suptitle(f"{station_location} Storm Analysis", fontsize=20)
    ax1.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
                  f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12)

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
        Line2D([0], [0], color='white', lw=0, label=f'{minrain_val:.2f} mm'),
        Line2D([0], [0], color='white', lw=0, label=f'{maxrain_val:.2f} mm'),
        Line2D([0], [0], color='white', lw=0, label=f'{avgrain_val:.2f} mm'),
    ]
    # Compute Air Pressure stats
    minair_val = data['Atmospheric pressure (mbar)'].min()
    maxair_val = data['Atmospheric pressure (mbar)'].max()
    avgair_val = data['Atmospheric pressure (mbar)'].mean()
    air_stat_handles = [
        Line2D([0], [0], color='white', lw=0, label=f'{minair_val:.2f} mbar'),
        Line2D([0], [0], color='white', lw=0, label=f'{maxair_val:.2f} mbar'),
        Line2D([0], [0], color='white', lw=0, label=f'{avgair_val:.2f} mbar'),
    ]
    # Compute Wind Gust stats
    minwind_val = data['Gust of wind (mph)'].min()
    maxwind_val = data['Gust of wind (mph)'].max()
    avgwind_val = data['Gust of wind (mph)'].mean()
    wind_stat_handles = [
        Line2D([0], [0], color='white', lw=0, label=f'{minwind_val:.2f} mph'),
        Line2D([0], [0], color='white', lw=0, label=f'{maxwind_val:.2f} mph'),
        Line2D([0], [0], color='white', lw=0, label=f'{avgwind_val:.2f} mph'),
    ]

    # Combine and insert legends for the three datasets
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax1.legend(stat_labels + lines + rain_stat_handles + lines2 + wind_stat_handles + lines3 + air_stat_handles,
               [handle.get_label() for handle in stat_labels] + labels +
               [handle.get_label() for handle in rain_stat_handles] + labels2 +
               [handle.get_label() for handle in wind_stat_handles] + labels3 +
               [handle.get_label() for handle in air_stat_handles], loc='lower center', bbox_to_anchor=(0.5, -0.6),
               ncol=4,
               edgecolor='lightgray')

    # Notes
    ax1.text(0.5, -0.65,
             'Low air pressure is often linked to more turbulent weather, while higher air pressure tends to '
             'be associated with calmer, more stable weather.', transform=ax1.transAxes, fontsize=10,
             color='black', ha='center')

    # Insert logo
    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")  # Hide axes around the logo

    # Author details
    ax1.text(0.5, -1.83, copyright_text(), transform=ax1.transAxes, fontsize=6, color='black',
             ha='center')

    ax1.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Storms")


def humidity_rain(pdf, start_date, end_date):
    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)', 'Humidity (%)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

    data = data[['Date (Europe/London)', 'Humidity (%)', 'Rain (mm)']]

    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()
    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                                  errors='coerce')

    data = data.sort_values(by='Date (Europe/London)')

    data['Humidity (%)'] = (data['Humidity (%)'].astype(str).str.replace(',', '', regex=True))

    data['Humidity (%)'] = pd.to_numeric(data['Humidity (%)'], errors='coerce')

    data['Rain (mm)'] = (data['Rain (mm)'].astype(str).str.replace(',', '', regex=True))

    data['Rain (mm)'] = pd.to_numeric(data['Rain (mm)'], errors='coerce')

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    # Create the canvas
    fig, ax1 = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

    # plot the data
    # Plot the atmospheric pressure data on the primary y-axis. Label is for legend.
    ax1.bar(data['Date (Europe/London)'], data['Rain (mm)'], label='Rainfall', color='cornflowerblue')
    # Create a secondary y-axis
    ax2 = ax1.twinx()
    # Plot the secondary y-axis
    ax2.plot(data['Date (Europe/London)'], data['Humidity (%)'], linestyle='solid', color='blue',
             label='Humidity', alpha=0.7)

    # x axis configuration
    x_min = data['Date (Europe/London)'].min()
    x_max = data['Date (Europe/London)'].max()
    margin = (x_max - x_min) * 0.01  # 1% of the data range
    # Set the x-axis limits to fit the data exactly with reduced buffer
    ax1.set_xlim(x_min - margin, x_max + margin)

    # y axis configuration
    # Get y ax1 limits
    y_min, y_max = ax1.get_ylim()
    a_min = (data['Rain (mm)'].min())
    a_max = (data['Rain (mm)'].max())
    ax1.set_ylim(a_min, a_max)
    # Round y_min down to the nearest 10 and y_max up to the next 10
    y_min = np.floor(y_min / 10) * 10
    y_max = np.ceil(y_max / 10) * 10
    # Apply rounded limits to y ax1 both axes
    ax1.set_ylim(y_min, y_max)
    ax1.minorticks_on()

    # Get y ax2 limits
    y2_min, y2_max = ax2.get_ylim()
    b_min = (data['Humidity (%)'].min())
    b_max = (data['Humidity (%)'].max())
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
    ax1.set_ylabel('Rainfall (mm)')  # Label for y-axis (left).
    ax2.set_ylabel('Humidity (%)')  # Label for y-axis (right).

    # Set chart Titles
    fig.suptitle(f"{station_location} Humidity & Rainfall", fontsize=20)
    ax1.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
                  f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12)

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
    # Compute Rain statistics
    rmin_val = data['Rain (mm)'].min()
    rmax_val = data['Rain (mm)'].max()
    ravg_val = data['Rain (mm)'].mean()
    rain_stat_handles = [
        Line2D([0], [0], color='white', lw=0, label=f'{rmin_val:.2f} mm'),
        Line2D([0], [0], color='white', lw=0, label=f'{rmax_val:.2f} mm'),
        Line2D([0], [0], color='white', lw=0, label=f'{ravg_val:.2f} mm'),
    ]
    # Compute Humidity (%) statistics
    apmin_val = data['Humidity (%)'].min()
    apmax_val = data['Humidity (%)'].max()
    apavg_val = data['Humidity (%)'].mean()
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
    ax1.text(0.5, -0.65, 'Humidity is a measure of moisture in the air. 100% means fully saturated and cannot hold any '
                        'more.',
             transform=ax1.transAxes, fontsize=10, color='black', ha='center')

    # Insert logo
    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")  # Hide axes around the logo

    # Author details
    ax1.text(0.5, -1.83, copyright_text(), transform=ax1.transAxes, fontsize=6, color='black',
             ha='center')

    ax1.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Humidity against Rainfall")


def wind_speed_gust(pdf, start_date, end_date):
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

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    # Create the canvas
    fig, ax1 = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

    # plot the data
    # Plot average wind speed on the primary y-axis
    ax1.bar(data['Date (Europe/London)'], data['Average wind speed (mph)'], label='Wind speed',
            color='cornflowerblue')
    # Create a secondary y-axis
    ax2 = ax1.twinx()
    # Plot wind gust on the secondary y-axis
    ax2.plot(data['Date (Europe/London)'], data['Gust of wind (mph)'], linestyle='solid', color='darkblue',
             label='Gust of wind', alpha=0.3, linewidth=0.6)

    # X-axis configuration
    x_min = data['Date (Europe/London)'].min()
    x_max = data['Date (Europe/London)'].max()
    x_range = x_max - x_min  # Store range to avoid recomputation
    margin = x_range * 0.01  # 2% of the data range

    ax1.set_xlim(x_min - margin, x_max + margin)  # Apply limits with buffer

    # Y-axis configuration (Gust of wind)
    a_min = np.floor(data['Gust of wind (mph)'].min() / 10) * 10
    a_max = np.ceil(data['Gust of wind (mph)'].max() / 10) * 10

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
    ax1.set_ylabel('Wind Gust (mph)')  # Label for y-axis (left).

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
        Line2D([0], [0], color='white', lw=0, label=f'Minimum: '),
        Line2D([0], [0], color='white', lw=0, label=f'Maximum: '),
        Line2D([0], [0], color='white', lw=0, label=f'Average: '),
    ]
    # Compute average wind speed statistics
    awmin_val = data['Average wind speed (mph)'].min()
    awmax_val = data['Average wind speed (mph)'].max()
    awavg_val = data['Average wind speed (mph)'].mean()
    aw_stat_handles = [
        Line2D([0], [0], color='white', lw=0, label=f'{awmin_val:.2f} mph'),
        Line2D([0], [0], color='white', lw=0, label=f'{awmax_val:.2f} mph'),
        Line2D([0], [0], color='white', lw=0, label=f'{awavg_val:.2f} mph'),
    ]
    # Compute wind gust statistics
    wgmin_val = data['Gust of wind (mph)'].min()
    wgmax_val = data['Gust of wind (mph)'].max()
    wgavg_val = data['Gust of wind (mph)'].mean()
    wg_stat_handles = [
        Line2D([0], [0], color='white', lw=0, label=f'{wgmin_val:.2f} mph'),
        Line2D([0], [0], color='white', lw=0, label=f'{wgmax_val:.2f} mph'),
        Line2D([0], [0], color='white', lw=0, label=f'{wgavg_val:.2f} mph'),
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
    ax1.text(0.5, -1.83, copyright_text(), transform=ax1.transAxes, fontsize=6, color='black',
             ha='center')

    ax1.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Wind Speed against Wind Gust")


def solaruv(pdf, start_date, end_date):
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

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    # Create the canvas
    fig, ax1 = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

    # plot the data
    # Plot the atmospheric pressure data on the primary y-axis. Label is for legend.
    ax1.bar(data['Date (Europe/London)'], data['Solar radiation (W/m²)'], linestyle='solid', color='gold',
            label='Solar radiation')
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
    b_max = round_up_nearest(data['Solar radiation (W/m²)'].max(), 10)
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
    ax1.set_ylabel('Solar radiation (W/m²)')  # Label for y-axis (left).
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
        Line2D([0], [0], color='white', lw=0, label=f'Minimum: '),
        Line2D([0], [0], color='white', lw=0, label=f'Maximum: '),
        Line2D([0], [0], color='white', lw=0, label=f'Average: '),
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
        Line2D([0], [0], color='white', lw=0, label=f'{srmin_val:.2f} W/m²'),
        Line2D([0], [0], color='white', lw=0, label=f'{srmax_val:.2f} W/m²'),
        Line2D([0], [0], color='white', lw=0, label=f'{sravg_val:.2f} W/m²'),
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
    ax1.text(0.5, -1.83, copyright_text(), transform=ax1.transAxes, fontsize=6, color='black',
             ha='center')

    ax1.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Solar Radiation against UV Index")


def temperature(pdf, start_date, end_date):
    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)', 'Temperature (°C)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

    data = data[['Date (Europe/London)', 'Temperature (°C)']]

    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()
    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                                  errors='coerce')

    data = data.sort_values(by='Date (Europe/London)')

    data['Temperature (°C)'] = pd.to_numeric(data['Temperature (°C)'], errors='coerce')

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    # Create the canvas
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

    # plot the data
    ax.plot(data['Date (Europe/London)'], data['Temperature (°C)'], linestyle='solid', color='darkkhaki',
            label='Air Temperature')

    # X-axis configuration
    x_min = data['Date (Europe/London)'].min()
    x_max = data['Date (Europe/London)'].max()
    margin = (x_max - x_min) * 0.01  # 2% buffer
    ax.set_xlim(x_min - margin, x_max + margin)

    # Y-axis configuration with buffer
    y_min = data['Temperature (°C)'].min()
    y_max = data['Temperature (°C)'].max()
    buffer = (y_max - y_min) * 0.05  # 5% buffer

    # Apply rounding and buffer
    y_min = np.floor(y_min - buffer)
    y_max = np.ceil(y_max + buffer)

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
    ax.set_ylabel('Air Temperature (°C)')  # Label for y-axis (left).
    ax.set_xlabel('Daily date markers')  # Date label

    # Set chart Titles
    fig.suptitle(f"{station_location} Air Temperature", fontsize=20)
    ax.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
                  f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12)

    # Stats
    # Remove NaN or infinite values
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    # Compute statistics
    min_val = data['Temperature (°C)'].min()
    max_val = data['Temperature (°C)'].max()
    avg_val = data['Temperature (°C)'].mean()
    # Superimpose Min, Max, and Avg lines
    ax.axhline(min_val, color='deepskyblue', linestyle='--', label=f'Min: {min_val:.2f} °C')
    ax.axhline(max_val, color='lightcoral', linestyle='--', label=f'Max: {max_val:.2f} °C')
    ax.axhline(avg_val, color='gold', linestyle='--', label=f'Average: {avg_val:.2f} °C')
    # Insert the legend
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.35), ncol=4, edgecolor='lightgray', )  # show legend

    # Notes
    ax.text(0.5, -0.4, 'Temperatures shown are "ambient" (the temperature of the free flowing air '
                       'protected from direct sunlight).', transform=ax.transAxes, fontsize=10, color='black',
            ha='center')

    # Insert logo
    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")  # Hide axes around the logo

    # Author details
    ax.text(0.5, -1.83, copyright_text(), transform=ax.transAxes, fontsize=6, color='black',
            ha='center')

    ax.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Temperature")


def pressure(pdf, start_date, end_date):
    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)', 'Atmospheric pressure (mbar)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

    data = data[['Date (Europe/London)', 'Atmospheric pressure (mbar)']]

    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()

    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                                  errors='coerce')

    data = data.sort_values(by='Date (Europe/London)')

    data['Atmospheric pressure (mbar)'] = \
        (data['Atmospheric pressure (mbar)'].astype(str).str.replace(',', '', regex=True))

    data['Atmospheric pressure (mbar)'] = pd.to_numeric(data['Atmospheric pressure (mbar)'], errors='coerce')

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    # Create the canvas
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

    # plot the data
    ax.plot(data['Date (Europe/London)'], data['Atmospheric pressure (mbar)'], linestyle='solid', color='lime',
            label='Air pressure')  # Label for legend

    # X-axis configuration
    x_min = data['Date (Europe/London)'].min()
    x_max = data['Date (Europe/London)'].max()
    margin = (x_max - x_min) * 0.01  # 1% buffer
    ax.set_xlim(x_min - margin, x_max + margin)

    # Y-axis configuration with buffer
    y_min = data['Atmospheric pressure (mbar)'].min()
    y_max = data['Atmospheric pressure (mbar)'].max()
    buffer = (y_max - y_min) * 0.05  # 5% buffer

    # Apply rounding and buffer
    y_min = np.floor(y_min - buffer)
    y_max = np.ceil(y_max + buffer)

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
    ax.set_ylabel('Air Pressure (mbar)')  # Label for y-axis (left).
    ax.set_xlabel('Daily date markers')  # Date label

    # Set chart Titles
    fig.suptitle(f"{station_location} Air Pressure", fontsize=20)
    ax.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
                  f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12)

    # Stats
    # Remove NaN or infinite values
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    # Compute statistics
    min_val = data['Atmospheric pressure (mbar)'].min()
    max_val = data['Atmospheric pressure (mbar)'].max()
    avg_val = data['Atmospheric pressure (mbar)'].mean()
    # Superimpose Min, Max, and Avg lines
    ax.axhline(min_val, color='darkblue', linestyle='--', label=f'Min: {min_val:.2f} mbar')
    ax.axhline(max_val, color='lightcoral', linestyle='--', label=f'Max: {max_val:.2f} mbar')
    ax.axhline(avg_val, color='aqua', linestyle='--', label=f'Average: {avg_val:.2f} mbar')
    # Insert the legend
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.35), ncol=4, edgecolor='lightgray', )  # show legend

    # Notes
    ax.text(0.5, -0.4, 'Air pressure shown is "relative" (adjusted to sea level) allowing for comparison '
                       'between stations at different elevations.',
            transform=ax.transAxes, fontsize=10, color='black', ha='center')

    # Insert logo
    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")  # Hide axes around the logo

    # Author details
    ax.text(0.5, -1.83, copyright_text(), transform=ax.transAxes, fontsize=6, color='black',
            ha='center')

    ax.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Air Pressure")


def rain(pdf, start_date, end_date):
    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)', 'Rain (mm)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

    data = data[['Date (Europe/London)', 'Rain (mm)']]

    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()

    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                                  errors='coerce')

    data = data.sort_values(by='Date (Europe/London)')

    data['Rain (mm)'] = (data['Rain (mm)'].astype(str).str.replace(',', '', regex=True))

    data['Rain (mm)'] = pd.to_numeric(data['Rain (mm)'], errors='coerce')

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    # Identify the longest drought period
    data['Drought'] = data['Rain (mm)'].eq(0).astype(int)
    data['Drought_Group'] = (data['Drought'].ne(data['Drought'].shift())).astype(int).cumsum()
    drought_periods = data.groupby('Drought_Group').agg({'Date (Europe/London)': ['first', 'last'], 'Drought': 'sum'})
    longest_drought = drought_periods[drought_periods['Drought']['sum'] > 0].nlargest(1, ('Drought', 'sum'))

    if not longest_drought.empty:
        drought_start = longest_drought[('Date (Europe/London)', 'first')].values[0]
        drought_end = longest_drought[('Date (Europe/London)', 'last')].values[0]
        drought_dates = data[(data['Date (Europe/London)'] >= drought_start) & (data['Date (Europe/London)']
                                                                                <= drought_end)]
    else:
        drought_dates = pd.DataFrame()

    # Create the canvas
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

    # Stats
    # Remove NaN or infinite values
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    # Compute statistics
    min_val = data['Rain (mm)'].min()
    max_val = data['Rain (mm)'].max()
    avg_val = data['Rain (mm)'].mean()
    # Superimpose Min, Max, and Avg lines
    ax.axhline(min_val, color='deepskyblue', linestyle='', label=f'Min: {min_val:.2f} mm')
    ax.axhline(max_val, color='darkblue', linestyle='--', label=f'Max: {max_val:.2f} mm')
    ax.axhline(avg_val, color='aqua', linestyle='--', label=f'Average: {avg_val:.2f} mm')

    # plot the data
    # Includes label for the legend
    ax.bar(data['Date (Europe/London)'], data['Rain (mm)'], label='Daily Rainfall', color='cornflowerblue',
           linestyle='solid')
    if not drought_dates.empty:
        ax.axvspan(drought_start, drought_end, color='gainsboro', alpha=0.4, label='Driest Period')
        # Insert the legend with ordering capability
    handles, labels = ax.get_legend_handles_labels()
    order = [4, 1, 0, 2, 3]  # Reordered: Rainfall, Max, Min, Average, Max Drought
    ax.legend([handles[i] for i in order], [labels[i] for i in order],
              loc='lower center', bbox_to_anchor=(0.5, -0.35), ncol=5, edgecolor='lightgray')

    # X-axis configuration
    x_min = data['Date (Europe/London)'].min()
    x_max = data['Date (Europe/London)'].max()
    margin = (x_max - x_min) * 0.01  # 1% buffer
    ax.set_xlim(x_min - margin, x_max + margin)

    # y axis configuration
    # Get y ax1 limits
    y_min, y_max = ax.get_ylim()
    a_min = (data['Rain (mm)'].min())
    a_max = (data['Rain (mm)'].max())
    ax.set_ylim(a_min, a_max)
    # Round y_min down to the nearest 10 and y_max up to the next 10
    y_min = np.floor(y_min / 1) * 1
    y_max = np.ceil(y_max / 1) * 1
    # Apply rounded limits to y-axis
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
    ax.set_ylabel('Daily Rainfall (mm)')  # Label for y-axis (left).
    ax.set_xlabel('Daily date markers')  # Date label

    # Set chart Titles
    fig.suptitle(f"{station_location} Daily Rainfall", fontsize=20)
    ax.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
                  f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12)

    # Notes
    ax.text(0.5, -0.4, "'Driest Period' identifies the longest period without rainfall.",
            transform=ax.transAxes, fontsize=10, color='black', ha='center')

    # Insert logo
    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")  # Hide axes around the logo

    # Author details
    ax.text(0.5, -1.83, copyright_text(), transform=ax.transAxes, fontsize=6, color='black',
            ha='center')

    ax.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Rainfall")


def humidity(pdf, start_date, end_date):
    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)', 'Humidity (%)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

    data = data[['Date (Europe/London)', 'Humidity (%)']]

    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()

    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                                  errors='coerce')

    data = data.sort_values(by='Date (Europe/London)')

    data['Humidity (%)'] = (data['Humidity (%)'].astype(str).str.replace(',', '', regex=True))

    data['Humidity (%)'] = pd.to_numeric(data['Humidity (%)'], errors='coerce')

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    # Create the canvas
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

    # plot the data
    ax.plot(data['Date (Europe/London)'], data['Humidity (%)'], linestyle='solid', color='blue',
            label='Humidity')  # Label for legend

    # X-axis configuration
    x_min = data['Date (Europe/London)'].min()
    x_max = data['Date (Europe/London)'].max()
    margin = (x_max - x_min) * 0.01  # 2% buffer
    ax.set_xlim(x_min - margin, x_max + margin)

    # Y-axis configuration with buffer
    y_min = data['Humidity (%)'].min()
    y_max = data['Humidity (%)'].max()
    buffer = (y_max - y_min) * 0.05  # 5% buffer

    # Apply rounding and buffer
    y_min = np.floor(y_min - buffer)
    y_max = np.ceil(y_max + buffer)

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
    ax.set_ylabel('Humidity (%)')  # Label for y-axis (left).
    ax.set_xlabel('Daily date markers')  # Date label

    # Set chart Titles
    fig.suptitle(f"{station_location} Air Humidity", fontsize=20)
    ax.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
                  f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12)

    # Stats
    # Remove NaN or infinite values
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    # Compute statistics
    min_val = data['Humidity (%)'].min()
    max_val = data['Humidity (%)'].max()
    avg_val = data['Humidity (%)'].mean()
    # Superimpose Min, Max, and Avg lines
    ax.axhline(min_val, color='lightblue', linestyle='--', label=f'Min: {min_val:.2f} %')
    ax.axhline(max_val, color='darkblue', linestyle='--', label=f'Max: {max_val:.2f} %')
    ax.axhline(avg_val, color='aqua', linestyle='--', label=f'Average: {avg_val:.2f} %')
    # Insert the legend
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.35), ncol=4, edgecolor='lightgray', )  # show legend

    # Notes
    ax.text(0.5, -0.4,
            'Humidity is a measure of moisture in the air. 100% means fully saturated and cannot hold any more.',
            transform=ax.transAxes, fontsize=10, color='black', ha='center')

    # Insert logo
    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")  # Hide axes around the logo

    # Author details
    ax.text(0.5, -1.83, copyright_text(), transform=ax.transAxes, fontsize=6, color='black',
            ha='center')

    ax.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Humidity")


def wind_speed(pdf, start_date, end_date):
    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)', 'Average wind speed (mph)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

    data = data[['Date (Europe/London)', 'Average wind speed (mph)']]
    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()

    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'],
                                                  format='%Y-%m-%d %H:%M:%S', errors='coerce')

    data = data.sort_values(by='Date (Europe/London)')

    data['Average wind speed (mph)'] = (data['Average wind speed (mph)'].astype(str).str.replace(',', '', regex=True))

    data['Average wind speed (mph)'] = pd.to_numeric(data['Average wind speed (mph)'], errors='coerce')

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

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
    y_min = np.floor(a_min / 10) * 10
    y_max = np.ceil(a_max / 10) * 10
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
    ax.set_ylabel('Wind Speed (mph)')  # Label for y-axis (left).
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
    ax.text(0.5, -0.4, '"Wind Speed" is the average wind speed measured over short intervals',
            transform=ax.transAxes, fontsize=10, color='black', ha='center')

    # Insert logo
    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")  # Hide axes around the logo

    # Author details
    ax.text(0.5, -1.83, copyright_text(), transform=ax.transAxes, fontsize=6, color='black',
             ha='center')

    ax.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Wind Speed")


def wind_gust(pdf, start_date, end_date):
    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)', 'Gust of wind (mph)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

    data = data[['Date (Europe/London)', 'Gust of wind (mph)']]
    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()

    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

    data = data.sort_values(by='Date (Europe/London)')

    data['Gust of wind (mph)'] = (data['Gust of wind (mph)'].astype(str).str.replace(',', '', regex=True))

    data['Gust of wind (mph)'] = pd.to_numeric(data['Gust of wind (mph)'], errors='coerce')

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    # Create the canvas
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

    # plot the data
    ax.plot(data['Date (Europe/London)'], data['Gust of wind (mph)'], linestyle='solid', color='darkblue',
            label='Wind Gust') # Label for legend

    # X-axis configuration
    x_min = data['Date (Europe/London)'].min()
    x_max = data['Date (Europe/London)'].max()
    margin = (x_max - x_min) * 0.01  # 1% buffer
    ax.set_xlim(x_min - margin, x_max + margin)

    # Y-axis configuration with buffer
        # Get min and max values from the dataset
    a_min = data['Gust of wind (mph)'].min()
    a_max = data['Gust of wind (mph)'].max()
    # Round down min to the nearest 10, and up max to the nearest 10
    y_min = np.floor(a_min / 10) * 10
    y_max = np.ceil(a_max / 10) * 10
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
    ax.set_ylabel('Wind Gust (mph)') # Label for y-axis (left).
    ax.set_xlabel('Daily date markers')  # Date label

    # Set chart Titles
    fig.suptitle(f"{station_location} Wind Gust", fontsize=20)
    ax.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
                  f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12)

    # Stats
        # Remove NaN or infinite values
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
        # Compute statistics
    min_val = data['Gust of wind (mph)'].min()
    max_val = data['Gust of wind (mph)'].max()
    avg_val = data['Gust of wind (mph)'].mean()
        # Superimpose Min, Max, and Avg lines
    ax.axhline(min_val, color='lightblue', linestyle='--', label=f'Min: {min_val:.2f} mph')
    ax.axhline(max_val, color='darkblue', linestyle='--', label=f'Max: {max_val:.2f} mph')
    ax.axhline(avg_val, color='aqua', linestyle='--', label=f'Average: {avg_val:.2f} mph')
        # Insert the legend
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.35), ncol=4, edgecolor='lightgray', ) # show legend

    # Notes
    ax.text(0.5, -0.4, '"Wind Gust" is the biggest gust of wind measured over short intervals.',
            transform=ax.transAxes, fontsize=10, color='black', ha='center')

    # Insert logo
    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")  # Hide axes around the logo

    # Author details
    ax.text(0.5, -1.83, copyright_text(), transform=ax.transAxes, fontsize=6, color='black',
             ha='center')

    ax.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Wind Gust")


def wind_direction(pdf, start_date, end_date):
    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)', 'Average wind speed (mph)', 'Average wind direction (°)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()
    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                                  errors='coerce')

    data = data.sort_values(by='Date (Europe/London)')

    data['Average wind direction (°)'] = (data['Average wind direction (°)'].astype(str).str.replace(',', '',
                                                                                                     regex=True))

    data['Average wind direction (°)'] = pd.to_numeric(data['Average wind direction (°)'], errors='coerce')

    data['Average wind speed (mph)'] = pd.to_numeric(data['Average wind speed (mph)'], errors='coerce')

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

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

    ax.annotate(contact_details(), xy=(0.5, -0.27), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.2, right=0.8, top=0.85, bottom=0.2)
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Wind Direction Distribution")


def temperature_indoor(pdf, start_date, end_date):
    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)', 'Inside temperature (°C)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

    data = data[['Date (Europe/London)', 'Inside temperature (°C)']]

    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()
    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                                  errors='coerce')

    data = data.sort_values(by='Date (Europe/London)')

    data['Inside temperature (°C)'] = pd.to_numeric(data['Inside temperature (°C)'], errors='coerce')

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    # Create the canvas
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

    # plot the data
    ax.plot(data['Date (Europe/London)'], data['Inside temperature (°C)'], linestyle='solid', color='darkkhaki',
            label='Inside temperature')

    # X-axis configuration
    x_min = data['Date (Europe/London)'].min()
    x_max = data['Date (Europe/London)'].max()
    margin = (x_max - x_min) * 0.01  # 2% buffer
    ax.set_xlim(x_min - margin, x_max + margin)

    # Y-axis configuration with buffer
    y_min = data['Inside temperature (°C)'].min()
    y_max = data['Inside temperature (°C)'].max()
    buffer = (y_max - y_min) * 0.05  # 5% buffer

    # Apply rounding and buffer
    y_min = np.floor(y_min - buffer)
    y_max = np.ceil(y_max + buffer)

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
    ax.set_ylabel('Indoor Air Temperature (°C)')  # Label for y-axis (left).
    ax.set_xlabel('Daily date markers')  # Date label

    # Set chart Titles
    fig.suptitle("Indoor Air Temperature", fontsize=20)
    ax.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
                  f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12)

    # Stats
    # Remove NaN or infinite values
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    # Compute statistics
    min_val = data['Inside temperature (°C)'].min()
    max_val = data['Inside temperature (°C)'].max()
    avg_val = data['Inside temperature (°C)'].mean()
    # Superimpose Min, Max, and Avg lines
    ax.axhline(min_val, color='deepskyblue', linestyle='--', label=f'Min: {min_val:.2f} °C')
    ax.axhline(max_val, color='lightcoral', linestyle='--', label=f'Max: {max_val:.2f} °C')
    ax.axhline(avg_val, color='gold', linestyle='--', label=f'Average: {avg_val:.2f} °C')
    # Insert the legend
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.35), ncol=4, edgecolor='lightgray', )  # show legend

    # Notes
    ax.text(0.5, -0.4, 'Temperatures shown are "ambient" (the temperature of the free flowing air '
                       'protected from direct sunlight).', transform=ax.transAxes, fontsize=10, color='black',
            ha='center')

    # Insert logo
    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")  # Hide axes around the logo

    # Author details
    ax.text(0.5, -1.83, copyright_text(), transform=ax.transAxes, fontsize=6, color='black',
            ha='center')

    ax.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Indoor Temperature")


def humidity_indoor(pdf, start_date, end_date):
    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)', 'Inside humidity (%)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")

    data = data[['Date (Europe/London)', 'Inside humidity (%)']]

    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()

    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                                  errors='coerce')

    data = data.sort_values(by='Date (Europe/London)')

    data['Inside humidity (%)'] = (data['Inside humidity (%)'].astype(str).str.replace(',', '', regex=True))

    data['Inside humidity (%)'] = pd.to_numeric(data['Inside humidity (%)'], errors='coerce')

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

    # Create the canvas
    fig, ax = plt.subplots(figsize=(11.69, 8.27))  # A4 landscape size in inches

    # plot the data
    ax.plot(data['Date (Europe/London)'], data['Inside humidity (%)'], linestyle='solid', color='blue',
            label='Indoor Air Humidity')  # Label for legend

    # X-axis configuration
    x_min = data['Date (Europe/London)'].min()
    x_max = data['Date (Europe/London)'].max()
    margin = (x_max - x_min) * 0.01  # 2% buffer
    ax.set_xlim(x_min - margin, x_max + margin)

    # Y-axis configuration with buffer
    y_min = data['Inside humidity (%)'].min()
    y_max = data['Inside humidity (%)'].max()
    buffer = (y_max - y_min) * 0.05  # 5% buffer

    # Apply rounding and buffer
    y_min = np.floor(y_min - buffer)
    y_max = np.ceil(y_max + buffer)

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
    ax.set_ylabel('Indoor Air Humidity (%)')  # Label for y-axis (left).
    ax.set_xlabel('Daily date markers')  # Date label

    # Set chart Titles
    fig.suptitle("Indoor Air Humidity", fontsize=20)
    ax.set_title(f"{data['Date (Europe/London)'].min().strftime('%d %B %Y')} - "
                  f"{data['Date (Europe/London)'].max().strftime('%d %B %Y')}", fontsize=12)

    # Stats
    # Remove NaN or infinite values
    data = data.replace([np.inf, -np.inf], np.nan).dropna()
    # Compute statistics
    min_val = data['Inside humidity (%)'].min()
    max_val = data['Inside humidity (%)'].max()
    avg_val = data['Inside humidity (%)'].mean()
    # Superimpose Min, Max, and Avg lines
    ax.axhline(min_val, color='lightblue', linestyle='--', label=f'Min: {min_val:.2f} %')
    ax.axhline(max_val, color='darkblue', linestyle='--', label=f'Max: {max_val:.2f} %')
    ax.axhline(avg_val, color='aqua', linestyle='--', label=f'Average: {avg_val:.2f} %')
    # Insert the legend
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.35), ncol=4, edgecolor='lightgray', )  # show legend

    # Notes
    ax.text(0.5, -0.4,
            'Humidity is a measure of moisture in the air. 100% means fully saturated and cannot hold any more.',
            transform=ax.transAxes, fontsize=10, color='black', ha='center')

    # Insert logo
    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.08, 0.07, 0.07])  # Adjust position & size (left, bottom, width, height)
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")  # Hide axes around the logo

    # Author details
    ax.text(0.5, -1.83, copyright_text(), transform=ax.transAxes, fontsize=6, color='black',
            ha='center')

    ax.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Indoor Humidity")


def temperature_humidity_indoor(pdf, start_date, end_date):
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

    data = data[(data['Date (Europe/London)'] >= start_date) & (data['Date (Europe/London)'] <= end_date)]
    if data.empty:
        print("\n\033[1;93m Warning: No data available for the selected date range.\n"
              " Use function 1 to check the database date range.\033[0m\n")
        return

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
    ax1.text(0.5, -1.83, copyright_text(), transform=ax1.transAxes, fontsize=6, color='black',
            ha='center')

    ax1.annotate(contact_details(), xy=(0.5, -1.9), ha='center', va='center', fontsize=7,
                 color='blue', xycoords='axes fraction', url=f'mailto:{contact_details()}')

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.6)  # 1 cm margins
    pdf.savefig(fig, dpi=300)
    plt.close()
    print("    Generated Chart: Humidity")


def generate_full_report():
    data = load_data()

    data.columns = [col.strip() for col in data.columns]
    expected_columns = {'Date (Europe/London)'}
    if not expected_columns.issubset(data.columns):
        raise ValueError(f"Missing expected columns: {expected_columns - set(data.columns)}")
    data = data[['Date (Europe/London)']]
    data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()
    data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S',
                                                  errors='coerce')
    data = data.sort_values(by='Date (Europe/London)')
    # Print data ranges
    print("\n Date range found:")
    print(f"    Start: {data['Date (Europe/London)'].min().strftime('%d-%m-%Y %H:%M hrs')}")
    print(f"    End:   {data['Date (Europe/London)'].max().strftime('%d-%m-%Y %H:%M hrs')}")

    start_date, end_date = get_user_date_range(data)

    analytics_path = 'analytics/'
    os.makedirs(analytics_path, exist_ok=True)

    current_date = date.today()
    current_time = datetime.now()

    public_pdf_filename = (f'{analytics_path}{current_date.strftime('%d%m%Y')}_{current_time.strftime('%H:%M')}hrs_'
                           f'{station_location}_Public_Weather_Report.pdf')

    with PdfPages(public_pdf_filename) as pdf:
        title(pdf, start_date, end_date)
        storms(pdf, start_date, end_date)
        humidity_rain(pdf, start_date, end_date)
        wind_speed_gust(pdf, start_date, end_date)
        solaruv(pdf, start_date, end_date)
        temperature(pdf, start_date, end_date)
        pressure(pdf, start_date, end_date)
        rain(pdf, start_date, end_date)
        humidity(pdf, start_date, end_date)
        wind_speed(pdf, start_date, end_date)
        wind_gust(pdf, start_date, end_date)
        wind_direction(pdf, start_date, end_date)

    print(f'\n\033[1;93m    Public report generated: '
          f'\n    {public_pdf_filename}\n\033[0m')

    private_pdf_filename = (f'{analytics_path}{current_date.strftime('%d%m%Y')}_{current_time.strftime('%H:%M')}hrs_'
                            f'{station_location}_Private_Weather_Report.pdf')

    with PdfPages(private_pdf_filename) as pdf:
        temperature_indoor(pdf, start_date, end_date)
        humidity_indoor(pdf, start_date, end_date)
        temperature_humidity_indoor(pdf, start_date, end_date)

    print(f'\n\033[1;93m    Private report generated: '
          f'\n    {private_pdf_filename}\n\033[0m')


def main():
    try:
        generate_full_report()
    except Exception as e:
        print(f"{e}")


station_location = get_station_location()


if __name__ == '__main__':
    main()
