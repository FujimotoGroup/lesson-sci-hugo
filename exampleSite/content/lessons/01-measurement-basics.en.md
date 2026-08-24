---
title: "Center and spread of measurements"
linkTitle: "Center and spread of measurements"
lesson: 1
weight: 1
duration: "20 min"
toc: true
summary: "Calculate the mean and standard deviation of five measurements and interpret them separately."
prerequisites:
  - "Create a Python list"
  - "Run Python from a terminal"
objectives:
  - "Calculate the mean of measurements"
  - "Explain standard deviation as a measure of spread"
  - "Report a result with its unit"
---

{{< goal >}}
Calculate the mean and standard deviation of five measurements, then distinguish the representative value from the spread of the measurements.
{{< /goal >}}

{{< code-link path="code/lesson-01.py" >}}

## Prepare the measurements

Suppose that measuring the same object five times gives the following lengths in centimeters. {{< xref id="measurement-values" >}} lists every measurement.

{{< table id="measurement-values" caption="Five length measurements" >}}
| Measurement | Length / cm |
| ---: | ---: |
| 1 | 10.1 |
| 2 | 9.9 |
| 3 | 10.0 |
| 4 | 10.2 |
| 5 | 9.8 |
{{< /table >}}

```python
measurements = [10.1, 9.9, 10.0, 10.2, 9.8]
```

{{< predict >}}
Before calculating, predict whether the mean will be greater than, less than, or equal to `10.0 cm`.
{{< /predict >}}

## Calculate the mean

```python
from statistics import fmean

mean = fmean(measurements)
print(f"mean: {mean:.2f} cm")
```

{{< expected-output >}}
mean: 10.00 cm
{{< /expected-output >}}

## Modify the data

{{< exercise >}}
Change the last measurement from `9.8` to `9.0`, predict the effect on both statistics, and run the code again.
{{< /exercise >}}

{{< hint >}}
The value `9.0` is far from the other four measurements. Consider its effect on center and spread separately.
{{< /hint >}}

{{< solution >}}
The mean becomes `9.84 cm`, while the sample standard deviation increases to approximately `0.483 cm`.
{{< /solution >}}
