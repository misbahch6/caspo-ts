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

import json
from zope import component, interface

from pyzcasp import asp

from interfaces import *
from impl import *

class Gringo3(asp.Process):
    interface.implements(IGringo3)

class Gringo4(asp.Process):
    interface.implements(IGringo4)
    
class ClaspSolver(asp.Process):
    interface.implements(IClaspSolver)
    
    def __init__(self, prg, allowed_returncodes = [10,20,30], strict_args=None):
        if strict_args:
            strict_args.update({'--outf': 2})
        else:
            strict_args = {'--outf': 2}
            
        super(ClaspSolver, self).__init__(prg, allowed_returncodes, strict_args)
        
    def execute(self, stdin, *args):
        try:
            stdout, code = super(ClaspSolver, self).execute(stdin, *args)
            self.json = json.loads(stdout)
                        
        except asp.ProcessError as e:
            if e.code == 11: # INTERRUPTED
                stdout = e.stdout
                code = e.code
                self.json = json.loads(stdout)
            else:
                raise e
        
        return stdout, code
                
    def answers(self):
        raise NotImplementedError("iterator over answer sets depends on specific solver series output")
        
    @property
    def unknown(self):
        return self.json['Result'] == "UNKNOWN"
        
    @property
    def unsat(self):
        return self.json['Result'] == "UNSATISFIABLE"
        
    @property
    def sat(self):
        return self.json['Result'] == "SATISFIABLE"
        
    @property
    def optimum(self):
        return self.json['Result'] == "OPTIMUM FOUND"
        
    @property
    def complete(self):
        raise NotImplementedError("complete property depends on specific solver series output")
            
class Clasp2(ClaspSolver):
    interface.implements(IClasp2)

    @property
    def complete(self):
        return self.__getstats__()['Complete'] == "yes"

    def answers(self):
        witnesses = self.__getwitnesses__()
        if witnesses:          
            for answer in witnesses:
                atoms = self.__filteratoms__(self.__getatoms__(answer))
                score = self.__getscore__(answer)
                if score:
                    ans = asp.AnswerSet(atoms, score)
                else:
                    ans = asp.AnswerSet(atoms)
            
                yield ans
    
    def __filteratoms__(self, atoms):
        return atoms
        
    def __getwitnesses__(self):
        if 'Witnesses' not in self.json:
            return
        else:
            return self.json['Witnesses']
                        
    def __getstats__(self):
        return self.json['Stats']
        
    def __getatoms__(self, answer):
        stats = self.__getstats__()
        
        if 'Brave' in stats:
            return answer['Brave']
        elif 'Cautious' in stats:
            return answer['Cautious']
        else:    
            return answer['Value']
            
    def __getscore__(self, answer):
        if 'Opt' in answer:
            return answer['Opt']
                
class HClasp(Clasp2):
    interface.implements(IHClasp, ISubsetMinimalSolver)
    
    def __filteratoms__(self, atoms):
        return filter(lambda atom: not atom.startswith('_'), atoms)
    
class ClaspD(Clasp2):
    interface.implements(IClaspD, ISubsetMinimalSolver)
    
    def __getstats__(self):
        return self.json['Models']

class Clasp3(ClaspSolver):
    interface.implements(IClasp3, IHeuristicSolver, IDisjunctiveSolver)

    @property
    def complete(self):
        return self.json['Models']['More'] == "no"
        
    @property
    def calls(self):
        return self.json['Calls']

    def answers(self):
        for call in xrange(self.calls):
            witnesses = self.__getwitnesses__(call)
            if witnesses:
                for answer in witnesses:
                    atoms = answer['Value'] if 'Value' in answer else []
                    score = answer['Costs'] if 'Costs' in answer else None
                    if score:
                        ans = asp.AnswerSet(atoms, score)
                    else:
                        ans = asp.AnswerSet(atoms)
            
                    yield ans

    def __getwitnesses__(self, call=None):
        if call == None:
            call = self.calls -  1
            
        if 'Witnesses' not in self.json['Call'][call]:
            return
        else:
            return self.json['Call'][call]['Witnesses']
       
class Clingo(Clasp3):
    interface.implements(IClingo)
    
    def __init__(self, prg, allowed_returncodes = [10,20,30], strict_args=None):
        if strict_args:
            strict_args.update({'--mode': 'clingo'})
        else:
            strict_args = {'--mode': 'clingo'}
            
        super(Clingo, self).__init__(prg, allowed_returncodes, strict_args)
        self.grounder = Gringo4(prg, allowed_returncodes = [0,10], strict_args={'--mode': 'gringo'})
        self.solver = self
        
    def run(self, lp="", grounder_args=[], solver_args=[], adapter=None, termset_filter=None):
        if lp and '-' not in grounder_args:
            grounder_args.append('-')
        
        clingo_args = grounder_args + solver_args
        self.execute(lp, *clingo_args)
        
        return asp.IAnswerSetsProcessing(self.solver).processing(adapter, termset_filter)
