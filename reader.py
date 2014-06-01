"""Give me a directory and I'll process all csvs in it."""
import csv
from os import walk
import re


patterns = {
    'trt': 'trt.*\.csv',
}


def files_in_dir(dirname, pattern):
    for (dirpath, dirnames, filenames) in walk(dirname):
        for filename in filenames:
            if re.match(pattern, filename):
                yield filename


def filter(infile_name, filters, outfile_name):
    reader = csv.DictReader(open(infile_name, 'r'))
    writer = csv.DictWriter(open(outfile_name, 'w'), reader.fieldnames)
    writer.writeheader()
    included = 0
    excluded = 0
    for line in reader:
        print("%s, %s" % (line['accuracy'], line['response_time']))
        filtered = [fltr(line) for fltr in filters]
        print(filtered)
        if any(filtered):
            print("excluding")
            excluded += 1
        else:
            writer.writerow(line)
            included += 1
    print("Included %s lines, excluded %s lines" % (included, excluded))
