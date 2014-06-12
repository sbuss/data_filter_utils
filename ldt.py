import argparse
import csv
from copy import deepcopy

from reader import filtered_reader
from summary import summarize_all
from summary import summarize_reader

ldt_filename_pattern = r'ldt.*\.csv'


def word_nonword_reader(reader):
    """Annotate each line in a reader with congruent/incongruent"""
    for line in reader:
        word_nonword_line = deepcopy(line)
        word_nonword_line['word_or_nonword'] = ''
        if line['image'].startswith('j'):
            word_nonword_line['word_or_nonword'] = 'nonword'
        elif line['image'].startswith('word'):
            word_nonword_line['word_or_nonword'] = 'word'
        yield word_nonword_line


def summarize_ldt(filename):
    """Filter and summarize ldt data.

    Exclude the first XXX lines of practice
    Do normal correct response filtering
    Group data on congruent and incongruent
    """
    path, name = filename.rsplit("/", 1)
    participant_name = name.rsplit(".", 1)[0]

    # ldt files are all weird with two heading rows...
    reader = open(filename, 'rU')
    reader.readline()
    reader.readline()
    # TODO: Choose a correc exclude_lines value
    reader = filtered_reader(
        csv.DictReader(reader),
        filters=[],
        exclude_lines=5)
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
