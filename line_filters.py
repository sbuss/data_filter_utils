exclude_wrong = lambda line: line['accuracy'] == '0'
exclude_response_time_out_of_range = lambda line: (
    line['response_time'] == 'NA' or
    not line['response_time'] or
    int(line['response_time']) < 200 or
    int(line['response_time']) > 2000)
