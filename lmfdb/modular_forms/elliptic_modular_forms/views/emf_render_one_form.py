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
Routines for rendering webpages for holomorphic modular forms on GL(2,Q)

AUTHORS:
 - Fredrik Strömberg
 - Stephan Ehlen

"""
from flask import render_template, url_for, request, redirect, make_response, send_file
import tempfile
import os
import re
from lmfdb.utils import ajax_more, ajax_result, make_logger
from sage.all import *
from sage.modular.dirichlet import DirichletGroup
from lmfdb.base import app, db
from lmfdb.modular_forms.elliptic_modular_forms.backend.web_modforms import WebNewForm
from lmfdb.modular_forms.elliptic_modular_forms.backend.web_modform_space import WebModFormSpace
from lmfdb.modular_forms.elliptic_modular_forms.backend.emf_classes import ClassicalMFDisplay, DimensionTable
from lmfdb.modular_forms import MF_TOP
from lmfdb.modular_forms.backend.mf_utils import my_get
from lmfdb.modular_forms.elliptic_modular_forms.backend.emf_core import *
from lmfdb.modular_forms.elliptic_modular_forms.backend.emf_utils import *
from lmfdb.modular_forms.elliptic_modular_forms.backend.plot_dom import *
from lmfdb.modular_forms.elliptic_modular_forms import EMF, emf_logger, emf, default_prec, default_bprec, default_display_bprec,EMF_TOP, N_max_extra_comp, N_max_comp, N_max_db, k_max_db, k_max_comp


def render_one_elliptic_modular_form(level, weight, character, label, **kwds):
    r"""
    Renders the webpage for one elliptic modular form.

    """
    citation = ['Sage:' + version()]
    info = set_info_for_one_modular_form(level, weight,
                                         character, label, **kwds)
    emf_logger.debug("info={0}".format(info))
    err = info.get('error', '')
    ## Check if we want to download either file of the function or Fourier coefficients
    if 'download' in info and 'error' not in info:
        return send_file(info['tempfile'], as_attachment=True, attachment_filename=info['filename'])
    return render_template("emf.html", **info)


def set_info_for_one_modular_form(level=None, weight=None, character=None, label=None, **kwds):
    r"""
    Set the info for on modular form.

    """
    info = to_dict(kwds)
    info['level'] = level
    info['weight'] = weight
    info['character'] = character
    info['label'] = label
    if level is None or weight is None or character is None or label is None:
        s = "In set info for one form but do not have enough args!"
        s += "level={0},weight={1},character={2},label={3}".format(level, weight, character, label)
        emf_logger.critical(s)
    emf_logger.debug("In set_info_for_one_mf: info={0}".format(info))
    prec = my_get(info, 'prec', default_prec, int)
    bprec = my_get(info, 'bprec', default_display_bprec, int)
    emf_logger.debug("PREC: {0}".format(prec))
    emf_logger.debug("BITPREC: {0}".format(bprec))    
    try:
        WNF = WebNewForm(N=level,k=weight, chi=character, label=label, verbose=1)
        # if info.has_key('download') and info.has_key('tempfile'):
        #     WNF._save_to_file(info['tempfile'])
        #     info['filename']=str(weight)+'-'+str(level)+'-'+str(character)+'-'+label+'.sobj'
        #     return info
    except IndexError as e:
        WNF = None
        info['error'] = e.message
    url1 = url_for("emf.render_elliptic_modular_forms")
    url2 = url_for("emf.render_elliptic_modular_forms", level=level)
    url3 = url_for("emf.render_elliptic_modular_forms", level=level, weight=weight)
    url4 = url_for("emf.render_elliptic_modular_forms", level=level, weight=weight, character=character)
    bread = [(EMF_TOP, url1)]
    bread.append(("of level %s" % level, url2))
    bread.append(("weight %s" % weight, url3))
    if int(character) == 0:
        bread.append(("trivial character", url4))
    else:
        bread.append(("\( %s \)" % (WNF.character().latex_name()), url4))
    info['bread'] = bread
    
    properties2 = list()
    friends = list()
    space_url = url_for('emf.render_elliptic_modular_forms',level=level, weight=weight, character=character)
    friends.append(('\( S_{%s}(%s, %s)\)'%(WNF.weight(), WNF.level(), WNF.character().latex_name()), space_url))
    friends.append(('Number field ' + WNF.coefficient_field_label(), WNF.coefficient_field_url()))
    friends.append(('Number field ' + WNF.base_field_label(), WNF.base_field_url()))
    friends = uniq(friends)
    friends.append(("Dirichlet character \(" + WNF.character().latex_name() + "\)", WNF.character().url()))
    
    if hasattr(WNF,"dimension") and WNF.dimension()==0:
        info['error'] = "This space is empty!"

#    emf_logger.debug("WNF={0}".format(WNF))    

    #info['name'] = name
    info['title'] = 'Modular Form ' + WNF.name()
    
    if 'error' in info:
        return info
    # info['name']=WNF._name
    ## Until we have figured out how to do the embeddings correctly we don't display the Satake
    ## parameters for non-trivial characters....
    if WNF.degree()==1:
        info['satake'] = WNF.satake_parameters()
    info['qexp'] = ajax_more(WNF.q_expansion_latex,{'prec':10},{'prec':20},{'prec':100},{'prec':200})
    # info['qexp'] = WNF.q_expansion_latex(prec=prec)
    c_pol_st = str(WNF.polynomial(type='coefficient_field',format='str'))
    b_pol_st = str(WNF.polynomial(type='base_ring',format='str'))
    c_pol_ltx = str(WNF.polynomial(type='coefficient_field',format='latex'))
    b_pol_ltx = str(WNF.polynomial(type='base_ring',format='latex'))
    #print "c=",c_pol_ltx
    #print "b=",b_pol_ltx
    if c_pol_st <> 'x': ## Field is QQ
        if b_pol_st <> 'x' and WNF.relative_degree()>1:
            info['polynomial_st'] = 'where \({0}=0\) and \({1}=0\).'.format(c_pol_ltx,b_pol_ltx)
        else:
            info['polynomial_st'] = 'where \({0}=0\).'.format(c_pol_ltx)         
    else:
        info['polynomial_st'] = ''
    info['degree'] = int(WNF.degree())
    if WNF.degree()==1:
        info['is_rational'] = 1
    else:
        info['is_rational'] = 0
    # info['q_exp_embeddings'] = WNF.print_q_expansion_embeddings()
    # if(int(info['degree'])>1 and WNF.dimension()>1):
    #    s = 'One can embed it into \( \mathbb{C} \) as:'
        # bprec = 26
        # print s
    #    info['embeddings'] =  ajax_more2(WNF.print_q_expansion_embeddings,{'prec':[5,10,25,50],'bprec':[26,53,106]},text=['more coeffs.','higher precision'])
    # elif(int(info['degree'])>1):
    #    s = 'There are '+str(info['degree'])+' embeddings into \( \mathbb{C} \):'
        # bprec = 26
        # print s
    #    info['embeddings'] =  ajax_more2(WNF.print_q_expansion_embeddings,{'prec':[5,10,25,50],'bprec':[26,53,106]},text=['more coeffs.','higher precision'])
    # else:
    #    info['embeddings'] = ''
    emf_logger.debug("PREC2: {0}".format(prec))
    info['embeddings'] = WNF.q_expansion_embeddings(prec, bprec,format='latex')
    info['embeddings_len'] = len(info['embeddings'])
    properties2 = []
    if (ZZ(level)).is_squarefree():
        info['twist_info'] = WNF.twist_info()
        if isinstance(info['twist_info'], list) and len(info['twist_info'])>0:
            info['is_minimal'] = info['twist_info'][0]
            if(info['twist_info'][0]):
                s = '- Is minimal<br>'
            else:
                s = '- Is a twist of lower level<br>'
            properties2 = [('Twist info', s)]
    else:
        info['twist_info'] = 'Twist info currently not available.'
        properties2 = [('Twist info', 'not available')]
    args = list()
    for x in range(5, 200, 10):
        args.append({'digits': x})
    alev = None
    CM = WNF.cm_values()
    if CM is not None:
        if CM.has_key('tau') and len(CM['tau']) != 0:
            info['CM_values'] = CM
    CM = WNF.is_CM()
    info['is_cm'] = CM
    if(WNF.is_CM()) == None or len(WNF.is_CM()) == 0:
        s = '- Unknown (insufficient data)<br>'
    elif(WNF.is_CM()[0]):
        s = '- Is a CM-form<br>'
    else:
        s = '- Is not a CM-form<br>'
    properties2.append(('CM info', s))
    alev = WNF.atkin_lehner_eigenvalues()
    info['atkinlehner'] = None
    if isinstance(alev,dict) and len(alev.keys())>0 and level != 1:
        s1 = " Atkin-Lehner eigenvalues "
        s2 = ""
        for Q in alev.keys():
            s2 += "\( \omega_{ %s } \) : %s <br>" % (Q, alev[Q])
        properties2.append((s1, s2))
        emf_logger.debug("properties={0}".format(properties2))
        alev = WNF.atkin_lehner_eigenvalues_for_all_cusps()
        if isinstance(alev,dict) and len(alev.keys())>0:
            info['atkinlehner'] = list()
            for c in alev.keys():
                if(c == Cusp(Infinity)):
                    continue
                s = "\(" + latex(c) + "\)"
                Q = alev[c][0]
                ev = alev[c][1]
                info['atkinlehner'].append([Q, c, ev])
    if(level == 1):
        info['explicit_formulas'] = WNF.as_polynomial_in_E4_and_E6()
    cur_url = '?&level=' + str(level) + '&weight=' + str(weight) + '&character=' + str(character) + \
        '&label=' + str(label)
    if(len(WNF.parent().labels()) > 1):
        for label_other in WNF.parent().labels():
            if(label_other != label):
                s = 'Modular form '
                if character:
                    s = s + str(level) + '.' + str(weight) + '.' + str(character) + str(label_other)
                else:
                    s = s + str(level) + '.' + str(weight) + str(label_other)
                url = url_for('emf.render_elliptic_modular_forms', level=level,
                              weight=weight, character=character, label=label_other)
                friends.append((s, url))

    s = 'L-Function '
    if character:
        s = s + str(level) + '.' + str(weight) + '.' + str(character) + str(label)
    else:
        s = s + str(level) + '.' + str(weight) + str(label)
    # url =
    # "/L/ModularForm/GL2/Q/holomorphic?level=%s&weight=%s&character=%s&label=%s&number=%s"
    # %(level,weight,character,label,0)
    url = '/L' + url_for(
        'emf.render_elliptic_modular_forms', level=level, weight=weight, character=character, label=label)
    if WNF.degree() > 1:
        for h in range(WNF.degree()):
            s0 = s + ".{0}".format(h)
            url0 = url + "{0}/".format(h)
            friends.append((s0, url0))
    else:
        friends.append((s, url))
    # if there is an elliptic curve over Q associated to self we also list that
    if WNF.weight() == 2 and WNF.degree() == 1:
        llabel = str(level) + '.' + label
        s = 'Elliptic curve isogeny class ' + llabel
        url = '/EllipticCurve/Q/' + llabel
        friends.append((s, url))
    info['properties2'] = properties2
    info['friends'] = friends
    info['max_cn']=WNF.max_cn()
    return info

import flask


@emf.route("/Qexp/<int:level>/<int:weight>/<int:character>/<label>")
def get_qexp(level, weight, character, label, **kwds):
    emf_logger.debug(
        "get_qexp for: level={0},weight={1},character={2},label={3}".format(level, weight, character, label))
    prec = my_get(request.args, "prec", default_prec, int)
    if not arg:
        return flask.abort(404)
    try:
        WNF = WebNewForm(level, weight, chi=character, label=label, prec=prec, verbose=2)
        nc = max(prec, 5)
        c = WNF.print_q_expansion(nc)
        return c
    except Exception as e:
        return "<span style='color:red;'>ERROR: %s</span>" % e.message
