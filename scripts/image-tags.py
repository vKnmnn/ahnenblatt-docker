#!/usr/bin/env python3
"""Keep local and CI image aliases identical; only stable series 5 owns latest."""
import argparse
from versions import read_manifest


def tags(series, version, wine):
    if wine != '11':
        raise ValueError(f'Unsupported Wine major: {wine}')
    result = [f'{series}-wine{wine}', f'{version}-wine{wine}']
    result += [series, version]
    if series == '5':
        result.append('latest')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('series', choices=['2.99', '3', '4', '5'])
    parser.add_argument('wine', choices=['11'])
    parser.add_argument('image')
    args = parser.parse_args()
    version = read_manifest()[args.series]['version']
    print('\n'.join(f'{args.image}:{tag}' for tag in tags(args.series, version, args.wine)))
