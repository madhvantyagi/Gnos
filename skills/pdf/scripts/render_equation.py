#!/usr/bin/env python3
"""Render a mathtext expression into a sharp transparent PNG."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


def render(expression, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(0.1, 0.1))
    fig.text(0, 0, '$' + expression.strip('$') + '$', fontsize=22, color='#172c35')
    try:
        fig.savefig(output, dpi=220, bbox_inches='tight', pad_inches=0.08, transparent=True)
    finally:
        plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('expression')
    parser.add_argument('-o', '--output', type=Path, required=True)
    args = parser.parse_args()
    render(args.expression, args.output)
