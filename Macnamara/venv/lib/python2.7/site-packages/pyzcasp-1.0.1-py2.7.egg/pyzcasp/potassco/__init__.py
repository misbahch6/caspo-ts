# Copyright (c) 2014, Santiago Videla
#
# This file is part of pyzcasp.
#
# caspo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caspo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-
import os

from adapters import *
from interfaces import *
from utilities import *

from pyzcasp import asp
from zope import component

gsm = component.getGlobalSiteManager()

gsm.registerAdapter(MetaAnswerSet2TermSet)
gsm.registerAdapter(MetaGrounderSolver, name='metasp')

root = os.path.dirname(__file__)
reg = component.getUtility(asp.IEncodingRegistry)
reg.register('potassco.meta',  os.path.join(root, 'encodings/meta.lp'),  IGringo3)
reg.register('potassco.metaD', os.path.join(root, 'encodings/metaD.lp'), IGringo3)
reg.register('potassco.metaO', os.path.join(root, 'encodings/metaO.lp'), IGringo3)

def configure(**kwargs):
    gsm = component.getGlobalSiteManager()
    if 'gringo3' in kwargs:
        gsm.registerUtility(Gringo3(kwargs['gringo3']), IGringo3)
        
    if 'gringo4' in kwargs:
        gsm.registerUtility(Gringo4(kwargs['gringo4']), IGringo4)

    if 'clasp2' in kwargs:
        gsm.registerUtility(Clasp2(kwargs['clasp2']),   IClasp2)
    
    if 'hclasp' in kwargs:
        gsm.registerUtility(HClasp(kwargs['hclasp']),   IHClasp)
        
    if 'claspD' in kwargs:
        gsm.registerUtility(ClaspD(kwargs['claspD']),   IClaspD)

    if 'clasp3' in kwargs:
        gsm.registerUtility(Clasp3(kwargs['clasp3']),   IClasp3)
    
    if 'clingo' in kwargs:
        gsm.registerUtility(Clingo(kwargs['clingo']),   IClingo)
