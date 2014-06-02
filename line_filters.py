exclude_wrong = lambda line: line['accuracy'] == '0'
exclude_response_time_out_of_range = lambda line: (
    line['response_time'] == 'NA' or
    not line['response_time'] or
    int(line['response_time']) < 200 or
    int(line['response_time']) > 2000)


def exclude_std_dev(mean, sigma, min_sigma=None, max_sigma=None):
    """
    Exclude data < (min_sigma * sigma) and > (max_sigma * sigma) from mean.

    Args:
        mean: The mean of the data
        sigma: The standard deviation of your data
        min_sigma: How many sigmas below the mean you want to treat as valid.
            If None, then all data will be included.
        max_sigma: How many sigmas above the mean you want to treat as valid.
            If None, then all data will be included.

    Returns a closure around this data so you can use it as a regular
    line filter.
    """
    if min_sigma is not None:
        lower = mean - min_sigma * sigma
    else:
        lower = -float("inf")

    if max_sigma is not None:
        upper = mean + max_sigma * sigma
    else:
        upper = float("inf")

    def filter_line(line):
        try:
            return (float(line['response_time']) < lower or
                    float(line['response_time']) > upper)
        except:
            return True

    return filter_line
