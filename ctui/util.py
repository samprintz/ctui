import configparser


def load_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config
