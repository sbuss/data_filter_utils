"""Give me a directory and I'll process all csvs in it."""
import csv
from os import walk
from os import path
import re


patterns = {
    'trt': 'trt.*\.csv',
}


def files_in_dir(dirname, pattern):
    for (dirpath, dirnames, filenames) in walk(dirname):
        for filename in filenames:
            if re.match(pattern, filename):
                yield path.join(dirpath, filename)


def filter_file(infile_name, filters, outfile_name):
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
    infile = csv.DictReader(open(infile_name, 'rU'))
    return to_float(line[field_name] for line in infile)


def to_float(iterable):
    values = []
    for elem in iterable:
        try:
            value = float(elem)
        except:
            pass
        else:
            values.append(value)
    return values
