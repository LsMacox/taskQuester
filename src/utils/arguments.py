def parse_arguments(argv):
    arguments = {}
    for arg in argv[1:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            arguments[key] = value
        else:
            arguments[arg] = ''

    return arguments
