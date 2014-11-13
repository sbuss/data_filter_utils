import argparse
import csv
from copy import deepcopy

import line_filters
from reader import filtered_reader
from reader import get_float_values
from stats import meanstdv
from summary import summarize_all
from summary import summarize_reader

ldt_filename_pattern = r'.*LDT.*\.csv'


def word_nonword_reader(reader):
    """Annotate each line in a reader with word/nonword.

    In the bilingual files, this is set by the `isword` variable (1 is True),
    in the immersion files, this is set by the filename of the image
    displayed - if the filename starts with 'word', then it's a real word.
    """
    for line in reader:
        word_nonword_line = deepcopy(line)
        word_nonword_line['word_or_nonword'] = ''
        if 'isword' in line:
            if line['isword'] == '1':
                word_nonword_line['word_or_nonword'] = 'word'
            else:
                word_nonword_line['word_or_nonword'] = 'nonword'
        else:
            if line['image'].startswith('j'):
                word_nonword_line['word_or_nonword'] = 'nonword'
            elif line['image'].startswith('word'):
                word_nonword_line['word_or_nonword'] = 'word'
        yield word_nonword_line


def summarize_ldt(filename):
    """Filter and summarize ldt data.

    Exclude the first 16 lines of practice
    Do normal correct response filtering
    Group data on congruent and incongruent
    """
    path, name = filename.rsplit("/", 1)
    participant_name = name.split("_", 1)[0]

    # Build the std-dev filter
    response_times = get_float_values(filename, 'response_time')
    mean, stddev = meanstdv(response_times)
    std_dev_filter = line_filters.exclude_std_dev(
        mean, stddev, max_sigma=2.5, min_sigma=2.5)

    # ldt files are sometimes weird with two heading rows...
    with open(filename, 'rU') as f:
        num_lines = 0
        for line in f:
            num_lines += 1
    reader = open(filename, 'rU')
    expected_lines = (1 +   # header
                      16 +  # practice
                      60 +  # correct words
                      60    # incorrect words
                      )
    for i in range(num_lines - expected_lines):
        reader.readline()
    reader = filtered_reader(
        csv.DictReader(reader),
        filters=[std_dev_filter],
        exclude_lines=16)
    data = summarize_reader(
        participant_name, word_nonword_reader(reader), 'word_or_nonword')
    data['participant'] = participant_name
    return [data]


def summarize_all_ldt(dirname):
    outfile_name = 'ldt-summary.csv'
    summarize_all(
        dirname, ldt_filename_pattern, outfile_name, summarize_ldt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse data files")
    parser.add_argument(
        "data_dir",
        help="The directory which contains all of your data files.")
    args = parser.parse_args()
    summarize_all_ldt(args.data_dir)
