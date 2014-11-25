import argparse
import csv
from functools import partial

from line_filters import get_dir_mean_std_filter
from reader import filtered_reader
from summary import summarize_all
from summary import summarize_reader


ospan_filename_pattern = r'.*OSPAN.*\.csv'


def summarize_ospan(filename, std_dev_filter=None):
    """Filter and summarize ospan data.

    Exclude the first 10 lines of practice.
    Do normal correct response filtering
    Group data on congruent and incongruent
    """
    path, name = filename.rsplit("/", 1)
    ospan_name = name.split("_", 1)[0]

    if std_dev_filter:
        filters = [std_dev_filter]
    else:
        filters = []
    reader = filtered_reader(
        csv.DictReader(open(filename, 'rU')),
        filters=filters,
        exclude_lines=24)
    data = summarize_reader(ospan_name, reader, 'use_correct')
    data['participant'] = ospan_name
    return [data]


def summarize_all_ospan(dirname):
    outfile_name = 'ospan-summary.csv'
    std_dev_filter = get_dir_mean_std_filter(
        dirname, ospan_filename_pattern, min_sigma=2.5, max_sigma=2.5,
        exclude_lines=24)
    summarize_fn = partial(summarize_ospan, std_dev_filter=std_dev_filter)
    summarize_all(
        dirname, ospan_filename_pattern, outfile_name, summarize_fn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse data files")
    parser.add_argument(
        "data_dir",
        help="The directory which contains all of your data files.")
    args = parser.parse_args()
    summarize_all_ospan(args.data_dir)
