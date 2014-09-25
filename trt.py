import argparse
from collections import OrderedDict

import line_filters
from reader import get_float_values
from stats import meanstdv
from summary import summarize_all
from summary import summarize_file


trt_filename_pattern = r'.*TRT.*\.csv'


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
        summary_items = summarize_file(
            filename, name, filters, exclude_lines=17).items()
        # I'm not sure if OrderedDict.update respects ordering, so...
        for (key, d) in summary_items:
            data[key] = d
        all_data.append(data)
    return all_data


def summarize_all_trt(dirname):
    outfile_name = 'trt-summary.csv'
    summarize_all(dirname, trt_filename_pattern, outfile_name, summarize_trt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse data files")
    parser.add_argument(
        "data_dir",
        help="The directory which contains all of your data files.")
    args = parser.parse_args()
    summarize_all_trt(args.data_dir)
