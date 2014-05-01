# -*- coding: utf-8 -*-
#*****************************************************************************
#  Copyright (C) 2010 Fredrik Strömberg <fredrik314@gmail.com>,
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************
r"""
Main file for viewing subgroups of the modular group

AUTHOR: Fredrik Strömberg

"""

import flask
from flask import render_template, url_for, request, redirect, make_response, send_file, send_from_directory
from sage.misc.latex import latex 
from lmfdb.base import app

from lmfdb.psl2z_subgroups import PSG,PSG_TOP,psg,db,psg_logger
from lmfdb.psl2z_subgroups.backend.psg_schema import PSL2Zsubgroup,Signature_class
from lmfdb.psl2z_subgroups.backend.psg_utils import is_consistent_signature,get_signature,build_signature_query,render_plot


@psg.context_processor
def body_class():
    return {'body_class': PSG}

def get_named(value):
    return filter(lambda x:x.name<>'',value)

def my_latex(x):
    print x,type(x)
    return latex(x)
app.jinja_env.filters['get_named']=get_named
app.jinja_env.filters['latex']=my_latex #  lambda x : latex(x)

met = ['GET', 'POST']

@psg.route("/", methods=met)
@psg.route("/<int:index>/", methods=met)
@psg.route("/<int:index>/<int:nu>/", methods=met)
@psg.route("/<int:index>/<int:nu>/<int:e2>/", methods=met)
@psg.route("/<int:index>/<int:nu>/<int:e2>/<int:e3>/", methods=met)
@psg.route("/<int:index>/<int:nu>/<int:e2>/<int:e3>/<int:genus>/", methods=met)
def browse_subgroups(**kwds):
    signature = get_signature(request,**kwds)
    print "request=",request
    print "signature=",signature
    #print "index=",index,type(index)
    print "args={0}".format(request.args)
    print "forms={0}".format(request.form)
    print "kwds=",kwds
    psg_logger.debug("args={0}".format(request.args))
    psg_logger.debug("args={0}".format(request.form))
    psg_logger.debug("met={0}".format(request.method))
    #psg_logger.debug("index=".format(index))   
    
    title = "Browse Subgroups"
    bread = [(PSG_TOP, url_for('psl2zsubg.browse_subgroups'))]
    #results = PSL2Zsubgroup.query.filter_by(psl2z_index=int(index))
    info = {}
    info['data'] = {'signature':signature}
    info['signatures'] = build_signature_query(signature)
    if info['signatures'].count()==0:
        ## Let's check if the signature is at all consistent.
        info['is_consistent'] = is_consistent_signature(signature)
    #Signature_class.query.filter_by(psl2z_index=int(index))
    #for r in results:
    #    info['data'].append(r)
    #if index>0:
    #    return navigate_groups(index)
    #info = {'paginate':db.paginate()}
    return render_template("psg_navigation.html", info=info, title=title, bread=bread)


def navigate_groups(info,title,bread):
    return render_template("psg_navigation.html", info=info, title=title, bread=bread)

# This is how we specify a group completely.
@psg.route("/<int:index>/<int:nu>/<int:e2>/<int:e3>/<int:genus>/<int:gid>", methods=met)
def show_one_group(**kwds):
    print "kwds=",kwds
    q = PSL2Zsubgroup.query.filter_by(id=kwds.get('gid',0))
    info = kwds
    if q.count() == 0:
        info['error'] = 'There is no subgroup with index {0} in the database!'
    else:
        g = q.one()
    title = "Show one subgroup"
    info['g']=g
    info['fd_plot_url'] = url_for('psg.render_plot', gid=gid)
    bread = [(PSG_TOP, url_for('psl2zsubg.browse_subgroups'))]
    return render_template("psg_one_group.html", info=info, title=title, bread=bread)        
        

@psg.route("/Plots/<int:gid>/",methods=met)
def render_plot(**kwds):
    q = PSL2Zsubgroup.query.filter_by(id=kwds.get('gid',0))
    info = kwds
    if q.count() == 0:
        info['error'] = 'There is no subgroup with index {0} in the database!'
    else:
        g = q.one()
    domain = render_plot(g,type=0)
    if isinstance(domain, sage.plot.plot.Graphics):
        psg_logger.debug('Got a Graphics object')
        _, filename = tempfile.mkstemp('.png')
        domain.save(filename)
        data = open(filename).read()
        os.unlink(filename)
    else:
        data = domain
    response = make_response(data)
    response.headers['Content-type'] = 'image/png'
    return response
