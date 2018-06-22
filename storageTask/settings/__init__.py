import sys
import yaml
from xylogger import BaseLogger

config = None
with open(sys.argv[1]) as f:
    config = yaml.load(f)
logger = BaseLogger(
    level=config.get('logging_level', 'debug'),
    release_enable=config.get('logging_release', False)).Logger
logger.write = logger.info
