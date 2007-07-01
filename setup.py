#!/usr/bin/env python
"""Distutils based setup script for Sympy.

This uses Distutils (http://python.org/sigs/distutils-sig/) the standard
python mechanism for installing packages. For the easiest installation
just type the command (you'll probably need root privileges for that):

    python setup.py install

This will install the library in the default location. For instructions on
how to customize the install procedure read the output of:

    python setup.py --help install

In addition, there are some other commands:

    python setup.py clean -> will clean all trash (*.pyc and stuff)
    python setup.py test  -> will run the complete test suite
    python setup.py test_core -> will run only tests concerning core features
    python setup.py test_doc -> will run tests on the examples of the documentation
    
To get a full list of avaiable commands, read the output of: 

    python setup.py --help-commands
    
Or, if all else fails, feel free to write to the sympy list at
sympy@googlegroups.com and ask for help.
"""

from distutils.core import setup
from distutils.core import Command
import sys

import sympy

# Make sure I have the right Python version.
if sys.version_info[1] < 4:
    print "Sympy requires Python 2.4 or newer.  Python %d.%d detected" % \
          sys.version_info[:2]
    sys.exit(-1)


class clean(Command):
    """Cleans *.pyc and debian trashs, so you should get the same copy as 
    is in the svn.
    """
    
    description = "Clean everything"
    user_options = [("all","a","the same")]  

    def initialize_options(self):  
        self.all = None
    
    def finalize_options(self):   
        pass

    def run(self):
        import os
        os.system("py.cleanup")
        os.system("rm -f python-build-stamp-2.4")
        os.system("rm -f MANIFEST")
        os.system("rm -rf build")
        os.system("rm -rf dist")

class gen_doc(Command):
    """Generate the (html) api documentation using epydoc

    output is sent to the directory ../api/
    """
    
    description = "generate the api doc"
    user_options = []
    
    target_dir = "../api/" 

    def initialize_options(self):  
        self.all = None
    
    def finalize_options(self):   
        pass

    def run(self):
        import os
        os.system("epydoc --no-frames -o %s sympy" % self.target_dir)


class test_sympy_core(Command):
    """Run only the tests concerning features of sympy.core.
    It's a lot faster than running the complete test suite.
    """
    
    description = "Automatically run the core test suite for Sympy."
    user_options = []  # distutils complains if this is not here.

    tests_to_run = ["tests/test_arit.py", "tests/test_basic.py", 
                   "tests/test_diff.py", "tests/test_equal.py", 
                   "tests/test_eval.py", "tests/test_evalf.py", 
                   "tests/test_functions.py", "tests/test_hashing.py", 
                   "tests/test_numbers.py", "tests/test_series.py", 
                   "tests/test_str.py", "tests/test_subs.py", 
                   "tests/test_symbol.py"
                   ]
    
    def initialize_options(self):  # distutils wants this
        pass
    
    def finalize_options(self):    # this too
        pass

        
    def run(self):
        try:
            import py
        except ImportError:
            print """In order to run the tests, you need codespeak's py.lib
            web page: http://codespeak.net/py/dist/
            If you are on debian systems, the package is named python-codespeak-lib
            """
            sys.exit(-1)
        py.test.cmdline.main(args=self.tests_to_run)
        

class test_sympy(Command):
    """Runs all tests under the tests/ folder
    """
    
    description = "Automatically run the test suite for Sympy."
    user_options = []  # distutils complains if this is not here.

    def __init__(self, *args):
        self.args = args[0] # so we can pass it to other classes
        Command.__init__(self, *args)

    def initialize_options(self):  # distutils wants this
        pass
    
    def finalize_options(self):    # this too
        pass
    
    def run(self):
        try:
            import py as pylib
        except ImportError:
            print """In order to run the tests, you need codespeak's py.lib
            web page: http://codespeak.net/py/dist/
            If you are on debian systems, the package is named python-codespeak-lib
            """
            sys.exit(-1)
        pylib.test.cmdline.main(args=["tests", "--nomagic"])
        tdoc = test_sympy_doc(self.args)
        tdoc.run() # run also the doc test suite

class test_sympy_doc(Command):
    
    description = "Run the tests for the examples in the documentation"
    user_options = []  # distutils complains if this is not here.
    
    def initialize_options(self):  # distutils wants this
        pass
    
    def finalize_options(self):    # this too
        pass
    
    def run(self):
        
        import unittest
        import doctest
        
        import glob

        print "Testing docstrings."

        files = glob.glob('sympy/*/*.py') + glob.glob('sympy/modules/*/*.py')
        #make it work on Windows too:
        files = [f.replace("\\","/") for f in files]
        
        # files without doctests or that don't work
        files.remove('sympy/modules/printing/pygame_.py')
        files.remove('sympy/modules/printing/pretty.py') # see issue 53
        # at this time Plot does not have doctests
        plotting_path = 'sympy/modules/plotting'
        files = [f for f in files if not f.startswith(plotting_path)]

        
        #testing for optional libraries
        try:
            import libxslt
        except ImportError:
            #remove tests that make use of libxslt1
            files.remove('sympy/modules/printing/latex.py')
            files.remove('sympy/modules/printing/__init__.py')

        modules = []
        for x in files:
            if len(x) > 12 and x[-11:] == '__init__.py':
                x = x.replace('/__init__', '') 
                print x
            modules.append(x.replace('/', '.')[:-3])
            #put . as separator and strip the extension (.py)

        modules.append('sympy')
        
        suite = unittest.TestSuite()
        for mod in modules:
            suite.addTest(doctest.DocTestSuite(mod))
            
        runner = unittest.TextTestRunner()
        runner.run(suite)

import sympy

setup(
      name = 'sympy', 
      version = sympy.__version__, 
      description = 'Computer algebra system (CAS) in Python', 
      license = 'BSD',
      url = 'http://code.google.com/p/sympy', 
      packages = ['sympy', 
                    'sympy.core', 'sympy.modules',
                    'sympy.modules.concrete',
                    'sympy.modules.geometry',
                    'sympy.modules.mathml', 
                    'sympy.modules.plotting',
                    'sympy.modules.plotting.renderables',
                    'sympy.modules.plotting.scene',
                    'sympy.modules.polynomials',
                    'sympy.modules.printing',
                    'sympy.modules.specfun',
                  ],
      package_data = {'sympy.modules.mathml' : ['data/*.xsl']}, 
      scripts = ['bin/isympy'],
      ext_modules = [],
      data_files = [('share/man/man1', ['doc/man/isympy.1'])],
      cmdclass    = {'test': test_sympy, 
                     'test_core' : test_sympy_core,
                     'test_doc' : test_sympy_doc,
                     'gen_doc' : gen_doc,
                     'clean' : clean, 
                     },
      )
