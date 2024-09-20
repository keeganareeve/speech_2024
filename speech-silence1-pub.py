import contextlib
import wave
import sys
import numpy as np
import maad
from maad import sound
import contextlib


'''

0.
Filename without specified directories is received as the argument for this script.
Script should be run as so: `speech-silenceX.py filename` where X = script version number.

Output is a TextGrid with two tiers: Tier 1 for time interval and Tier 2 for text.
However, both tiers are empty as the output before one manually edits them in PRAAT.

'''
filename = sys.argv[1]
if len(sys.argv) > 2:
    printBool = sys.argv[2]  # whether script will print output
else:
    printBool = None

# Positive values for printBool variable
pos_vals = ["t", "true", "True", None, "1",
            "print", "Print", "Output", "output"]
neg_vals = ["f", "false" "False", "0", "None", "none", "null"]

'''
1.
Loading in sound file and 'plotting' according to power.

tn=time vector (horizontal x-axis)
fn=Frequency vector (vertical y-axis)
ex=The location, in data-coordinates, of the lower-left and upper-right corners. (min, max)
'''
filepath = f'../{filename}'
s, fs = sound.load(filepath)
N = 4096  # 4096 or above keeps 'energy' as significant factor
Sxx_power, tn, fn, ex = maad.sound.spectrogram(
    s, fs, nperseg=N, noverlap=N//2, mode='psd')


'''
3.

If it's the first change, it won't meet the condition if it's just silence, but if it's 
speech, then it will start appending the rows and columns: the first | is thus always the first point at which speech is detected.

'''

freq_min = 0
freq_max = 500

freq_indices = np.where((fn >= freq_min) & (fn <= freq_max))[0]
Sxx_power_low_freq = Sxx_power[freq_indices, :]

# Define threshold for low power (can be adjusted as needed)
# Example: 1st percentile as threshold
threshold = np.percentile(Sxx_power_low_freq, 1)
row_indices = []
col_indices = []
# Assume non-speech is first
speechBool = False
# Loop through each element in the 2D array
for row in range(Sxx_power_low_freq.shape[0]):
    for col in range(Sxx_power_low_freq.shape[1]):
        # Check if the element is less than the threshold
        if Sxx_power_low_freq[row, col] < threshold and speechBool == True:
            # Append the row and column indices if the condition is met
            row_indices.append(row)
            col_indices.append(col)
            speechBool = False
        elif Sxx_power_low_freq[row, col] >= threshold and speechBool == False:
            row_indices.append(row)
            col_indices.append(col)
            speechBool = True
        else:
            pass

# Convert the lists of indices to numpy arrays
row_indices = np.array(row_indices)
col_indices = np.array(col_indices)

low_power_indices = (row_indices, col_indices)

low_power_timestamps = tn[low_power_indices[1]]

low_power_timestamps = np.unique(low_power_timestamps)

'''
4.

Defines function 'filter_intervals()' so that it finds only when speech and silence change over a longer difference, time-wise.

'''


def filter_intervals(boundaries, min_interval=0.3):
    """
    Filter out intervals shorter than min_interval from the boundaries.

    Parameters:
    - boundaries: 1D numpy array of boundaries.
    - min_interval: Minimum interval length to keep. (in seconds)

    Returns:
    - A 1D numpy array of filtered boundaries.
    """
    # Ensure boundaries is a numpy array
    boundaries = np.array(boundaries)

    # Compute intervals between consecutive boundaries
    intervals = np.diff(boundaries)

    # Identify the intervals to keep
    valid_intervals = intervals >= min_interval

    # To keep intervals, we need to keep the boundaries at the start and end of each valid interval
    # Start by including the first boundary
    filtered_boundaries = [boundaries[0]]

    # Iterate through intervals and add boundaries that mark valid intervals
    for i in range(len(valid_intervals)):
        if valid_intervals[i]:
            filtered_boundaries.append(boundaries[i + 1])

    # Convert to numpy array
    filtered_boundaries = np.array(filtered_boundaries)

    return filtered_boundaries


filtered_boundaries = filter_intervals(low_power_timestamps, 0.5)
print("Filtered boundaries:", filtered_boundaries)

'''

5.
Now, we'll make these intervals into a PRAAT TextGrid.
For this, we need:
1. The duration of the wav file itself.
2. A list containing the bounds of each time interval.
3. The right TextGrid format (two-tiered in this case)

The formula for finding wav file duration is from here:
https://stackoverflow.com/questions/7833807/get-wav-file-length-or-duration

I changed the TextGrid format in this version so that the first tier holds longer intervals first, utterances, meant also to include semi-utterances; then the second tier to be for single words, or phrases if you so choose (and so this second tier is initially blank with no intervals).

'''

with contextlib.closing(wave.open(filepath, 'r')) as f:
    frames = f.getnframes()
    rate = f.getframerate()
    duration = frames / float(rate)

intervals = []
for i in range(len(filtered_boundaries) - 1):
    intervals.append([filtered_boundaries[i], filtered_boundaries[i + 1]])


tg_head = 'File type = "ooTextFile"\nObject class = "TextGrid"\n\n'
tg_interval = f"0 {duration}\n<exists>\n2\n"
tg_tier_head0 = f'"IntervalTier"\n"utterances"\n'
tg_tiers0 = f'0 {duration}\n{len(intervals)} intervals\n'
tg_tier_intervals = ""
for interval in intervals:
    tg_tier_intervals += f'{interval[0]} {interval[1]}\n'
    tg_tier_intervals += '""'
    tg_tier_intervals += "\n"
tg_tier_head1 = f'"IntervalTier"\n"words"\n'

full_string = tg_head + tg_interval + tg_tier_head0 + tg_tiers0 + \
    tg_tier_intervals + tg_tier_head1 + \
    f'0 {duration}\n' + '0 intervals'
# I think printing the output's helpful but you can get rid of this if you'd like
if printBool in pos_vals:
    print("\n««<<\tFile contents:\t>>»»\n")
    print(full_string)
elif printBool in neg_vals:
    pass
else:
    pass

wo_extension = filepath.split("/")[-1].split('.')[-2]
with open(f"./{wo_extension}1.TextGrid", 'w') as file:
    file.write(full_string)
