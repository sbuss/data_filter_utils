from collections import OrderedDict
import csv
from itertools import groupby

from natsort import natsorted

import line_filters
from reader import files_in_dir
from reader import filtered_reader
from reader import to_float
from stats import meanstdv


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
        sorted_data = natsorted(data, key=key_func)
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


def summarize_reader(name, reader, group):
    data = OrderedDict()
    summary = Summarizer(name, reader, group)
    for (key, datum) in natsorted(summary.groups.items(), key=lambda d: d[0]):
        data['AvgRT-%s' % key] = datum['response_time'].average
        #data['SDRT-%s' % key] = datum['response_time'].std_dev
        data['AvgAcc-%s' % key] = datum['accuracy'].average
    return data


def summarize_file(filename, name, filters, exclude_lines=0):
    reader = filtered_reader(
        csv.DictReader(open(filename, 'rU')),
        filters=filters,
        exclude_lines=exclude_lines)
    data = OrderedDict()
    data.update(summarize_reader(name, reader, 'class'))
    return data


def summarize_all(dirname, file_name_pattern, outfile_name, summarize_method):
    writer = None
    for infile_name in files_in_dir(dirname, file_name_pattern):
        print("Processing %s" % infile_name)
        try:
            data = summarize_method(infile_name)
            if writer is None:
                fieldnames = natsorted(data[0].keys())
                writer = csv.DictWriter(open(outfile_name, 'w'), fieldnames)
                writer.writeheader()
            for datum in data:
                writer.writerow(datum)
        except Exception as e:
            print("Couldn't parse %s correctly." % infile_name)
            print(e)
