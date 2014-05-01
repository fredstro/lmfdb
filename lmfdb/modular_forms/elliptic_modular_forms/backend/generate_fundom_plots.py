
import pymongo
from sage.all import dumps, save, parallel
from modular_forms.elliptic_modular_forms.backend.plot_dom import *
from lmfdb.website import dbport
C = pymongo.connection.Connection(port=dbport)
C = pymongo.connection.Connection(port=dbport)
from bson.binary import Binary

@parallel
def generate_fundom_plots(N, group='Gamma0'):
    gps = C['SL2Zsubgroups']['groups']
    if group == 'Gamma0':
        G = Gamma0(N)
        grouptype = int(0)
    else:
        G = Gamma1(N)
        grouptype = int(1)
    dom = draw_fundamental_domain(N, group)
    filename = 'domain' + str(N) + '.png'
    save(dom, filename)
    data = open(filename).read()
    idins = gps.insert({'level': int(N), 'index': int(G.index(
    )), 'G': Binary(dumps(G)), 'domain': Binary(data), 'type': grouptype})
    print "inserted: ", N, " ", idins
