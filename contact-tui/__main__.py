import config as cfg
import core
import pudb

import os


config = None
RUN_DIR = os.path.dirname(os.path.realpath(__file__)) + '/'
CONFIG_FILE = '../config'
CONFIG_PATH = RUN_DIR + CONFIG_FILE


def main():
    global config
    config = cfg.load_config(CONFIG_PATH)
    hiea = core.Core(config)


if __name__ == "__main__":
    main()

