from statistics import fmean


def summarize_measurements() -> float:
    # --8<-- [start:measurement-values]
    measurements = [10.1, 9.9, 10.0, 10.2, 9.8]
    mean = fmean(measurements)
    print(f"mean: {mean:.2f} cm")
    # --8<-- [end:measurement-values]
    return mean
