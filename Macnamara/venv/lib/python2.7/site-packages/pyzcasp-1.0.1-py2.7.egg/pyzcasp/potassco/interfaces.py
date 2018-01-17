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

from zope import interface
from pyzcasp import asp

class IGringoGrounder(asp.IGrounder):
    """
    gringo grounder
    """
    
class IGringo3(IGringoGrounder):
    """
    gringo 3 grounder
    """

class IGringo4(IGringoGrounder):
    """
    gringo 4 grounder
    """

class IClaspSolver(asp.ISolver):
    """
    clasp solver
    """

class IClasp2(IClaspSolver):
    """
    clasp 2 series
    """
    
    def __filteratoms__(self, atoms):
        """
        Return atoms after filter
        """

    def __getwitnesses__(self):
        """
        Return answer sets witnesses
        """
        
    def __getstats__(self):
        """
        Return solver stats
        """
        
    def __getatoms__(self, answer):
        """
        Return answer set atoms
        """
        
    def __getscore__(self, answer):
        """
        Return answer set score(s)
        """
    
class IClasp3(IClaspSolver):
    """
    clasp 3 series
    """
    
    calls = interface.Attribute("Number of solving calls")
    
class IHeuristicSolver(IClaspSolver):
    """
    domain heuristic solver
    """

class IDisjunctiveSolver(IClaspSolver):
    """
    disjunctive solver
    """

class IHClasp(IHeuristicSolver):
    """
    hclasp solver
    """
    
class IClaspD(IDisjunctiveSolver):
    """
    claspD solver
    """
    
class ISubsetMinimalSolver(asp.ISubsetMinimalSolver):
    """
    Marker interface for clasp subset minimal solver
    """
    
class IMetaAnswerSet(asp.IAnswerSet):
    """
    """

class IMetaGrounderSolver(asp.IGrounderSolver):
    """
    """
    
    optimize = interface.Attribute("Optimization method as expected by metasp encodings")

class IGrounderSolver(asp.IGrounderSolver):
    """
    Marker interface for Potassco grounder & solver
    """
    
class IClingo(IGrounderSolver):
    """
    clingo solver (grounder included)
    """
    