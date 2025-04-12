import os
import chardet
import pandas as pd
import matplotlib.dates as mdates


# This script is unused but can be utilised to help debug data processing
# should the input format change at some time in the future
# The script will display the data types prior and post processing

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
clear_console()

try:
    # Detect file encoding
    with open('../database/ingest/ingest.csv', 'rb') as f:
        raw_data = f.read(5000)  # Read the first 5000 bytes
        result = chardet.detect(raw_data)  # Detect encoding
        detected_encoding = result['encoding']
        print(f"\nDetected file encoding: {detected_encoding}\n")
except Exception as e:
    print(f"\n\033[1;91m Error reading CSV file: {e}\033[0m\n")
    exit()

# Load CSV with detected encoding without predefined headers
try:
    data = pd.read_csv(
        '../database/ingest/ingest.csv',
        sep=';',  # Use semicolon as delimiter
        encoding=detected_encoding,  # Use detected encoding
        skip_blank_lines=True,  # Ignore blank lines
        header=0,  # Use the first row as column names
        na_values=['', ' '],  # Treat empty cells as NaN
        on_bad_lines='skip',  # Skip problematic lines
        engine='python'  # Handles inconsistent row lengths
    )
except Exception as e:
    print(f"\n\033[1;91m Error: {e}\033[0m\n")
    exit()

# Print first few rows to verify structure
print("Raw Data:")
print("Sample:", data.head(3))

# Generate default column names if necessary
expected_columns = [
    "Date (Europe/London)", "Inside temperature (°C)", "Temperature (°C)", "Wind chill (°C)",
    "Inside dew point (°C)", "Dew point (°C)", "Inside heat index (°C)", "Heat index (°C)",
    "Inside humidity (%)", "Humidity (%)", "Gust of wind (mph)", "Average wind speed (mph)",
    "Average wind direction (°)", "Atmospheric pressure (mbar)", "Rain (mm)",
    "Evapotranspiration (mm)", "Rain rate (mm/h)", "Solar radiation (W/m²)", "UV index"
]
    # If there's an extra column, add a placeholder name
while len(expected_columns) < len(data.columns):
    expected_columns.append(f"Extra Column {len(expected_columns) - 19}")
    # Assign column names dynamically
data.columns = expected_columns[:len(data.columns)]
    # The following can be used to force printing the assigned column names:
    # print(f"\nAssigned column names:\n{list(data.columns)}")

# Select columns for processing
data = data[['Date (Europe/London)', 'Example metric 1', 'Example metric 2']]

# Print raw data types
print("\nRaw data types:")
print(data.dtypes)

# Convert dates from objects to datetime format
    # Ensure date column is read as string before conversion
print("\nConverting dates to datetime format...")
data['Date (Europe/London)'] = data['Date (Europe/London)'].astype(str).str.strip()
    # Explicitly convert the column to datetime format
data['Date (Europe/London)'] = pd.to_datetime(data['Date (Europe/London)'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    # Check that the formatting has been changed
print("Complete (sample):")
print(data['Date (Europe/London)'].head(3))

# Ensure dataset is sorted by date
data = data.sort_values(by='Date (Europe/London)')

# Convert 'Example metric 1' column, strip spaces, remove commas, and convert to numeric
print("\nConverting Example metric 1 data format...")
data['Example metric 1'] = (
    data['Example metric 1']
    .astype(str)  # Ensure it's a string
    .str.replace(',', '', regex=True)  # Remove commas
)
data['Example metric 1'] = pd.to_numeric(data['Example metric 1'], errors='coerce')
print("Complete (sample):")
print(data['Example metric 1'].head(3))

# Convert the 'Average wind speed (mph)' column to numeric, coercing errors to NaN
print("\nConverting Example metric 2 data format...")
data['Example metric 2'] = pd.to_numeric(data['Example metric 2'], errors='coerce')
print("Complete (sample):")
print(data['Example metric 2'].head(3))

# Confirm converted data types
print("\nConverted data types:")
print(data.dtypes)

# Print data ranges
print("\n    Date range found:")
print(f"    Start: {data['Date (Europe/London)'].min()}")
print(f"    End: {data['Date (Europe/London)'].max()}")
print("\n    Example metric 1 range found:")
y_min = (data['Example metric 1'].min())
y_max = (data['Example metric 1'].max())
print(f"    {y_min} - {y_max} unit")
print("\n    Example metric 2 range found:")
y_min = (data['Example metric 2'].min())
y_max = (data['Example metric 2'].max())
print(f"    {y_min} - {y_max} unit")

input(" Press 'enter' to continue...")

