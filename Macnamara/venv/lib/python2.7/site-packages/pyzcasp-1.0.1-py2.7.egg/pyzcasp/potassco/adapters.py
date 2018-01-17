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
from zope import component, interface
from pyzcasp import asp
from interfaces import *
from impl import *

class MetaAnswerSet2TermSet(asp.TermSetAdapter):
    component.adapts(IMetaAnswerSet)
    
    def __init__(self, answer):
        super(MetaAnswerSet2TermSet, self).__init__()
        
        parser = asp.Grammar()
        for atom in answer.atoms:
            # raise pyparsing.ParseException if cannot parse
            meta = parser.parse(atom)
            self._termset.add(meta.arg(0).arg(0))

        self._termset.score = answer.score
        
class MetaGrounderSolver(object):
    component.adapts(IGringo3, IDisjunctiveSolver)
    interface.implements(IMetaGrounderSolver)
    
    def __init__(self, grounder, solver):
        super(MetaGrounderSolver, self).__init__()
        self.solver   = solver
        self.grounder = grounder
        self.optimize = asp.TermSet()
        
    def run(self, lp="", grounder_args=[], solver_args=[], adapter=None, termset_filter=None):
        if '--reify' not in grounder_args:
            grounder_args.append('--reify')
            
        grounding, code = self.grounder.execute("", *grounder_args)
                
        encodings = component.getUtility(asp.IEncodingRegistry).encodings(self.grounder)
        meta = encodings('potassco.meta')
        metaD = encodings('potassco.metaD')
        metaO = encodings('potassco.metaO')
        
        metasp = ['-', meta, metaD, metaO, self.optimize.to_file()]        
        grounding, code = self.grounder.execute(grounding + lp, *metasp)
        self.solver.execute(grounding, *solver_args)
        
        ans = []
        for answer in self.solver.answers():
            interface.directlyProvides(answer, IMetaAnswerSet)
            if adapter:
                ans.append(adapter(answer))
            else:
                ts = asp.ITermSet(answer)
                if termset_filter:
                    ts = asp.TermSet(filter(termset_filter, ts), ts.score)
                    
                ans.append(ts)

        return ans
