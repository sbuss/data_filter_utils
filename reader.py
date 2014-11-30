"""Give me a directory and I'll process all csvs in it."""
import csv
from os import walk
from os import path
import re

from natsort import natsorted


def files_in_dir(dirname, pattern):
    matched_files = []
    for (dirpath, dirnames, filenames) in walk(dirname):
        for filename in filenames:
            if re.match(pattern, filename):
                matched_files.append(path.join(dirpath, filename))
    return natsorted(matched_files)


def filtered_reader(file_like, filters, exclude_lines=0):
    """Read a file-like object, applying the given filters.

    Args:
        filters: A list of callables to apply to each line of the file. If
            any of the filters returns True, then the line is discarded.
        exclude_lines: The number of leading lines in the file to exclude.
            This is useful for excluding the practice runs that occur at
            the beginning of the file.
    """
    skipped = 0
    included = 0
    excluded = 0
    for line in file_like:
        if skipped < exclude_lines:
            skipped += 1
            continue
        if any(fltr(line) for fltr in filters):
            excluded += 1
        else:
            yield line
            included += 1
    print("Included %s lines, skipped %s lines, excluded %s lines" % (
        included, skipped, excluded))


def filter_file(infile_name, filters, outfile_name, exclude_lines=0):
    """Filter infile by applying filters, and writing to outfile.

    Args:
        infile_name: The name/path to the input csv
        filters: A list of callables to apply to each line of the file. If
            any of the filters returns True, then the line is discarded.
        outfile_name: The name/path of the file to write to
        exclude_lines: The number of leading lines in the file to exclude.
            This is useful for excluding the practice runs that occur at
            the beginning of the file.
    """
    reader = csv.DictReader(open(infile_name, 'rU'))
    writer = csv.DictWriter(open(outfile_name, 'w'), reader.fieldnames)
    writer.writeheader()
    for line in filtered_reader(reader, filters, exclude_lines=exclude_lines):
        writer.writerow(line)


def get_float_values(infile_name, field_name, exclude_lines=0):
    infile = csv.DictReader(open(infile_name, 'rU'))
    return to_float(line[field_name]
                    for line in filtered_reader(infile, [], exclude_lines))


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
