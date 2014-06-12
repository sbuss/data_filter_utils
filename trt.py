import argparse
from collections import OrderedDict
import csv
from itertools import groupby

import line_filters
from reader import filtered_reader
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
            if not key:
                continue
            group_data = list(group)
            # Response time always excludes wrong answers, but accuracy doesnt
            self.groups[key] = {
                'response_time': meanstdv(
                    to_float([datum['response_time']
                              for datum in filtered_reader(
                                  group_data, [line_filters.exclude_wrong])])),
                'accuracy': meanstdv(
                    to_float([datum['accuracy']
                              for datum in group_data]))
            }
        self.groups['overall'] = {
            'response_time': meanstdv(
                to_float([datum['response_time']
                          for datum in filtered_reader(
                              data, [line_filters.exclude_wrong])])),
            'accuracy': meanstdv(
                to_float([datum['accuracy']
                          for datum in data]))
        }


def _summarize(filename, name, filters, exclude_lines=0):
    reader = filtered_reader(
        csv.DictReader(open(filename, 'rU')),
        filters=filters,
        exclude_lines=exclude_lines)
    summary = Summarizer(name, reader, 'class')
    data = OrderedDict()
    for (key, datum) in sorted(summary.groups.items(), key=lambda d: d[0]):
        data['%s-response_time_avg' % key] = \
            datum['response_time'].average
        data['%s-response_time_std_dev' % key] = \
            datum['response_time'].std_dev
        data['%s-accuracy_avg' % key] = \
            datum['accuracy'].average
        data['%s-accuracy_std_dev' % key] = \
            datum['accuracy'].std_dev
    return data


def summarize_trt(filename):
    """Filter and summarize a single TRT file four ways:

    * One pass include all
    * One pass exclude outliers
    * One pass exclude < 200, > 2000
    * One pass exclude both
    (Always exclude incorrect responses for RT calc)
    """
    path, name = filename.rsplit("/", 1)
    trt_name = name.rsplit(".", 1)[0]

    all_data = []

    # Build the std-dev filter
    response_times = get_float_values(filename, 'response_time')
    mean, stddev = meanstdv(response_times)
    std_dev_filter = line_filters.exclude_std_dev(
        mean, stddev, max_sigma=2.5)

    # Include all data
    for name, filters in [
            ('all', []),
            ('exclude outliers', [std_dev_filter]),
            ('exclude <200ms and >2000ms',
             [line_filters.exclude_response_time_out_of_range]),
            ('exclude both',
             [std_dev_filter,
              line_filters.exclude_response_time_out_of_range])]:
        data = OrderedDict()
        data['trt_session'] = "%s-%s" % (trt_name, name)
        # Actually exclude the first *17* lines because there's a blank
        # first line after the heading
        summary_items = _summarize(
            filename, name, filters, exclude_lines=17).items()
        # I'm not sure if OrderedDict.update respects ordering, so...
        for (key, d) in summary_items:
            data[key] = d
        all_data.append(data)
    return all_data


def summarize_all_trt(dirname):
    outfile_name = 'trt-summary.csv'
    writer = None
    for infile_name in files_in_dir(dirname, trt_filename_pattern):
        print("Processing %s" % infile_name)
        try:
            data = summarize_trt(infile_name)
            if writer is None:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(open(outfile_name, 'w'), fieldnames)
                writer.writeheader()
            for datum in data:
                writer.writerow(datum)
        except Exception as e:
            print("Couldn't parse %s correctly." % infile_name)
            print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse data files")
    parser.add_argument(
        "data_dir",
        help="The directory which contains all of your data files.")
    args = parser.parse_args()
    summarize_all_trt(args.data_dir)
