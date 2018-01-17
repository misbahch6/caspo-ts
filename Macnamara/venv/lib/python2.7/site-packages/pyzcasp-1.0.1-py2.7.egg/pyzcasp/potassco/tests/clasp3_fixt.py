import json
from zope import interface, component
from pyzcasp import asp, potassco

JSON1 = """
{
  "Solver": "clingo version 4.3.0",
  "Input": [
    "test.lp"
  ],
  "Call": [
    {
      "Witnesses": [
        {
          "Value": [
            "a(1)", "a(2)"
          ],
          "Costs": [
            3
          ]
        }
      ]
    },
    {
      "Witnesses": [
        {
          "Value": [
            "a(1)", "a(2)"
          ],
          "Costs": [
            3
          ]
        }
      ]
    }
  ],
  "Result": "OPTIMUM FOUND",
  "Models": {
    "Number": 4,
    "More": "no",
    "Optimum": "yes",
    "Optimal": 1,
    "Costs": [
      3
    ]
  },
  "Calls": 2,
  "Time": {
    "Total": 0.023,
    "Solve": 0.000,
    "Model": 0.000,
    "Unsat": 0.000,
    "CPU": 0.010
  }
}
"""

JSON2 = """
{
  "Solver": "clingo version 4.3.0",
  "Input": [
    "test.lp"
  ],
  "Call": [
    {

    }
  ],
  "Result": "SATISFIABLE",
  "Models": {
    "Number": 1,
    "More": "yes"
  },
  "Calls": 1,
  "Time": {
    "Total": 0.001,
    "Solve": 0.000,
    "Model": 0.000,
    "Unsat": 0.000,
    "CPU": 0.000
  }
}
"""
class Clasp3Mock(potassco.Clasp3):
    
    def execute(self, gr, *args):
        if gr == 1:
            self.json = json.loads(JSON1)
        elif gr == 2:
            self.json = json.loads(JSON2)
            
        return "",0

    
def setup_test(test):
    test.globs['clasp3'] = Clasp3Mock(None)

setup_test.__test__ = False
