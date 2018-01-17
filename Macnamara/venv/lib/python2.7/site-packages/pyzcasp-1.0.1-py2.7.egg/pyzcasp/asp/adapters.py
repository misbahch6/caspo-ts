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

from zope import component

import re, os

from interfaces import *
from impl import *

class TermSetAdapter(object):
    interface.implements(ITermSet)
    
    def __init__(self):
        super(TermSetAdapter, self).__init__()
        self._termset = TermSet()

    @property
    def score(self):
        return self._termset.score
        
    def add(self, term):
        self._termset.add(term)
    
    def union(self, other):
        return self._termset.union(other)
                
    def to_str(self, pprint=False):
        return self._termset.to_str(pprint)
        
    def to_file(self, filename=None, pprint=False):
        return self._termset.to_file(filename, pprint)
        
    def pprint(self):
        self._termset.pprint()
            
    def __iter__(self):
        return iter(self._termset)
        
    def __len__(self):
        return len(self._termset)
        
class AnswerSet2TermSet(TermSetAdapter):
    component.adapts(IAnswerSet)
    
    def __init__(self, answer):
        super(AnswerSet2TermSet, self).__init__()
        parser = Grammar()
        
        for atom in answer.atoms:
            # raise pyparsing.ParseException if cannot parse
            self._termset.add(parser.parse(atom))
        
        self._termset.score = answer.score

class GrounderSolver(object):
    interface.implements(IGrounderSolver)
    component.adapts(IGrounder, ISolver)

    def __init__(self, grounder, solver):
        super(GrounderSolver, self).__init__()
        self.grounder = grounder
        self.solver = solver
        
    def run(self, lp="", grounder_args=[], solver_args=[], adapter=None, termset_filter=None):
        if lp and '-' not in grounder_args:
            grounder_args.append('-')
            
        grounding, code = self.grounder.execute(lp, *grounder_args)
        self.solver.execute(grounding, *solver_args)
        
        return IAnswerSetsProcessing(self.solver).processing(adapter, termset_filter)
        
class AnswerSetsProcessing(object):
    component.adapts(ISolver)
    interface.implements(IAnswerSetsProcessing)
    
    def __init__(self, solver):
        self.solver = solver
        
    def processing(self, adapter=None, termset_filter=None):
        ans = []
        for answer in self.solver.answers():
            if adapter:
                ans.append(adapter(answer))
            else:
                ts = ITermSet(answer)
                if termset_filter:
                    ts = TermSet(filter(termset_filter, ts), ts.score)
                    
                ans.append(ts)

        return ans
