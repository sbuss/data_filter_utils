import argparse
import csv
from copy import deepcopy
from functools import partial

from line_filters import get_dir_mean_std_filter
from reader import filtered_reader
from summary import summarize_all
from summary import summarize_reader

simon_filename_pattern = r'.*((?i)SIMON).*\.csv'

center_filter = lambda line: line['alignment'] == 'center'


def cog_incog_reader(reader):
    """Annotate each line in a reader with congruent/incongruent

    Note: The box in the middle of the screen is always considered congruent.
    """
    for line in reader:
        cog_incog_line = deepcopy(line)
        cog_incog_line['congruent'] = 'incongruent'
        (color, alignment) = (line['box_img'], line['alignment'])
        if ((color == 'redsquare.bmp' and alignment == 'left') or
                (color == 'bluesquare.bmp' and 'alignment' == 'right')):
            cog_incog_line['congruent'] = 'congruent'
        yield cog_incog_line


def summarize_simon(filename, std_dev_filter=None):
    """Filter and summarize simon data.

    Exclude the first 24 lines of practice
    Do normal correct response filtering
    Group data on congruent and incongruent
    """
    path, name = filename.rsplit("/", 1)
    simon_name = name.split("_", 1)[0]

    filters = [center_filter]
    if std_dev_filter:
        filters.append(std_dev_filter)
    reader = filtered_reader(
        csv.DictReader(open(filename, 'rU')),
        filters=filters,
        exclude_lines=24)
    data = summarize_reader(simon_name, cog_incog_reader(reader), 'congruent')
    data['participant'] = simon_name
    data['simon_score'] = data['AvgRT-incongruent'] - data['AvgRT-congruent']
    return [data]


def summarize_all_simon(dirname):
    outfile_name = 'simon-summary.csv'
    std_dev_filter = get_dir_mean_std_filter(
        dirname, simon_filename_pattern, min_sigma=2.5, max_sigma=2.5,
        exclude_lines=24)
    summarize_fn = partial(summarize_simon, std_dev_filter=std_dev_filter)
    summarize_all(
        dirname, simon_filename_pattern, outfile_name, summarize_fn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse data files")
    parser.add_argument(
        "data_dir",
        help="The directory which contains all of your data files.")
    args = parser.parse_args()
    summarize_all_simon(args.data_dir)
