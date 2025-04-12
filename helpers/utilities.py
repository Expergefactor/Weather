import pandas as pd
import os
import glob
import os
import chardet
import matplotlib.dates as mdates


def view_database_dates():
    try:
        data = load_data()
        date_col = 'Date (Europe/London)'
        data[date_col] = pd.to_datetime(data[date_col].astype(str).str.strip(),
                                        format='%Y-%m-%d %H:%M:%S', errors='coerce')
        min_date, max_date = data[date_col].min(), data[date_col].max()
        print(f"\033[1;97m Existing database: {min_date.strftime('%B %Y')} - {max_date.strftime('%B %Y')}\033[0m")

    except Exception as e:
        print(f"\n\033[1;91m Error reading database: {e}\033[0m\n")
    input("  Press 'enter' to continue...")


def merge_csv_files():
    try:
        input_folder = 'database/original/' # mapped from the root folder (menu.py)
        output_file: str = "database/compiled/ingest.csv" # mapped from the root folder (menu.py)

        csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

        if not csv_files:
            print("\n No CSV files found in the folder.")
            return

        with open(output_file, 'w', encoding='utf-16le', newline='') as outfile:
            header_written = False

            for file in csv_files:
                with open(file, 'r', encoding='utf-16le') as infile:
                    header = infile.readline()

                    if not header_written:
                        outfile.write(header)  # Write header from the first file
                        header_written = True

                    for line in infile:
                        outfile.write(line)  # Append data

        file_size = os.path.getsize(output_file) / (1024 * 1024)  # Convert bytes to MB

        print(f"\n\033[1;92m Compiled {len(csv_files)} files.\033[0m")
        print(f"\033[1;97m Working copy for analytics: {output_file} (Size: {file_size:.2f} MB)\033[0m")

        try:
            file_path = 'database/compiled/ingest.csv'
            with open(file_path, 'rb') as f:
                detected_encoding = chardet.detect(f.read(5000))['encoding']
            data = pd.read_csv(
                file_path, sep=';', encoding=detected_encoding, skip_blank_lines=True,
                header=0, na_values=['', ' '], on_bad_lines='skip', engine='python'
            )
            date_col = 'Date (Europe/London)'
            data[date_col] = pd.to_datetime(data[date_col].astype(str).str.strip(),
                                            format='%Y-%m-%d %H:%M:%S', errors='coerce')
            min_date, max_date = data[date_col].min(), data[date_col].max()
            print(f"\033[1;97m New database: {min_date.strftime('%B %Y')} - {max_date.strftime('%B %Y')}\033[0m")
        except Exception as e:
            print(f"\n\033[1;91m Error reading database: {e}\033[0m\n")

        input(" Press 'enter' to continue...")

    except KeyboardInterrupt as kbi:
        print(f"{kbi}")

    except Exception as e:
        print(f' Error: {e}')


def get_station_location():
    try:
        location = input("\n Location entered will be used in the title of all charts.\n"
                     " Enter location of the weather station: ")

        return location

    except Exception as e:
        print(f"{e}")

    except KeyboardInterrupt as kbi:
        print(f"{kbi}")


def get_user_date_range(data):
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

        except KeyboardInterrupt as kbi:
            print(f"{kbi}")


def load_data():
    while True:
        try:
            with open('database/compiled/ingest.csv', 'rb') as f:
                raw_data = f.read(5000)  # Read the first 5000 bytes
                result = chardet.detect(raw_data)  # Detect encoding
                detected_encoding = result['encoding']

                loaded_data = pd.read_csv('database/compiled/ingest.csv', sep=';', encoding=detected_encoding,
                                   skip_blank_lines=True, header=0, na_values=['', ' '], on_bad_lines='skip',
                                   engine='python')
                return loaded_data

        except Exception as e:
            print(f"\n\033[1;91m Error: {e}\033[0m\n")
            raise SystemExit(f"Error: {e}")


def copyright_text():
    return ('Data & design © 2025 Expergefactor\nGot an idea on how this project can be improved?'
            ' Feedback is welcome at:')


def contact_details():
    return 'the.expergefactor@protonmail.com'
