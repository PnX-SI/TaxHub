#!/usr/bin/python
import os, sys, logging
logging.basicConfig(stream=sys.stderr)

# Activate your virtual env
activate_env=os.path.expanduser(os.path.join(os.path.dirname(__file__), 'venv/bin/activate_this.py'))
execfile(activate_env, dict(__file__=activate_env))

sys.path.insert(0,os.path.dirname(__file__))

from server import init_app
application = init_app()
