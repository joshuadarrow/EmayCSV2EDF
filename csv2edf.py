#!/usr/bin/env python3

import pandas as pd
import numpy as np
import pyedflib
import re
from datetime import datetime

# ---------------------------
# USER OPTIONS
# ---------------------------
INPUT_CSV = "/home/joshua/Documents/Medical/Data/SpO2/JoshuaDarrow/2026/csv/EMAY_SpO2_20260215_025349.csv"
OUTPUT_EDF = "output.edf"
AUTO_SAMPLE_RATE = True   # If False, use MANUAL_SAMPLE_RATE
MANUAL_SAMPLE_RATE = 1
NAN = -999
# ---------------------------


def extract_unit(column_name):
    """Extract unit from header like 'SpO2(%)' -> '%' """
    match = re.search(r"\((.*?)\)", column_name)
    return match.group(1) if match else ""


def clean_label(column_name):
    """Remove unit part from label"""
    return re.sub(r"\(.*?\)", "", column_name).strip()

def convert_times(df):
    '''convert Date + time columns to datetime object timestamps'''
    df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
    df.drop(['Date', 'Time'], axis=1, inplace=True)

def calc_sample_rate(df):
    '''get the sample rate from the elapsed time between first two data points'''
    dt = df["datetime"].iloc[1] - df["datetime"].iloc[0] 
    return 1 / dt.total_seconds()

def fill_nans(df, nan=0):
    '''add rows of Nans for missing values to maintain constant sample rate'''
    df["dt"] = (df["datetime"].shift(-1) - df["datetime"])- pd.Timedelta(seconds=1)

    # create dataframe of Nan values to fill in missing observations
    nans = pd.DataFrame(columns=df.columns.difference(["dt"])) 

    for index, row in df.iloc[:-1].iterrows():
        for i in range(1, int(row["dt"].total_seconds()+1)):
            new_row = {col: nan for col in nans.columns}
            new_row["datetime"] = row["datetime"] + pd.Timedelta(seconds=i)
            nans.loc[len(nans)] = new_row

    df.drop(["dt"], axis=1, inplace=True)
    print(len(nans), "Nan observations created to maintain constant sample rate.")

    # concatenate two datasets and sort to maintain proper ordering
    df = pd.concat([df, nans])
    df = df.sort_values(by="datetime")
    print(df)
    
    return 0


# 1️⃣ Load CSV
df = pd.read_csv(INPUT_CSV)

convert_times(df)
sample_rate = calc_sample_rate(df)
fill_nans(df)
print(df)
print(sample_rate)
exit(0)





# Calculate sample rate
# Fill in missing or Nan values with -999
# extract SpO2 and PR columns
# write to edf+ format




# 4️⃣ Replace NaNs with 0
df = df.fill_null(0)

# 5️⃣ Convert signal data
data_np = df.to_numpy().T
n_channels, n_samples = data_np.shape

# 6️⃣ Build channel headers dynamically
channel_info = []

for i, col in enumerate(df.columns):
    signal = data_np[i]
    unit = extract_unit(col)
    label = clean_label(col)

    channel_info.append({
        "label": label,
        "dimension": unit,
        "sample_rate": sample_rate,
        "physical_min": float(signal.min()),
        "physical_max": float(signal.max()),
        "digital_min": -32768,
        "digital_max": 32767,
        "transducer": "",
        "prefilter": ""
    })


# 7️⃣ Write EDF+
writer = pyedflib.EdfWriter(
    OUTPUT_EDF,
    n_channels=n_channels,
    file_type=pyedflib.FILETYPE_EDFPLUS
)

writer.setSignalHeaders(channel_info)
writer.writeSamples(data_np)
writer.close()

print("Done.")
print(f"Detected sample rate: {sample_rate} Hz")
print("NaNs automatically replaced with 0.")
