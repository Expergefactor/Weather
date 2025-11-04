# Weather
Weather Analytics for weather stations

Main Menu:

![menu](https://github.com/Expergefactor/Weather/blob/main/helpers/img/menu.jpg)

Sub Menu (option 4 from main menu):

![menu2](https://github.com/Expergefactor/Weather/blob/main/helpers/img/menu2.jpg)

# WHAT IS IT?
This software is designed to be used with weather station data and provides a total of 14 analytics:
 * 11 public (outdoor)
 * 3 private (indoor)

You have the option of generating a full report (from the main menu) which conducts analytics on all datasets or, conducting a single report (from the sub menu using option 4) for an individual dataset.

# WHAT DOES IT DO?
You can view examples of the analytics in the '/example' folder. Note: individual reports created from the sub-menu are identical to those contained in the full reports when using the main menu, it is just a function provided to enable an individual report to be created without generating a report for every type of metric. 

# HOW TO USE IT
 * Download the package to a local directory.
 * Run terminal, cd to the package root dir.
 * Put all weather station .csv files into folder: "database/original/"
 * run 'python3 menu.py'
 * Use option 2 to compile all weather station files into a single database
 * Now you can use functions 3 & 4
 * Keep adding more weather station files and use option 2 to ingest them into the working database
 * Option 1 from the main menu is a reminder of some of the information contained here.

# COMPONENTS:
System:
  * menu.py         Control module for all functions
  * compile.py	    Compiles database files in preparation for processing
  * utilities.py    Hosts various supporting functions
  * report_full.py  Conducts all available analytics and generates two reports (private & public).
  
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
  * solaruv.py	        Charting - solar radiation (bar) against UV index (line) over time.
  * storms.py	          Charting - atmospheric pressure (line), rainfall (bar) & wind gust (line) over time.

# DEPENDENCIES:

 *  pip
 *  pandas – data manipulation and analysis library.
 *  matplotlib – Plotting library.

# DEBUG

Lines 48-52 in the 'helpers/debug.py' script contain the expected column headers that should exist in the original database files. This code can be customised to suit your .csv based dataset. You will have to do this if your column headers differ from those presneted. 

If your column headers do not match those shown, you will need to update each module script accordingly to suit your requirements. 
