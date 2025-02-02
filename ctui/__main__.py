#!/usr/bin/env python
import os.path
from argparse import ArgumentParser

import ctui.util as util
from ctui.core import Core
from ctui.ui import UI
from ctui.model.contact import Contact


def main():
    parser = ArgumentParser(prog='ctui',
                            description='Contact TUI')

    parser.add_argument("--config",
                        default="~/.config/ctui/config.ini",
                        help="configuration file")

    parser.add_argument("--names",
                        action="store_true",
                        help="print names and exit")

    parser.add_argument("--select",
                        metavar="<contact_name>",
                        help="select a contact by name")

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

    ui = UI(core, config)

    if args.select:
        contact_id = Contact.name_to_id(args.select)
        core.select_contact(contact_id)

    ui.run()


if __name__ == "__main__":
    main()
