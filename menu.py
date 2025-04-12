import subprocess
import os
from helpers.utilities import view_database_dates, merge_csv_files


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def banner():
    print(
        """\033[1;93m
            ╦ ╦┌─┐┌─┐┌┬┐┬ ┬┌─┐┬─┐  ╔═╗┌┐┌┌─┐┬ ┬ ┬┌┬┐┬┌─┐┌─┐
            ║║║├┤ ├─┤ │ ├─┤├┤ ├┬┘  ╠═╣│││├─┤│ └┬┘ │ ││  └─┐
            ╚╩╝└─┘┴ ┴ ┴ ┴ ┴└─┘┴└─  ╩ ╩┘└┘┴ ┴┴─┘┴  ┴ ┴└─┘└─┘\033[0m
                          by \033[1;92mExpergefactor\033[1;93m"""
    )


def about():
    clear_console()
    print("""\n\033[1;97m
    Weather Analytics by \033[1;92mExpergefactor...
    \033[1;93m
    WHAT IS IT?\033[0m
    This software is designed to be used with weather station data and provides a total
    of 14 analytics, 3 private (indoor) & 11 public (outdoor). You have the option of
    generating a full report which conducts analytics on all datasets or, conducting a
    single report for an individual dataset. 
    \033[1;93m
    HOW TO USE IT\033[0m
    * Put all original weather station files into folder: "database/original/"
    * Use option 2 to compile all weather station files into a single database
    * Now you can use functions 3 & 4
    * Keep adding more weather station files and use option 2 to ingest them into the
      working database
    \033[1;93m
    COMPONENTS:\033[0m
    System:
    menu.py         Control module for all functions
    compile.py	    Compiles database files in preparation for processing
    utilities.py    Hosts various supporting functions
    report_full.py  Conducts all available analytics and generates two reports 
                    (private & public).
    
    Private Analytics:
    indoor_temp.py      Charting - indoor air temperature (line) over time.
    indoor_humidity.py 	Charting - indoor humidity (line) over time.
    indoor_humidtemp.py Charting - indoor air temperature (bar) against humidity (line)
                                   over time.
    
    Public Analytics:
    humidity.py         Charting - humidity (line) over time.
    humidityrain.py     Charting - humidity (line) against rainfall (bar) over time.
    pressure.py         Charting - atmospheric pressure (line) over time.
    rain.py             Charting - rainfall (bar) over time.
    temperature.py      Charting - outdoor air temperature (line) over time.
    windgust.py         Charting - wind gusts (line) over time.
    windspeed.py        Charting - wind speed (line) over time.
    windspeeddistro.py  Charting - wind direction distribution (radial).
    windspeedgust.py    Charting - wind speed (bar) against wind gusts (line) over time.
    solaruv.py	        Charting - solar radiation (bar) against UV index (line) over time.
    storms.py	        Charting - atmospheric pressure (line), rainfall (bar) & 
                                   wind gust (line) over time.
    \033[1;93m
    REQUIREMENTS:\033[0m
    This software is designed for a specific weather station which includes the
    following data: Date, Inside temperature, Temperature, Inside humidity,
    Humidity, Gust of wind, Average wind speed, Average wind direction,
    Atmospheric pressure, Rain, Solar radiation & UV index.
    \033[1;97m
    It is possible to adapt this software for use with other weather stations
    or datasets, in which case please adhere to the following licence conditions...
    \033[1;93m
    *******************************************************************************
                                    LICENCE
            Weather Analytics by Expergefactor Copyright (c) 2025

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    *******************************************************************************
    \033[0m
    """)
    input(" Press 'enter' to continue...")
    main()


def menu():
    try:
        choice = input(
            "       \n\033[1;97m Select a feature...\n\n\033[0m"
            "       \033[1;93m1\033[1;97m View the existing database limits\n"
            "       \033[1;93m2\033[1;97m Compile a new database\n"
            "       \033[1;93m3\033[1;97m Generate full report\n"
            "       \033[1;93m4\033[1;97m Generate a single report\n\n"
            " Help & Information\n"
            "       \033[1;93mi\033[1;97m Display the info/help\n\n"
            " Navigation Options\n"
            "       \033[1;93me\033[1;97m Exit\n\n\033[0m"
            " \033[1;93mInput a value and press 'enter': \033[0m"
        )
        while True:
            if choice == "i":
                about()
            if choice == "1":
                try:
                    view_database_dates()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "2":
                try:
                    merge_csv_files()
                    clear_console()
                    main()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "3":
                try:
                    command = f"python3 -m modules.report_full"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "4":
                try:
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "e":
                print("\n\033[1;92m Exiting...\033[0m\n")
                raise SystemExit()
            else:
                main()

    except KeyboardInterrupt:
        print("\n\033[1;92m You stopped the operation, exiting...\033[0m\n")
        exit(0)

    except Exception as e:
        print(f' Error: {e}')


def single_report_menu():
    clear_console()
    banner()
    try:
        choice = input(
            "       \n\033[1;97m Select a feature...\n\n"
            " Single Public Analytics\n"
            "       \033[1;93m 1\033[1;97m Humidity\n"
            "       \033[1;93m 2\033[1;97m Air Pressure\n"
            "       \033[1;93m 3\033[1;97m Rainfall\n"
            "       \033[1;93m 4\033[1;97m Temperature\n"            
            "       \033[1;93m 5\033[1;97m Wind Gust\n"
            "       \033[1;93m 6\033[1;97m Wind Speed\n"
            "       \033[1;93m 7\033[1;97m Wind Distribution\n\n"
            " Hybrid Public Analytics\n"
            "       \033[1;93m 8\033[1;97m Wind Speed & Wind Gust\n"
            "       \033[1;93m 9\033[1;97m Humidity & Rain\n"
            "       \033[1;93m10\033[1;97m Solar Radiation & UV Index\n"
            "       \033[1;93m11\033[1;97m Storms\n\n"
            " Single Private Analytics\n"
            "       \033[1;93m12\033[1;97m Indoor Temperature\n"
            "       \033[1;93m13\033[1;97m Indoor Humidity\n\n"
            " Hybrid Private Analytics\n"
            "       \033[1;93m14\033[1;97m Indoor Temperature & Humidity\n\n"
            " Navigation Options\n"
            "       \033[1;93mr\033[1;97m Return to the main menu\n\033[0m"
            "       \033[1;93me\033[1;97m Exit\n\n"
            " \033[1;93mInput a value and press 'enter': \033[0m"
        )
        while True:
            if choice == "1":
                try:
                    command = f"python3 -m modules.humidity"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "2":
                try:
                    command = f"python3 -m modules.pressure"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "3":
                try:
                    command = f"python3 -m modules.rain"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "4":
                try:
                    command = f"python3 -m modules.temperature"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                        print(f' Error: {e}')
            if choice == "5":
                try:
                    command = f"python3 -m modules.windgust"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "6":
                try:
                    command = f"python3 -m modules.windspeed"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "7":
                try:
                    command = f"python3 -m modules.winddistribution"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "8":
                try:
                    command = f"python3 -m modules.windspeedgust"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "9":
                try:
                    command = f"python3 -m modules.humidityrain"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "10":
                try:
                    command = f"python3 -m modules.solaruv"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "11":
                try:
                    command = f"python3 -m modules.storms"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "12":
                try:
                    command = f"python3 -m modules.indoor_temp"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "13":
                try:
                    command = f"python3 -m modules.indoor_humidity"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "14":
                try:
                    command = f"python3 -m modules.indoor_humidtemp"
                    clear_console()
                    subprocess.run(command, shell=True)
                    input(" Press 'enter' to continue...")
                    clear_console()
                    banner()
                    single_report_menu()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "15":
                try:
                    main()
                except Exception as e:
                    print(f' Error: {e}')
            if choice == "r":
                main()
            if choice == "e":
                print("\n\033[1;92m Exiting...\033[0m\n")
                raise SystemExit()
            else:
                input("Invalid option, press 'enter' and try again...")
                single_report_menu()


    except KeyboardInterrupt:
        print("\n\033[1;92m You stopped the operation, exiting...\033[0m\n")
        exit(0)

    except Exception as e:
        print(f' Error: {e}')


def main():
    clear_console()
    banner()
    menu()

main()
