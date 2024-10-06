B, RD, GR, YL, BL, PR, CY, BRD, BGR, BYL, BBL, BPR, BCY = [
    lambda msg, i=i: f"\x1b[{i}m{msg}\x1b[m" for i in [1, *range(31,37), *range(91,97)]
]
