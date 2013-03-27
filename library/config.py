import configparser
import os

ini = configparser.ConfigParser()
ini.read(os.path.join(os.path.abspath(os.path.dirname(__file__) + '/..'), 'cfg.ini'))
