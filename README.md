# EmayCSV2EDF
Convert CSV output from Emay and similar recording pulse oximeters to EDF+ format for data compression, viewing, and further analysis.


# Example Usage

python3 csv2edf.py EMAY_data.csv


# Expected csv format

            Date         Time  SpO2(%)  PR(bpm)
0      2/15/2026   2:53:49 AM     91.0     77.0
1      2/15/2026   2:53:50 AM     91.0     77.0
2      2/15/2026   2:53:51 AM     91.0     77.0
3      2/15/2026   2:53:52 AM     91.0     77.0
4      2/15/2026   2:53:53 AM     91.0     77.0
