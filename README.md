Data filtering & summarizing tools for my fiancée's research.

# Basic flow:

```
For all files in a directory (that match a filename pattern):
    Open the file using a filtered reader
    Pass the file through summarize_reader
        Build a Summarize object to calculate avg/std_dev of response_time and accuracy
    Write the results to a file
```

## Filtered Readers

A `filtered_reader` is just a wrapper on top of file objects which discard
lines if they satisfy one of the given `filters`. This is especially useful
if you pass in a `DictReader`, so we can filter on particular fields of that
line.

For example, say your data looks like:

```
participant,correct,stimulus,response,response_time_ms
1,0,A,B,600
1,1,C,B,480
...
```

This shows participant 1 being shown two stimuli, and inputting two values.
They got the first one wrong (typed B which didn't match the stimulus A), and 
got the second one right. Now you want to calculate the average respone time
of correct responses. You could use filter out these incorrect lines with a
filter function that looks like:

```python
lambda line: line['correct'] == '0'
```

This function returns `True` when the `correct` field is 0, which causes the
`filtered_reader` to discard the line.

The full program would look like:

```python
filters = [
    lambda line: line['correct'] == '0',
]
data = summarize_file('data.csv', 'John Smith', filters)
```

## Summarize Reader

The `summarize_reader` takes a file-like object and calculates summary values
on its data. It's really only useful with a `DictReader`-type object, since it
expects to be able to access fields by key.

It builds a Summary object on the file by grouping the data by the given `key`
and then calculating average and standard deviation for response time and 
accuraccy. Note that it excludes incorrect responses when calculating
response time values.
