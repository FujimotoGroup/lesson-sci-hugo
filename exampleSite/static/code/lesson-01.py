"""Lesson 1: summarize repeated measurements."""

from statistics import fmean, stdev


measurements = [10.1, 9.9, 10.0, 10.2, 9.8]
mean = fmean(measurements)
spread = stdev(measurements)

print(f"mean: {mean:.2f} cm")
print(f"sample standard deviation: {spread:.3f} cm")
