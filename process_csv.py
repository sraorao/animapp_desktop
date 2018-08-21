#!/home/srao/virtualenvs/opencv/bin/python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help = 'csv file with 3 columns (x, y, frame) without header line')
parser.add_argument('-o', '--output', help = 'suffix to be added to output csv file', default = '_processed')
args = parser.parse_args()

import pandas as pd
import process_csv_module as pcsv

original_csv = pd.read_csv(args.file, names = ['x', 'y', 'frame'], usecols = [0, 1, 2])
filled_csv = pcsv.fill_frames(original_csv)
pcsv.calculate_velocity(filled_csv)
pcsv.calculate_rolling_velocity(filled_csv)
filtered_csv = pcsv.filter_by_rolling_velocity(filled_csv, 10)

print "original:\n", original_csv.head()
print "processed:\n", filled_csv.head()

filled_csv.to_csv(args.file + args.output + ".csv", index = False, header = False)
filtered_csv.to_csv(args.file + args.output + "_filtered.csv", index = False, header = False)
