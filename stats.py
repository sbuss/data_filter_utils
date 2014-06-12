from collections import namedtuple

AvgAndStd = namedtuple('AvgAndStd', ['average', 'std_dev'])


def meanstdv(x):
    """
    Calculate mean and standard deviation of data x[]:
        mean = {\sum_i x_i \over n}
        std = sqrt(\sum_i (x_i - mean)^2 \over n-1)

    Taken from https://www.physics.rutgers.edu/~masud/computing/WPark_recipes_in_python.html  # nopep8
    """
    from math import sqrt
    n, mean, std = len(x), 0, 0
    if n == 0:
        return AvgAndStd('null', 'null')

    for a in x:
        mean = mean + a
    mean = mean / float(n)
    for a in x:
        std = std + (a - mean)**2
    if n == 1:
        return AvgAndStd(mean, 'null')

    std = sqrt(std / float(n-1))
    return AvgAndStd(mean, std)
