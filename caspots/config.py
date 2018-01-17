
import os

ASP_DIR = os.path.join(os.path.dirname(__file__), "asp")

def aspf(name):
    return os.path.join(ASP_DIR, name)

