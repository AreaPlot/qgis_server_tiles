#!/usr/bin/env python

import os
import sys
from typing import Optional
import argparse


def convertPath(path: str, path_type: Optional[str]) -> str:
    parts = [x for x in filter(None, path.split("/"))]
    while parts:
        if parts[0].isdigit() and len(parts[0]) <= 2:
            z = parts.pop(0)
            break
        else:
            parts.pop(0)
    try:
        if len(parts) == 6 or path_type == "tc":
            x = "".join(parts[0:3]).lstrip("0")
            y = "".join(parts[3:]).lstrip("0")
            return os.path.join(z, x, y)
        if len(parts) == 4 or path_type == "mp":
            x = "".join(parts[0:2]).lstrip("0")
            y = "".join(parts[2:]).lstrip("0")
            return os.path.join(z, x, y)
    except Exception as e:
        print(e)
    return None


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "path",
        help="Input path for individual tile.",
        nargs="*",
        #        type=argparse.FileType("r"),
        default="-",
    )
    p.add_argument(
        "-t",
        "--type",
        required=False,
        help="Input path type (tc: tilecache, mp: mapproxy).",
    )
    p.add_argument(
        "-c",
        "--copy",
        required=False,
        help="Return both the input and the output.",
        action="store_true",
    )
    p.add_argument("--prefix", required=False, help="Prefix to apply to output.")

    args = p.parse_args()
    if args.path == "-" and not sys.stdin.isatty():
        args.path = sys.stdin.readlines()
    if not isinstance(args.path, list):
        args.path = [
            args.path,
        ]
    for path_entry in args.path:
        converted = convertPath(path_entry.rstrip(), args.type)
        if converted:
            if args.copy:
                print(args.path, f"{args.prefix or ''}{converted}")
            else:
                print(f"{args.prefix or ''}{converted}")
