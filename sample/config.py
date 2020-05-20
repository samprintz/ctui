import configparser

def load_config(path):
    cfg = configparser.ConfigParser()
    cfg.read(path)
    config = {
            'path': {
                'rdf_file': cfg.get('paths', 'rdf_file'),
                'notes_dir': cfg.get('paths', 'notes_dir')
                },
            'rdf': {
                'namespace': cfg.get('rdf', 'namespace')
                },
            'editor': 'vim',
            'display': {
                'nav_width': cfg.getint('display', 'nav_width'),
                'palette': [
                    (None,  'light gray', 'black'),
                    ('options', 'light gray', 'black'),
                    ('focus options', 'black', 'light gray'),
                    ('selected', 'black', 'light gray'),
                    ('status_bar', 'light gray', 'black')
                    ],
                'focus_map': {
                    'options': 'focus options'}
                }
            }
    return config

#GIVEN_NAME_REF = URIRef('http://hiea.de/contact#givenName')
#GIFTIDEA_REF = URIRef('http://hiea.de/contact#giftIdea')
#EDITOR = os.environ.get('EDITOR','vim')

