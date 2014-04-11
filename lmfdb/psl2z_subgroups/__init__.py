import lmfdb.utils as utils
import flask
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

from lmfdb.base import app
#from sl2z_subgroups import PSL2Zsubgroup

## Some common definitions to use in this module.
psg_version = 1.0
PSG_TOP = "Subgroups of $PSL(2,Z)$"  # The name to use for the top of this catergory
PSG = "psl2zsubg"  # The current blueprint name
psg = flask.Blueprint(PSG, __name__, template_folder="views/templates", static_folder="views/static")
psg_logger = utils.make_logger(psg)

#filen = inspect.getabsfile(inspect.currentframe())
#datadir = "/".join(os.path.dirname(filen).rsplit("/")[0:-1]+["data"])
datadir = "/home/pmzfs/Devel/noncongruence/data/"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{0}/groups3.sqlite'.format(datadir)
db = SQLAlchemy(app)

import views
import backend
from views import browse_subgroups, navigate_groups
app.register_blueprint(psg, url_prefix="/Subgroups/")
