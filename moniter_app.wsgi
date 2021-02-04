#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
#sys.path.insert(0,"/home/schsysadmin/.local/lib/python3.6/site-packages/pandas/")
sys.path.insert(0,"/var/www/moniter_app/")
#import pandas
#from flask import Flask
#raise NameError(sys.path)

from moniter_app import app as application
application.secret_key = 'school construction progress moniter'
