#!/usr/bin/env python3
"""Validate a GNOS lesson JSON file against a course JSON file."""
import argparse
import json
from pathlib import Path
import sys

from course_contract import validate_course
from lesson_contract import lesson_design_fingerprint, validate_lesson


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lesson", type=Path)
    parser.add_argument("--course", required=True, type=Path)
    parser.add_argument("--design-fingerprint", action="store_true",
                        help="print the authored-content hash for a reviewed draft; does not record a review")
    parser.add_argument("--for-publication", action="store_true",
                        help="require a content-bound review for a new ready publication")
    args = parser.parse_args()
    try:
        course = validate_course(json.loads(args.course.read_text()))
        lesson = validate_lesson(json.loads(args.lesson.read_text()), course,
                                 require_content_binding=args.for_publication)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, f"Invalid lesson: {exc}\n")
    if args.design_fingerprint:
        print(lesson_design_fingerprint(lesson))
    else:
        print(f"Valid: {lesson['title']} ({len(lesson['blocks'])} blocks, {len(lesson['exercises'])} exercises)")


if __name__ == "__main__":
    main()
