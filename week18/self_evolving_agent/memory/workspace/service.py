def parse(line):
    a, b = line.split(',')
    return int(a) / int(b)

def run(lines):
    return [parse(l) for l in lines]  # no error handling
