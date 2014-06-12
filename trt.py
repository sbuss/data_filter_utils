import argparse
import csv
from itertools import groupby
from os import makedirs
import os

import line_filters
from reader import filter_file
from reader import files_in_dir
from reader import get_float_values
from reader import to_float
from stats import meanstdv


trt_filename_pattern = r'trt.*\.csv'


class Summarizer(object):
    def __init__(self, name, reader, group_field):
        self.reader = reader
        self.name = name
        self.group_field = group_field
        self.groups = {}
        self._read_and_populate()

    def _read_and_populate(self):
        data = list(self.reader)
        # Sort data by group_field
        key_func = lambda d: d[self.group_field].lower()
        sorted_data = sorted(data, key=key_func)
        for key, group in groupby(sorted_data, key_func):
            group_data = list(group)
            self.groups[key] = {
                'response_time': meanstdv(
                    to_float([datum['response_time']
                              for datum in group_data])),
                'accuracy': meanstdv(
                    to_float([datum['accuracy']
                              for datum in group_data]))
            }


def summarize(dirname):
    print("Summarizing %s" % dirname)
    fieldnames = [
        'trt_session', 'class',
        'response_time_avg', 'response_time_std_dev',
        'accuracy_avg', 'accuracy_std_dev']
    outfile_name = os.path.join(dirname, "summary.csv")
    writer = csv.DictWriter(open(outfile_name, 'w'), fieldnames)
    writer.writeheader()

    for infile_name in files_in_dir(dirname, trt_filename_pattern):
        path, name = infile_name.rsplit("/", 1)
        trt_session = name.rsplit(".", 1)[0]
        reader = csv.DictReader(open(infile_name, 'rU'))
        summary = Summarizer(infile_name, reader, 'class')
        for (key, data) in sorted(summary.groups.items(), key=lambda d: d[0]):
            writer.writerow(
                {fieldnames[0]: trt_session,
                 fieldnames[1]: key,
                 fieldnames[2]: data['response_time'].average,
                 fieldnames[3]: data['response_time'].std_dev,
                 fieldnames[4]: data['accuracy'].average,
                 fieldnames[5]: data['accuracy'].std_dev})


def filter_all_trt(dirname):
    """Filter all TRT csv files in `dirname`.

    This loads all of the source csv files from OpenSesame, filters the
    lines, and writes out the filtered files to `data/trt/%s-filtered.csv`,
    where %s is the original filename.
    """
    # Prepare the output
    outdir = 'data/trt'
    try:
        makedirs(outdir)
    except:
        pass

    for infile_name in files_in_dir(dirname, trt_filename_pattern):
        print("Filtering %s" % infile_name)
        path, name = infile_name.rsplit("/", 1)
        trt_name = name.rsplit(".", 1)[0]
        outfile_name = "data/trt/%s-filtered.csv" % trt_name
        try:
            # To do the std-dev filtering we have to do a first pass over the
            # data first.
            response_times = get_float_values(infile_name, 'response_time')
            mean, stddev = meanstdv(response_times)
            std_dev_filter = line_filters.exclude_std_dev(
                mean, stddev, max_sigma=2.5)
            filter_file(infile_name,
                        [line_filters.exclude_wrong,
                         line_filters.exclude_response_time_out_of_range,
                         std_dev_filter],
                        outfile_name)
        except Exception as e:
            print("Couldn't parse %s correctly." % infile_name)
            print(e)
    return outdir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse data files")
    parser.add_argument(
        "data_dir",
        help="The directory which contains all of your data files.")
    args = parser.parse_args()
    outdir = filter_all_trt(args.data_dir)
    summarize(outdir)
