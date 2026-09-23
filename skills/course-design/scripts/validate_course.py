#!/usr/bin/env python3
"""Validate a GNOS course without calling a model or changing files."""
import argparse
import json
from pathlib import Path
import sys

from course_contract import course_topics, validate_course


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('course', type=Path)
    args = parser.parse_args()
    try:
        data = validate_course(json.loads(args.course.read_text()))
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Invalid course: {exc}\n')
    print(f"Valid: {data['title']} ({len(course_topics(data))} topics)")


if __name__ == '__main__':
    main()
