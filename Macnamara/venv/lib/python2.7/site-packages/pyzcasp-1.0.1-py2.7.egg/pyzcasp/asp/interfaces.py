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

class ITerm(interface.Interface):
    """
    Represents a term as a function symbol followed by a list of arguments.
    String arguments are automatically escaped, e.g. 'a' becomes '"a"' in order
    to avoid conlfict with uppercase strings. To avoid this, use an instance
    of NativeTerm. Number arguments must be integers.
    """
    
    pred = interface.Attribute("Term predicate name")
    args = interface.Attribute("Term arguments list")
    
    def __init__(self, predicate, arguments=[]):
        """
        Constructor
        
        :param str predicate: term name
        :param list arguments: list of arguments
        """
            
    def __str__(self):
        """
        Term as string
        """
        
    def __repr__(self):
        """
        Term object representation
        """
        
    def __eq__(self, other):
        """
        Compare by pred and args
        """

    def __ne__(self, other):
        """
        Compare by pred and args
        """
        
    def __hash__(self):
        """
        Hash by ([pred] + args)
        """
    
class ITermSet(interface.Interface):
    """
    Represents a set of terms objects. Typically used to describe an input instance
    and resulting answer sets.
    """
    
    score = interface.Attribute("List of score(s) if any")
    
    def __init__(self, terms=[], score=None):
        """
        Constructor
        
        :param list terms: list of terms objects
        :param list score: list of score(s)
        """
    
    def to_str(self, pprint=False):
        """
        Returns all terms converted to strings ending with a dot.
        
        :param boolean pprint: use pretty print.
        :returns: the str of all terms.
        """
    
    def to_file(self, filename=None, pprint=False):
        """
        Write terms to filename or temp file. If filename==None, the filename is collected
        in the ICleaner utility for a proper cleaning using @cleanrun decorator.
        
        :param str filename: an optional filename.
        :returns: a file descriptor object.
        """
        
    def pprint(self):
        """
        Simple pretty print user for debugging logic instances.
        
        :returns: a str formatted with appropriate tabs and breaklines.
        """
    
    def add(self, term):
        """
        Adds a term to the TermSet
        
        :param Term term: a Term object
        """
        
    def union(self, other):
        """
        Returns the union of self and other TermSet
        
        :param TermSet other: other TermSet object
        """
        
    def __iter__(self):
        """
        Return an iterator over terms
        """
        
    def __len__(self):
        """
        Return number of terms in the TermSet
        """
            
class IGrammar(interface.Interface):
    """
    Grammar pyparsing object
    """
    
    function = interface.Attribute("token object for a function (including constant). Resulting object has 'pred' (str) and 'args' (list) keywords")
    integer = interface.Attribute("token object for an integer")
    term = interface.Attribute("token object for term: function, integer or quoted string")
    
    def parse(self, atom, parseAll=True):
        """
        Parse an atom using self.term.parseString
        
        :param str atom: string representation of an atom (more precisely, a term)
        :param bool parseAll: True to force parsing all the string, False otherwise
        
        :return: by default a Term object. It may change if you modify use setParseAction
        """
    
class IProcess(interface.Interface):
    """
    Represents a program to be executed using system calls
    """

    def __init__(self, prg, allowed_returncodes = [0], strict_args=None):
        """
        Constructor
        
        :param str prg: excutable command
        :param list allowed_returncodes: list of allowed code by `prg`
        :param dict strict_args: mapping of fixed arguments
        """
        
    def execute(self, stdin, *args):
        """
        Execute the program via a system call.
        An Exception is raised if the `prg` is not found. A ProcessError exception is raised
        if the returned code is not in the allowed_returncodes.
        
        :param str stdin: a valid input for `prg`
        :param list *args: any accepted argument by `prg`
        
        :returns: tuple with standard output from `prg` and its returned code
        """

class IGrounder(IProcess):
    """
    Represents an ASP grounder program
    """
    
class ISolver(IProcess):
    """
    Represents an ASP solver program
    """
    
    complete = interface.Attribute("True if the solving was completed, False otherwise")
    unknown = interface.Attribute("True if SAT is unknown, False otherwise")
    unsat = interface.Attribute("True if the solving was UNSAT, False otherwise")
    sat = interface.Attribute("True if the solving was SAT, False otherwise")
    optimum = interface.Attribute("True if the solving found an optimum, False otherwise")
    
    def answers(self):
        """
        Iterator over AnswerSet objects
        """
        
class ISubsetMinimalSolver(interface.Interface):
    """
    Marker interface for subset minimal solver
    """
    
class IAnswerSet(interface.Interface):
    """
    An plain answer set
    """
    
    atoms = interface.Attribute("Atoms as strings")
    score = interface.Attribute("Answer set scores or costs")
    
class IGrounderSolver(interface.Interface):
    """
    Ground, solve and parse to TermSet
    """
    
    grounder = interface.Attribute("Grounder")
    solver = interface.Attribute("Solver")

    def run(self, lp="", grounder_args=[], solver_args=[], adapter=None, termset_filter=None):
        """"""
        
    def processing(self, answers, adapter=None, termset_filter=None):
        """"""
        
class IAnswerSetsProcessing(interface.Interface):
    """
    Post-processing for raw answer sets
    """
    
    solver = interface.Attribute("Solver to get the answers")
    
    def processing(self, adapter=None, termset_filter=None):
        """"
        :param Interface adapter: interface to adapt AnswerSet objects. If none ITermSet is used
        :param callable termset_filter: callable to filter termsets if no adapter == None
        
        :return: either a list of (filtered) ITermSet objects or list of adaptee object providing `adapter` interface
        """

class IEncodingRegistry(interface.Interface):
    """
    Registry of ASP encodings
    """
    
    def register(self, name, path, igrounder):
        """
        Register an encoding by name
        
        :param str name: the name to identify the encoding
        :param str path: full path to encoding file
        :param IGrounder igrounder: grounder type for the encoding, e.g., IGringo3 or IGringo4
        """
        
    def encodings(self, igrounder):
        """
        Return a function to get encodings paths registered for a given grounder
        
        :param IGrounder igrounder: grounder type
        :return: a function to be called with an encoding name as only parameter. It returns the registered path
        """

class IEncoding(interface.Interface):
    """
    Marker interface for encodings
    """
    

class IArgumentRegistry(interface.Interface):
    """
    Registry for process arguments
    """
    
    def register(self, name, args, iprocess):
        """
        Register a list of arguments by name
        
        :param str name: the name to identify the list of args
        :param list args: the list of arguments
        :param IProcess iprocess: process type, e.g., IClasp2 or IClasp3
        """
        
    def arguments(self, iprocess):
        """
        Return a function to get arguments registered for a given process
        
        :param IProcess iprocess: process type, e.g., IClasp2 or IClasp3
        :return: a function to be called with an arguments name as only parameter. It returns the registered list of arguments
        """

class IArgument(interface.Interface):
    """
    Marker interface for a process argument
    """
    
class ICleaner(interface.Interface):
    """
    Cleaner for tmp files generated during grounding&solving
    """
    
    def collect_file(self, filename):
        """
        Collect a tmp file to be deleted afterwards
        """
        
    def clean_files(self):
        """
        Remove all collected file since last call
        """
        
class IProcessError(interface.Interface):
    """
    Exception used by Process
    """
    
    prg = interface.Attribute("")
    code = interface.Attribute("")
    stdout = interface.Attribute("")
    stderr = interface.Attribute("")
