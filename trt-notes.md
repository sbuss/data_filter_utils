# Filtering

Exclude practice (the first 16)
Only correct responsess were used for analysis
Responses between 200ms and 2000ms were considered valid
responses slower than 2.5 std-devs beyond mean were excluded as outliers
  (On average, 4.11% of data excluded as outliers)

# Summarizing

1. Group by class
2. Average response_time (See below)
3. Average accuracy (over all correct and incorrect responses that were filtered)

Also overall accuracy and average

Make each class it's own column, too.


## Calculating response time stats
* Always exclude incorrect responses
  * One pass include all
  * One pass exclude outliers
  * One pass exclude < 200, > 2000
  * One pass exclude both


# CSV

For ordering columns: accurracy all constraints first
