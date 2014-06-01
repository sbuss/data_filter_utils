exclude_wrong = lambda line: line['accuraccy'] == '0'
exclude_data = lambda line: (int(line['response_time']) < 200 or
                             int(line['response_time']) > 2000)
