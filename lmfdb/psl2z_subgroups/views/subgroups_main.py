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


from lmfdb.psl2z_subgroups import PSG,PSG_TOP,psg,db,psg_logger
from lmfdb.psl2z_subgroups.backend.psg_schema import PSL2Zsubgroup


@psg.context_processor
def body_class():
    return {'body_class': PSG}



met = ['GET', 'POST']

@psg.route("/", methods=met)
@psg.route("/<int:index>/", methods=met)
def browse_subgroups(index=0,**kwds):
    index = request.args.get('index',kwds.get('index',index))
    print "request=",request
    print "index=",index
    print "args={0}".format(request.args)
    print "forms={0}".format(request.form)
    print "kwds=",kwds
    psg_logger.debug("args={0}".format(request.args))
    psg_logger.debug("args={0}".format(request.form))
    psg_logger.debug("met={0}".format(request.method))
    psg_logger.debug("index=".format(index))
    
    
    title = "Browse Subgroups"
    bread = [(PSG_TOP, url_for('psl2zsubg.browse_subgroups'))]
    results = PSL2Zsubgroup.query.filter_by(psl2z_index=int(index))
    info = {}
    info['data'] = []
    for r in results:
        info['data'].append(r)
    #if index>0:
    #    return navigate_groups(index)
    #info = {'paginate':db.paginate()}
    return render_template("psg_navigation.html", info=info, title=title, bread=bread)


def navigate_groups(info,title,bread):
    return render_template("psg_navigation.html", info=info, title=title, bread=bread)



