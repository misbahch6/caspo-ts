import json
from zope import interface, component
from pyzcasp import asp, potassco

JSON1 = """
{
  "Solver": "clasp version 2.1.4",
  "Input": "stdin",
  "Witnesses": [
    {
      "Value": [
        "a(2)", "a(3)"
      ],
      "Opt": [
        5
      ]
    },
    {
      "Value": [
        "a(1)", "a(3)"
      ],
      "Opt": [
        4
      ]
    },
    {
      "Value": [
        "a(1)", "a(2)"
      ],
      "Opt": [
        3
      ]
    },
    {
      "Value": [
        "a(1)", "a(2)", "a(3)"
      ],
      "Opt": [
        6
      ]
    }
  ],
  "Result": "OPTIMUM FOUND",
  "Stats": {
    "Models": 4,
    "Complete": "yes",
    "Optimum": "yes",
    "Time": {
      "Total": 0.003,
      "Solve": 0.000,
      "Model": 0.000,
      "Unsat": 0.000,
      "CPU": 0.000
    }
  }
}
"""

JSON2 = """
{
  "Solver": "clasp version 2.1.4",
  "Input": "stdin",
  "Witnesses": [
    {
      "Brave": [
        "a(1)", "a(2)", "a(3)"
      ]
    }
  ],
  "Result": "SATISFIABLE",
  "Stats": {
    "Models": 1,
    "Complete": "yes",
    "Enumerated": 2,
    "Brave": "yes",
    "Time": {
      "Total": 0.000,
      "Solve": 0.000,
      "Model": 0.000,
      "Unsat": 0.000,
      "CPU": 0.000
    }
  }
}
"""

JSON3 = """
{
  "Solver": "clasp version 2.1.4",
  "Input": "stdin",
  "Witnesses": [
    {
      "Cautious": [

      ]
    }
  ],
  "Result": "SATISFIABLE",
  "Stats": {
    "Models": 1,
    "Complete": "yes",
    "Enumerated": 3,
    "Cautious": "yes",
    "Time": {
      "Total": 0.000,
      "Solve": 0.000,
      "Model": 0.000,
      "Unsat": 0.000,
      "CPU": 0.000
    }
  }
}
"""

JSON4 = """
{
  "Solver": "clasp version 2.1.4",
  "Input": "stdin",
  "Result": "SATISFIABLE",
  "Stats": {
    "Models": 4,
    "Complete": "yes",
    "Time": {
      "Total": 0.000,
      "Solve": 0.000,
      "Model": 0.000,
      "Unsat": 0.000,
      "CPU": 0.000
    }
  }
}
"""

class Clasp2Mock(potassco.Clasp2):
    
    def execute(self, gr, *args):
        if gr == 1:
            self.json = json.loads(JSON1)
        elif gr == 2:
            self.json = json.loads(JSON2)
        elif gr == 3:
            self.json = json.loads(JSON3)
        elif gr == 4:
            self.json = json.loads(JSON4)
        
        return "",0

def setup_test(test):
    test.globs['clasp2'] = Clasp2Mock(None)

setup_test.__test__ = False
