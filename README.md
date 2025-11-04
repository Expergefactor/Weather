# Weather
Weather Analytics for weather stations

Autumn 2025 Update...

Bugs squished:
 * Removed some redundant imports
 * Fixed rain/wind gust scaling issue in storms analysis
 * Fixed solar radiation scaling issue in Solar Radiation & UV Index analysis
 * Fixed date axis buffer issue on some analytics
 * Fixed units repetition on full report chats keys
 * Adjusted some axis labels

New features:
 * Updated main menu.
 * Updated help & information.
 * New utility added to normalise older date formats.
 * Log generation for cleansed lines when normalising files.
 * Compiled databases are now sorted chronologically.
 * 'Snapshot' feature 

Main Menu:

![menu](https://github.com/Expergefactor/Weather/blob/main/helpers/img/menu.png)

Sub Menu (option 2 from main menu):

![menu2](https://github.com/Expergefactor/Weather/blob/main/helpers/img/menu2.jpg)

# WHAT IS IT?
This software is designed to be used with weather station data and provides a total of 14 analytics:
 * 11 public (outdoor data).
 * 3 private (indoor data).
 * 'Snapshot' feature provides an 'at a glance', single page report.

You have the option of:
*   generating a full report (main menu, option 1) which conducts analytics on all datasets or,
*   conducting a single report (sub menu, option 2) for an individual dataset or,
*   Creating a 'Snapshot' (main menu, option 3) provides an 'at a glance', single page report for:

    * Hottest Day
    * Driest Period
    * Coldest Day
    * Wettest Day
    * Biggest Downpour
    * Total Rainfall
    * Windiest Day
    * Average wind direction
    * Snapshot reports on 3 criteria: 
    * For the user-defined date period,
    * For 'Year-To-Date' &,
    * Since your records began. 

# WHAT DOES IT DO?
You can view examples of the analytics in the '/example' folder. Note: individual reports created from the sub-menu are identical to those contained in the full reports when using the main menu, it is just a function provided to enable an individual report to be created without generating a report for every type of metric. 

# HOW TO USE IT
 * Download the package to a local directory.
 * Run terminal, cd to the package root dir.
 * Put all weather station .csv files into folder: "database/original/"
 * run 'python3 menu.py'
 * Normalise the original files
 * Compile the database
 * Generate reports

# COMPONENTS:
System:
  * menu.py         Control module for all functions
  * compile.py	     Compiles database files in preparation for processing
  * utilities.py    Hosts various supporting functions
  * report_full.py  Conducts all available analytics and generates two reports (private & public).

Snapshot
  * snapshot.py         Create a glance view of key statistics.
  
Private Analytics:
  * indoor_temp.py      Charting - indoor air temperature (line) over time.
  * indoor_humidity.py 	Charting - indoor humidity (line) over time.
  * indoor_humidtemp.py Charting - indoor air temperature (bar) against humidity (line) over time.
  
Public Analytics:
  * humidity.py         Charting - humidity (line) over time.
  * humidityrain.py     Charting - humidity (line) against rainfall (bar) over time.
  * pressure.py         Charting - atmospheric pressure (line) over time.
  * rain.py             Charting - rainfall (bar) over time.
  * temperature.py      Charting - outdoor air temperature (line) over time.
  * windgust.py         Charting - wind gusts (line) over time.
  * windspeed.py        Charting - wind speed (line) over time.
  * windspeeddistro.py  Charting - wind direction distribution (radial).
  * windspeedgust.py    Charting - wind speed (bar) against wind gusts (line) over time.
  * solaruv.py	         Charting - solar radiation (bar) against UV index (line) over time.
  * storms.py	         Charting - atmospheric pressure (line), rainfall (bar) & wind gust (line) over time.

# DEPENDENCIES:

 *  pip
 *  pandas – data manipulation and analysis library.
 *  matplotlib – Plotting library.

# DEBUG

Lines 48-52 in the 'helpers/debug.py' script contain the expected column headers that should exist in the original database files. This code can be customised to suit your .csv based dataset. You will have to do this if your column headers differ from those presneted. 

If your column headers do not match those shown, you will need to update each module script accordingly to suit your requirements. 
