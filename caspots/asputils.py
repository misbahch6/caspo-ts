import re

re_clause = re.compile("(\w+)\(([^\)]*)\)\.")
re_answer = re.compile("(\w+)\(([^\)]*)\)")

def parse_args(args):
    def parse_arg(a):
        a = a.strip()
        if a[0] == '"':
            return a.strip('"')
        else:
            return int(a)
    return [parse_arg(a) for a in args.split(",")]

class funset(set):
    def __init__(self, *objs):
        self.push(*objs)

    def push(self, *objs):
        for obj in objs:
            self.update(obj.to_funset())
    def to_funset(self):
        return self

    def to_file(self, path):
        open(path, 'w').write(self.to_str())

    def to_str(self):
        if len(self):
            return ".\n".join(sorted(map(str, self)))+".\n"
        return ""
