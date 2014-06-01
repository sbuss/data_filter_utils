exclude_wrong = lambda line: line['accuracy'] == '0'
exclude_data = lambda line: (line['response_time'] == 'NA' or
                             int(line['response_time']) < 200 or
                             int(line['response_time']) > 2000)
