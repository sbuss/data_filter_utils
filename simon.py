import argparse
import csv
from copy import deepcopy

import line_filters
from reader import filtered_reader
from reader import get_float_values
from stats import meanstdv
from summary import summarize_all
from summary import summarize_reader

simon_filename_pattern = r'.*((?i)SIMON).*\.csv'


def cog_incog_reader(reader):
    """Annotate each line in a reader with congruent/incongruent

    Note: The box in the middle of the screen is always considered congruent.
    """
    for line in reader:
        cog_incog_line = deepcopy(line)
        cog_incog_line['congruent'] = 'incongruent'
        if ((line['box_img'] == 'redsquare.bmp' and
                line['alignment'] in ['left', 'center']) or
                (line['box_img'] == 'bluesquare.bmp' and
                    line['alignment'] in ['right', 'center'])):
            cog_incog_line['congruent'] = 'congruent'
        yield cog_incog_line


def summarize_simon(filename):
    """Filter and summarize simon data.

    Exclude the first 24 lines of practice
    Do normal correct response filtering
    Group data on congruent and incongruent
    """
    path, name = filename.rsplit("/", 1)
    simon_name = name.split("_", 1)[0]

    # Build the std-dev filter
    response_times = get_float_values(filename, 'response_time')
    mean, stddev = meanstdv(response_times)
    std_dev_filter = line_filters.exclude_std_dev(
        mean, stddev, max_sigma=2.5, min_sigma=2.5)

    reader = filtered_reader(
        csv.DictReader(open(filename, 'rU')),
        filters=[std_dev_filter],
        exclude_lines=24)
    data = summarize_reader(simon_name, cog_incog_reader(reader), 'congruent')
    data['participant'] = simon_name
    data['simon_score'] = data['AvgRT-incongruent'] - data['AvgRT-congruent']
    return [data]


def summarize_all_simon(dirname):
    outfile_name = 'simon-summary.csv'
    summarize_all(
        dirname, simon_filename_pattern, outfile_name, summarize_simon)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse data files")
    parser.add_argument(
        "data_dir",
        help="The directory which contains all of your data files.")
    args = parser.parse_args()
    summarize_all_simon(args.data_dir)
