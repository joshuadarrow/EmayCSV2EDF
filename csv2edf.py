#!/usr/bin/env python3

# todo:
# 1) Enable more file types (EDF, EDF+, BDF, BDF+)
# 2) Add cmdline argument capabilities (new filename)
# 3) More flexible timestamp column options + make this available via cmdline

import pandas as pd
import numpy as np
import pyedflib
import re
import sys
import os
from datetime import datetime

def extract_unit(column_name):
    match = re.search(r"\((.*?)\)", column_name)
    return match.group(1) if match else ""

def clean_label(column_name):
    return re.sub(r"\(.*?\)", "", column_name).strip()

def process_csv(input_path):
    # 1. Load Data
    df = pd.read_csv(input_path)
    
    # 2. Handle Time/Date
    # Convert to a single datetime index
    df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df = df.sort_values(by="datetime").drop_duplicates(subset="datetime")
    start_time = df["datetime"].iloc[0]

    # 3. Calculate Sample Rate & Resample
    # Instead of a manual loop, we use resample() which is much faster.
    # It automatically inserts NaNs for missing seconds.
    df = df.set_index("datetime")
    # Drop original Date/Time strings so they don't break the numeric resampling
    df = df.drop(columns=["Date", "Time"], errors='ignore')
    
    # Resample to 1-second intervals (adjust '1S' if your rate is different)
    df = df.resample('1s').asfreq()
    
    # Fill NaNs with your designated placeholder
    df = df.fillna(0) 
#    print(df)
#    df.to_csv(os.path.splitext(input_path)[0] + "_v2.csv")

    sample_rate = 1.0 # Standard for most EMAY CSVs (1 sample per second)
    
    # 4. Write EDF+
    output_edf = os.path.splitext(input_path)[0] + ".edf"
    n_channels = len(df.columns)
    
    print(output_edf)
    print(n_channels)
    
    writer = pyedflib.EdfWriter(
        output_edf, 
        n_channels=n_channels, 
        file_type=pyedflib.FILETYPE_EDF#PLUS
    )
    
#    writer.setDatarecordDuration(60) # 10 seconds per record block
    
    channel_info = []
    signals = []

    for col in df.columns:
        signal_data = df[col].values
        unit = extract_unit(col)
        label = clean_label(col)

        channel_info.append({
            "label": label[:16], # EDF labels are limited to 16 chars
            "dimension": unit,
            "sample_frequency": sample_rate,
            "physical_min": float(np.min(signal_data)),
            "physical_max": float(np.max(signal_data)) if np.max(signal_data) > np.min(signal_data) else float(np.min(signal_data) + 1),
            "digital_min": -32768,
            "digital_max": 32767,
            "transducer": "EMAY Device",
            "prefilter": ""
        })
        signals.append(signal_data)

    writer.setSignalHeaders(channel_info)
    writer.setStartdatetime(start_time)
    writer.writeSamples(signals)
    writer.close()

    print(f"Successfully converted {input_path} to {output_edf}")
    print(f"Start Time: {start_time} | Samples: {len(df)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./script.py <filename.csv>")
    else:
        process_csv(sys.argv[1])
