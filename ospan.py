import argparse
import csv

import line_filters
from reader import filtered_reader
from reader import get_float_values
from stats import meanstdv
from summary import summarize_all
from summary import summarize_reader


ospan_filename_pattern = r'.*OSPAN.*\.csv'


def summarize_ospan(filename):
    """Filter and summarize ospan data.

    Exclude the first 10 lines of practice.
    Do normal correct response filtering
    Group data on congruent and incongruent
    """
    path, name = filename.rsplit("/", 1)
    ospan_name = name.split("_", 1)[0]

    # Build the std-dev filter
    response_times = get_float_values(filename, 'response_time')
    mean, stddev = meanstdv(response_times)
    std_dev_filter = line_filters.exclude_std_dev(
        mean, stddev, max_sigma=2.5, min_sigma=2.5)

    reader = filtered_reader(
        csv.DictReader(open(filename, 'rU')),
        filters=[std_dev_filter],
        exclude_lines=24)
    data = summarize_reader(ospan_name, reader, 'use_correct')
    data['participant'] = ospan_name
    return [data]


def summarize_all_ospan(dirname):
    outfile_name = 'ospan-summary.csv'
    summarize_all(
        dirname, ospan_filename_pattern, outfile_name, summarize_ospan)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse data files")
    parser.add_argument(
        "data_dir",
        help="The directory which contains all of your data files.")
    args = parser.parse_args()
    summarize_all_ospan(args.data_dir)
