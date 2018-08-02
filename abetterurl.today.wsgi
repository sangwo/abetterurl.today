#!/usr/bin/python
activate_this = '/var/www/abetterurl.today/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/abetterurl.today")

from abetterurltoday import app as application
