#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import srt
from os import path


def merge_subs(subs):
    new_subs = []
    for i in range(len(subs)):
        if i == 0:
            new_subs.append(subs[i])
        else:
            if (
                subs[i].content == new_subs[-1].content
                and subs[i].start == new_subs[-1].end
            ):
                new_subs[-1] = srt.Subtitle(
                    new_subs[-1].index,
                    new_subs[-1].start,
                    subs[i].end,
                    new_subs[-1].content,
                )
            else:
                new_subs.append(subs[i])
    return new_subs


def get_filter_words(filename):
    with open(filename) as f:
        return f.read().split("\n")


def filter_subs(subs, filter_words):
    new_subs = []
    for sub in subs:
        if sub.content in filter_words:
            continue
        if sub.content.startswith("♪") or sub.content.startswith("♫"):
            continue
        if sub.content.startswith("(") and sub.content.endswith(")"):
            continue
        if sub.content.startswith("(") and sub.content.endswith(")"):
            continue
        new_subs.append(sub)
    return new_subs


def main(arg):
    parser = argparse.ArgumentParser(description="Post handle after whisper.cpp")
    parser.add_argument("srt_file", help="srt file to post handle")
    parser.add_argument("-o", "--output", help="output file")
    parser.add_argument("-f", "--filter", help="filter file")
    args = parser.parse_args(arg)
    filename = args.srt_file
    new_filename = (
        args.output
        if args.output
        else path.splitext(filename)[0] + "_post" + path.splitext(filename)[1]
    )
    sub = open(filename,errors='ignore').read()
    subs = list(srt.parse(sub))
    new_subs = merge_subs(subs)
    filter_path = (
        args.filter if args.filter else path.join(path.dirname(__file__), "filter.txt")
    )
    filter_words = get_filter_words(filter_path)
    new_subs = filter_subs(new_subs, filter_words)
    with open(new_filename, "w") as f:
        f.write(srt.compose(new_subs))


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
