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

import json, subprocess, os
from itertools import chain

from zope import component

from interfaces import *
from impl import *
        
class Process(object):
    interface.implements(IProcess)
    
    def __init__(self, prg, allowed_returncodes = [0], strict_args=None):
        self.prg = prg
        self.allowed_returncodes = allowed_returncodes
        self.strict_args = strict_args or dict()
        
    def execute(self, stdin, *args):
        largs = list(args)
        for strict, value in self.strict_args.iteritems():
            largs = filter(lambda arg: not arg.startswith(strict), largs)
            if value:
                largs.append("{0}={1}".format(strict, value))
            else:
                largs.append(strict)
            
        args = list(chain.from_iterable(map(lambda arg: arg.split(), largs)))
        try:
            self.__popen = subprocess.Popen([self.prg] + args, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                
        except OSError, e:
            if e.errno == 2:
                raise Exception('Program \'%s\' not found' % self.prg)
            else: 
                raise e
                
        (stdout, stderr) = self.__popen.communicate(stdin)
        returncode = self.__popen.returncode
        if returncode not in self.allowed_returncodes:
            raise ProcessError(self.prg, returncode, stdout, stderr)
    
        return stdout, returncode

class Solver(Process):
    interface.implements(ISolver)
    
    def answers(self):
        raise NotImplementedError("This is an abstract solver")

class Grounder(Process):
    interface.implements(IGrounder)

class EncodingRegistry(object):
    interface.implements(IEncodingRegistry)
    
    def __init__(self):
        super(EncodingRegistry, self).__init__()
    
    def register(self, name, path, igrounder):
        if not os.path.isfile(path):
            raise IOError("File not found: %s" % path)

        @interface.implementer(IEncoding)
        @component.adapter(igrounder)
        def encoding(grounder):
            return path
            
        gsm = component.getGlobalSiteManager()    
        gsm.registerAdapter(encoding, (igrounder,), IEncoding, name)

    def encodings(self, grounder):
        return lambda name: component.getAdapter(grounder, IEncoding, name=name)

class ArgumentRegistry(object):
    interface.implements(IArgumentRegistry)
    
    def __init__(self):
        super(ArgumentRegistry, self).__init__()
    
    def register(self, name, args, iprocess):
        @interface.implementer(IArgument)
        @component.adapter(iprocess)
        def argument(process):
            return args
            
        gsm = component.getGlobalSiteManager()    
        gsm.registerAdapter(argument, (iprocess,), IArgument, name)

    def arguments(self, process):
        return lambda name: component.getAdapter(process, IArgument, name=name)

class Cleaner(object):
    interface.implements(ICleaner)
    
    def __init__(self):
        super(Cleaner, self).__init__()
        self.__files = set()
        
    def collect_file(self, filename):
        self.__files.add(filename)
    
    def clean_files(self):
        while self.__files:
            filename = self.__files.pop()
            if os.path.isfile(filename):
                os.unlink(filename)
