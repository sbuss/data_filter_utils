"""Give me a directory and I'll process all csvs in it."""
import argparse
import csv
from os import walk
from os import path
from os import makedirs
import re

import line_filters
from stats import meanstdv


patterns = {
    'trt': 'trt.*\.csv',
}


def files_in_dir(dirname, pattern):
    for (dirpath, dirnames, filenames) in walk(dirname):
        for filename in filenames:
            if re.match(pattern, filename):
                yield path.join(dirpath, filename)


def filter(infile_name, filters, outfile_name):
    reader = csv.DictReader(open(infile_name, 'rU'))
    writer = csv.DictWriter(open(outfile_name, 'w'), reader.fieldnames)
    writer.writeheader()
    included = 0
    excluded = 0
    for line in reader:
        if any(fltr(line) for fltr in filters):
            excluded += 1
        else:
            writer.writerow(line)
            included += 1
    print("Included %s lines, excluded %s lines" % (included, excluded))


def get_float_values(infile_name, field_name):
    values = []
    infile = csv.DictReader(open(infile_name, 'rU'))
    for line in infile:
        try:
            value = float(line[field_name])
        except:
            pass
        else:
            values.append(value)
    return values


def filter_all_trt(dirname):
    """Filter all TRT csv files in `dirname`."""
    outdir = 'data/trt'
    try:
        makedirs(outdir)
    except:
        pass
    for infile_name in files_in_dir(dirname, patterns['trt']):
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
            filter(infile_name,
                   [line_filters.exclude_wrong,
                    line_filters.exclude_response_time_out_of_range,
                    std_dev_filter],
                   outfile_name)
        except Exception as e:
            print("Couldn't parse %s correctly." % infile_name)
            print(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse data files")
    parser.add_argument(
        "data_dir",
        help="The directory which contains all of your data files.")
    parser.add_argument(
        "-f", "--filetype",
        choices=['trt'],
        help="The filetype.")
    args = parser.parse_args()
    if not args.filetype:
        raise ValueError("You must specify a file type.")
    if args.filetype.lower() == 'trt':
        filter_all_trt(args.data_dir)
    else:
        raise ValueError("Invalid filetype.")
