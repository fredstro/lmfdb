# -*- coding: utf-8 -*-
#*****************************************************************************
#  Copyright (C) 2010
#  Fredrik Strömberg <fredrik314@gmail.com>,
#  Stephan Ehlen <stephan.j.ehlen@gmail.com>
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
Classes for displaying Maass waveforms on the web.

AUTHORS:

 - Fredrik Stroemberg

 
"""

from lmfdb.modular_forms.elliptic_modular_forms.backend.web_object import (
     WebObject,
     WebInt,
     WebBool,
     WebStr,
     WebFloat,
     WebDict,
     WebList,
     WebSageObject,
     WebNoStoreObject,
     WebPoly,
     WebProperty,
     WebProperties,
     WebNumberField,     
     )
from sage.all import (
     ZZ,
     Gamma0,
     Gamma1,
     RealField,
     ComplexField,
     prime_range,
     join,
     ceil,
     RR,
     Integer,
     matrix,
     PowerSeriesRing,
     Matrix,
     vector,
     latex,
     primes_first_n,
     loads,
     dumps
     )
from sage.structure.unique_representation import CachedRepresentation

class WebMaassFormSpace:
    pass


class WebMaassForm(WebObject, CachedRepresentation):
    r"""


    """

    def __init__(self,eigenvalue,group,character=1, update_from_db=True):
        r"""

        """
        ## make a kind of unique label
        N = group.level()
        R = float(eigenvalue)
        
        label = "{0:0>4}-{1:0>10.6f}-{2:0>7.5f}-{3:0>7.5f}-{4:0>7.5f}-{5:0>7.5f}".format(N,R,c2r,c2i,c3r,c3i)
        self._properties = WebProperties(
            WebInt('level', value=level),
            WebFloat('weight',value=weight),
            WebFloat('eigenvalue',value=float(eigenvalue)),
            WebStr('eigenvalue_mp',value=''),
            WebInt('symmetry',value=sym_type),
            WebInt('M0'),
            WebInt('Y'),
            WebBool('is_exceptional'))         
            
            

            
        
        super(WebNewForm, self).__init__(
            update_from_db=update_from_db
            )
