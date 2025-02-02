import configparser

alphanumeric = r'[^a-zA-Z0-9À-ÖØ-öø-ÿČčĆćĐđŠšŽž -]'


def load_config(path):
    config = configparser.ConfigParser()
    config.read(path)
    return config
