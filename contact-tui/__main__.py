#!/usr/bin/env python
import os.path
from argparse import ArgumentParser

import util as util

import core


def main():
    parser = ArgumentParser(prog='ctui',
                            description='Contact TUI')

    parser.add_argument("--config",
                        default="~/.config/ctui/config.ini",
                        help="configuration file")

    args = parser.parse_args()

    config_path = os.path.expanduser(args.config)

    if not os.path.isfile(config_path):
        print(f'Configuration file not found: "{config_path}"')
        exit(0)

    config = util.load_config(config_path)
    core.Core(config)


if __name__ == "__main__":
    main()

