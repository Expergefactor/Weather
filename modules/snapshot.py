import chardet
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
from matplotlib.table import Table
from datetime import datetime, date
from pathlib import Path
from helpers.utilities import (copyright_text, get_station_location, contact_details)


try:
    station_location = get_station_location()
except Exception as exception:
    print(f"{exception}")
except KeyboardInterrupt as kbi:
    print(f"{kbi}")


def load_data(csv_path: str | Path = "database/compiled/ingest.csv") -> pd.DataFrame:
    csv_path = Path(csv_path)

    try:
        with csv_path.open("rb") as f:
            raw_sample = f.read(10_240)
    except FileNotFoundError:
        raise FileNotFoundError(f" ❌ File not found: {csv_path}") from None

    detection = chardet.detect(raw_sample)
    enc = detection.get("encoding")
    conf = detection.get("confidence", 0)

    if not enc:
        raise UnicodeError(" ❌ chardet could not determine an encoding for the file.")

    def _read(encoding: str, replace_errors: bool = False) -> pd.DataFrame:
        kwargs = {"encoding": encoding}
        if replace_errors:
            kwargs["errors"] = "replace"
        with csv_path.open("r", **kwargs) as fh:
            return pd.read_csv(fh, sep=";", skip_blank_lines=True, header=0, na_values=["", " "], on_bad_lines="skip",
                               engine="python")

    try:
        df = _read(enc, replace_errors=False)
        print(f" Loaded with encoding: {enc}")
        return df
    except Exception as exc:
        print(f" Detected encoding '{enc}' raised an error: {exc}")
        print(" Retrying with the same encoding using error replacement...")
        df = _read(enc, replace_errors=True)
        print(f" Loaded (with replacement) using encoding: {enc}")
        return df


def load_and_prepare(csv_path: Path = Path("database/compiled/ingest.csv")) -> pd.DataFrame:
    df = load_data(csv_path)

    # Strip whitespace from column names
    df.columns = [c.strip() for c in df.columns]

    # Parse the date column
    date_col = "Date (Europe/London)"
    if date_col not in df.columns:
        raise KeyError(f" Expected column '{date_col}' not found in CSV.")
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df.set_index(date_col, inplace=True)

    # Convert everything else to numeric (commas removed, bad values → NaN)
    for col in df.columns:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", ""), errors="coerce"
        )
    return df


# prompt user-defined date range for Snapshot
def prompt_date_range(df: pd.DataFrame) -> tuple[pd.DataFrame, date, date]:
    min_date = df.index.min().date()
    max_date = df.index.max().date()
    print(f"\n \033[1;93mData range {min_date.strftime('%d/%m/%Y')} → {max_date.strftime('%d/%m/%Y')}\n\033[0m")

    def ask_one(prompt_msg: str, default: date) -> date:
        while True:
            user_in = input(f"{prompt_msg} [{default.strftime('%d-%m-%Y')}]: ").strip()
            if not user_in:
                return default
            try:
                parsed = datetime.strptime(user_in, "%d-%m-%Y").date()
                if parsed < min_date or parsed > max_date:
                    print(
                        f" Date must be between {min_date.strftime('%d-%m-%Y')} and {max_date.strftime('%d-%m-%Y')}."
                    )
                else:
                    return parsed
            except ValueError:
                print(" Please use the format DD‑MM‑yy (e.g., 05-03-2023).")

    start = ask_one(" Enter start date. Leave blank and press 'enter' to use entire dataset.\n"
                    " |← Earliest:", min_date)
    end = ask_one("\n Enter end date. Leave blank and press 'enter' to use entire dataset.\n"
                  " →| Latest:", max_date)

    if start > end:
        print(" Start date is after end date.")
        start, end = end, start

    mask = (df.index.date >= start) & (df.index.date <= end)
    filtered = df.loc[mask]
    print(
        f"\n Used {len(filtered)} rows of data from {start.strftime('%d/%m/%Y')} → {end.strftime('%d/%m/%Y')}\n"
    )
    return filtered, start, end


# HELPERS ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
def _apply_border_colour(tbl: Table, colour: str) -> None:
    for (_row, _col), cell in tbl.get_celld().items():
        cell.set_edgecolor(colour)


def fmt_value(metric: str, val: float) -> str:
    return f"{val:.1f}"


def deg_to_cardinal_16(deg: float) -> str:
    if np.isnan(deg):
        return "–"
    dirs = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]
    idx = int((deg + 11.25) // 22.5) % 16
    return dirs[idx]


def compute_col_widths(table_data: list[list[str]]) -> list[float]:
    if not table_data:
        return []
    cols = list(zip(*table_data))
    max_lengths = [max(len(str(item)) for item in col) for col in cols]
    total = sum(max_lengths) or 1
    return [length / total for length in max_lengths]


def compute_daily_max_sum(series: pd.Series) -> float:
    if series.empty:
        return np.nan
    daily_max = series.groupby(series.index.date).max()
    return daily_max.sum()


def compute_driest_period(df: pd.DataFrame, date_fmt: str = "%d %b") -> str:
    if df.empty or "Rain (mm)" not in df.columns:
        return "–"

    daily_max = (
        df["Rain (mm)"]
        .fillna(0)
        .groupby(df.index.date)
        .max()
    )
    daily_max.index = pd.to_datetime(daily_max.index)

    dry_mask = daily_max == 0

    longest_len = 0
    longest_start = None
    longest_end = None

    cur_len = 0
    cur_start = None

    for ts, is_dry in zip(daily_max.index, dry_mask):
        if is_dry:
            if cur_len == 0:
                cur_start = ts
            cur_len += 1
        else:
            if cur_len > longest_len:
                longest_len = cur_len
                longest_start = cur_start
                longest_end = ts - pd.Timedelta(days=1)
            cur_len = 0
            cur_start = None

    if cur_len > longest_len:
        longest_len = cur_len
        longest_start = cur_start
        longest_end = daily_max.index[-1]

    if longest_len == 0 or longest_start is None:
        return "–"

    start_str = longest_start.strftime(date_fmt)
    end_str   = longest_end.strftime(date_fmt)

    return f"{start_str} – {end_str} ({longest_len} days)"


def build_ytd_summary(df: pd.DataFrame, date_fmt: str = "%d %b") -> pd.DataFrame:
    def deg_to_compass(deg: float) -> str:
        if np.isnan(deg):
            return "–"
        deg = deg % 360
        idx = int((deg + 11.25) // 22.5) % 16
        points = [
            "N", "NNE", "NE", "ENE",
            "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW",
            "W", "WNW", "NW", "NNW",
        ]
        return points[idx]

    hottest_idx = df["Temperature (°C)"].idxmax()
    hottest_day = f"{hottest_idx.strftime(date_fmt)} ({df.at[hottest_idx, 'Temperature (°C)']:.1f}°C)"
    coldest_idx = df["Temperature (°C)"].idxmin()
    coldest_day = f"{coldest_idx.strftime(date_fmt)} ({df.at[coldest_idx, 'Temperature (°C)']:.1f}°C)"
    driest_period_str = compute_driest_period(df, date_fmt=date_fmt)
    wettest_idx = df["Rain (mm)"].idxmax()
    wettest_day = f"{wettest_idx.strftime(date_fmt)} (Total: {df.at[wettest_idx, 'Rain (mm)']:.1f} mm)"
    if "Rain rate (mm/h)" in df.columns:
        downpour_idx = df["Rain rate (mm/h)"].idxmax()
        biggest_downpour = f"{downpour_idx.strftime(date_fmt)} ({df.at[downpour_idx, 'Rain rate (mm/h)']:.1f} mm/hour)"
    else:
        biggest_downpour = "–"
    total_rain = compute_daily_max_sum(df["Rain (mm)"])
    total_rain_str = f"{total_rain:.1f} mm" if not np.isnan(total_rain) else "–"
    avg_deg = df["Average wind direction (°)"].mean()
    avg_wind_label = f"{deg_to_compass(avg_deg)} ({int(round(avg_deg))}°)"

    if "Gust of wind (mph)" in df.columns:
        gust_idx = df["Gust of wind (mph)"].idxmax()
        windiest_day = f"{gust_idx.strftime(date_fmt)} ({df.at[gust_idx, 'Gust of wind (mph)']:.1f} mph)"
    else:
        windiest_day = "–"

    rows = [
        ("Hottest Day", hottest_day),
        ("Coldest Day", coldest_day),
        ("Driest Period", driest_period_str),
        ("Wettest Day", wettest_day),
        ("Total Rainfall", total_rain_str),
        ("Biggest Downpour", biggest_downpour),
        ("Windiest Day", windiest_day),
        ("Average wind direction", avg_wind_label),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value"])


def build_auxiliary_summary(df: pd.DataFrame) -> pd.DataFrame:
    def deg_to_compass(deg: float) -> str:
        if np.isnan(deg):
            return "–"
        deg = deg % 360
        idx = int((deg + 11.25) // 22.5) % 16
        points = [
            "N", "NNE", "NE", "ENE",
            "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW",
            "W", "WNW", "NW", "NNW",
        ]
        return points[idx]

    hottest_idx = df["Temperature (°C)"].idxmax()
    hottest_day = f"{hottest_idx.strftime('%d %b')} ({df.at[hottest_idx, 'Temperature (°C)']:.1f}°C)"
    coldest_idx = df["Temperature (°C)"].idxmin()
    coldest_day = f"{coldest_idx.strftime('%d %b')} ({df.at[coldest_idx, 'Temperature (°C)']:.1f}°C)"
    driest_period_str = compute_driest_period(df)
    wettest_idx = df["Rain (mm)"].idxmax()
    wettest_day = f"{wettest_idx.strftime('%d %b')} (Total: {df.at[wettest_idx, 'Rain (mm)']:.1f} mm)"
    total_rain = compute_daily_max_sum(df["Rain (mm)"])
    total_rain_str = f"{total_rain:.1f} mm" if not np.isnan(total_rain) else "–"
    avg_deg = df["Average wind direction (°)"].mean()
    avg_wind_label = f"{deg_to_compass(avg_deg)} ({int(round(avg_deg))}°)"

    if "Gust of wind (mph)" in df.columns:
        gust_idx = df["Gust of wind (mph)"].idxmax()
        windiest_day = f"{gust_idx.strftime('%d %b')} ({df.at[gust_idx, 'Gust of wind (mph)']:.1f} mph)"
    else:
        windiest_day = "–"

    if "Rain rate (mm/h)" in df.columns:
        downpour_idx = df["Rain rate (mm/h)"].idxmax()
        biggest_downpour = f"{downpour_idx.strftime('%d %b')} ({df.at[downpour_idx, 'Rain rate (mm/h)']:.1f} mm/hour)"
    else:
        biggest_downpour = "–"

    rows = [
        ("Hottest Day", hottest_day),
        ("Coldest Day", coldest_day),
        ("Driest Period", driest_period_str),
        ("Wettest Day", wettest_day),
        ("Total Rainfall", total_rain_str),
        ("Biggest Downpour", biggest_downpour),
        ("Windiest Day", windiest_day),
        ("Average wind direction", avg_wind_label),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value"])
# helpers end ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑


# generate pdf
def save_as_pdf(main_tbl: pd.DataFrame, aux_tbl: pd.DataFrame, out_path: Path, start: date, end: date,
                raw_df: pd.DataFrame, full_df: pd.DataFrame = None,):

    aux_tbl = aux_tbl.set_index("Metric")
    main_tbl = main_tbl.set_index("Metric")
    full_df = full_df.set_index("Metric")
    merged = aux_tbl.join(main_tbl, lsuffix="_period", rsuffix="_ytd", how="outer")
    merged = merged.join(full_df, rsuffix="_full", how="outer")
    metric_order = [
        "Hottest Day",
        "Driest Period",
        "Coldest Day",
        "Wettest Day",
        "Biggest Downpour",
        "Total Rainfall",
        "Windiest Day",
        "Average wind direction",
    ]
    merged = merged.reindex(metric_order)
    merged = merged.rename(columns={"Value_period": "User‑defined period",
                                    "Value_ytd": "Year‑to‑Date",
                                    "Value_full": "Since May 2024",
                                    })
    merged.reset_index(inplace=True)

    # table appearance
    font_size = 9
    header_bg = "#ffffff"
    header_fg = "#000000"
    alt_row_color = "#FFFFCC" # Yellow alternating rows
    outer_edge = "#00FF00" # Green = date‑defined column
    ytd_edge   = "#0000FF" # Blue – YTD column
    full_edge  = "#FF0000" # Red – Since records began

    fig = plt.figure(figsize=(11.69, 8.27))
    gs = GridSpec(2, 1, height_ratios=[0.85, 0.15], hspace=0.05, wspace=0.05,)

    ax_table = fig.add_subplot(gs[0, 0])
    ax_table.axis("off")

    table_header = ["", f"{start.strftime('%d %b %Y')} – {end.strftime('%d %b %Y')}", "Year‑to‑Date", "Since May 2024"]
    table_rows = merged.values.tolist()
    table_data = [table_header] + table_rows

    col_widths = compute_col_widths(table_data)

    tbl = ax_table.table(cellText=table_data, loc="center", cellLoc="center", colWidths=col_widths)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(font_size)
    tbl.scale(1, 1.5)

    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(outer_edge)

        if r == 0:
            cell.set_text_props(weight="bold", color=header_fg)
            cell.set_facecolor(header_bg)

        elif c == 0:
            cell.set_text_props(weight="bold")

        else:
            if r % 2:
                cell.set_facecolor(alt_row_color)


        if c == 1:
            cell.set_edgecolor(outer_edge)
        elif c == 2:
            cell.set_edgecolor(ytd_edge)
        elif c == 3:
            cell.set_edgecolor(full_edge)

    # footer
    logo = mpimg.imread("helpers/img/logo.jpg")
    logo_ax = fig.add_axes([0.47, 0.34, 0.07, 0.07])  # horizontal, vertical, size width, size height
    logo_ax.imshow(logo, interpolation="antialiased")
    logo_ax.axis("off")

    ax_footer = fig.add_subplot(gs[1, 0])
    ax_footer.axis("off")
    ax_footer.text(
        0.5, # Horizontal
        1.9, # Vertical
        copyright_text(),
        ha="center",
        va="center",
        fontsize=6,
    )
    ax_footer.text(
        0.5, # Horizontal
        1.7, # Vertical
        contact_details(),
        ha="center",
        va="center",
        fontsize=6,
        color="black",
    )

    # title
    header_str = (
        f"{station_location} Weather Snapshot\n"
        f"{start.strftime('%d %b %Y')} – {end.strftime('%d %b %Y')}"
    )
    fig.text(
        0.5, # Horizontal
        0.78, # Vertical
        header_str,
        ha="center",
        va="top",
        fontsize=16,
        weight="bold",
        color="#000000",
    )

    with PdfPages(out_path) as pdf:
        pdf.savefig(fig, dpi=300)
        plt.close(fig)
    print(f" \033[1;92mPDF saved to {out_path}\n\033[0m")


if __name__ == "__main__":
    df_weather = load_and_prepare(Path("database/compiled/ingest.csv"))

    df_filtered, start_date, end_date = prompt_date_range(df_weather)

    today = pd.Timestamp(datetime.now().date())
    latest_in_dataset = df_weather.index.max()
    ytd_end = min(today, latest_in_dataset)
    ytd_start = pd.Timestamp(year=ytd_end.year, month=1, day=1)
    df_ytd = df_weather.loc[ytd_start:ytd_end]

    main_table = build_ytd_summary(df_ytd)
    aux_table  = build_auxiliary_summary(df_filtered)
    full_summary_table = build_ytd_summary(df_weather, date_fmt="%d %b %y")

    out_dir = Path('analytics')
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = out_dir / f"{station_location}_snapshot.pdf"

    save_as_pdf(
        main_tbl=main_table,
        aux_tbl=aux_table,
        out_path=str(pdf_path),
        start=start_date,
        end=end_date,
        raw_df=df_filtered,
        full_df=full_summary_table,
    )

