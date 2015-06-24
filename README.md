# foos-rating

https://ajberglund.github.io/foos-rating/

Compute rating updates for any two-team game played to a fixed number of points


Using similar methods to an Elo rating system, the probability that Team A will
score any particular point is computed based on the rating difference between
Team A and Team B. With this probability of success *per point*, the distribution of final game scores is computed,
and the teams' ratings are adjusted toward the maximum likelihood
difference between ratings corresponding to the actual game score. 

Parameters are tuned to expect ratings roughly in the range 1000 to 2000 and games played to 5 points.

Win probabilities and score distributions are calculated using simple recursive definitions and memoization. A correction factor accounts for rating bias by discounting the point spread. See foos.py and images in the png directory for information on the correction factor.

Typical point spreads look like:
```
Team A (1500) is expected to score with probability 0.72
Team B (1200) is expected to score with probability 0.28
Team A is expected to win with probability 0.92
The score differential is expected to be 2.91
```
and rating update calculations look like:
```
Based on the actual score of 5-4
Ratings are updated to
Rating A = 1486
Rating B = 1214
```

Have fun!
