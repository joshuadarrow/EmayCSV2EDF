import pyedflib

edf_file = "EMAY_SpO2_20260215_025349.edf"

# Open EDF
f = pyedflib.EdfReader(edf_file)

print("Number of signals (channels):", f.signals_in_file)
print("Signal labels:", f.getSignalLabels())
print("Start datetime:", f.getStartdatetime())
print("File duration (seconds):", f.getFileDuration())
print("Samples per channel:", [f.getNSamples()[i] for i in range(f.signals_in_file)])

# Check min/max for each channel
for i in range(f.signals_in_file):
    print(f"Channel {i} ({f.getLabel(i)}):")
    print("  Physical min/max:", f.getPhysicalMinimum(i), f.getPhysicalMaximum(i))
    print("  Digital min/max:", f.getDigitalMinimum(i), f.getDigitalMaximum(i))

# If you want, read raw data of first channel
signal0 = f.readSignal(0)
print("First 10 samples of channel 0:", signal0[:10])

f.close()
