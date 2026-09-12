#!/usr/bin/env python3
"""Search the local source catalog; does not claim a fresh network check."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SUBJECTS = ('math', 'physics', 'history', 'biology', 'economics', 'computer-science')


def resources():
    return json.loads((ROOT / 'skills/subject/references/resources.json').read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--subject', choices=SUBJECTS)
    parser.add_argument('--query', default='')
    args = parser.parse_args()
    rows = [r for r in resources() if (not args.subject or args.subject in r['subjects'])
            and args.query.casefold() in json.dumps(r).casefold()]
    print(json.dumps(rows, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
