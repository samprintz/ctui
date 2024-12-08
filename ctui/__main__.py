#!/usr/bin/env python
import os.path
from argparse import ArgumentParser

import ctui.util as util
from ctui.core import Core
from ctui.ui import UI


def main():
    parser = ArgumentParser(prog='ctui',
                            description='Contact TUI')

    parser.add_argument("--config",
                        default="~/.config/ctui/config.ini",
                        help="configuration file")

    parser.add_argument("--names",
                        action="store_true",
                        help="print names and exit")

    args = parser.parse_args()

    config_path = os.path.expanduser(args.config)

    if not os.path.isfile(config_path):
        print(f'Configuration file not found: "{config_path}"')
        exit(0)

    config = util.load_config(config_path)

    core = Core(config)

    if args.names:
        for name in core.contact_handler.load_contact_names():
            print(name)
        exit(0)

    UI(core, config).run()


if __name__ == "__main__":
    main()
