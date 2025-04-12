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
You can view examples of the analytics in the '/examples' folder. Note: individual reports created from the sub-menu are identical to those contained in the full reports when using the main menu, it is just a function provided to enable an individual report to be created without generating a report for every type of metric. 

# HOW TO USE IT
 * Download the package to a local directory.
 * Run terminal, cd to the package root dir.
 * Put all weather station .csv files into folder: "database/original/"
 * run 'python3 menu.py'
 * Use option 2 to compile all weather station files into a single database
 * Now you can use functions 3 & 4
 * Keep adding more weather station files and use option 2 to ingest them into the working database
 * Option 1 from the main menu is a reminder of some of the information contained here.

# DEBUG

Lines 48-52 in the 'helpers/debug.py' script contain the expected column headers that should exist in the original database files. This code can be customised to suit your .csv based dataset. You will have to do this if your column headers differ from those presneted. 

If your column headers do not match those presented, you will need to update each module script accordingly to suit your requirements. 
