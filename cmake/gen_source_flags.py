# (C) Copyright 1996-2015 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

"""
Generate .cmake file to set source-file specific compiler flags based on
rules defined in a JSON file.
"""

from argparse import ArgumentParser
from fnmatch import fnmatch
import logging
from json import JSONDecoder
from os import path

log = logging.getLogger('gen_source_flags')


def match(source, pattern, op, flags):
    if fnmatch(source, pattern) or path.split(source)[0] == pattern:

        suff = '' if op[0] in ('+', '=', '/') else ' (nested pattern)'
        log.debug(' -> pattern "%s" matches "%s"%s', pattern, source, suff)

        if op[0] == "+":
            log.debug('  appending %s', op[1:])
            flags += [flag for flag in op[1:] if flag not in flags]

        elif op[0] == "=":
            log.debug('  setting %s', op[1:])
            flags = []
            flags += [flag for flag in op[1:] if flag not in flags]

        elif op[0] == "/":
            log.debug('  removing %s', op[1:])
            for flag in op[1:]:
                flags.remove(flag)

        else:  # Nested rule
            for nested_pattern, nested_op in op:
                match(source, nested_pattern, nested_op, flags)


def generate(rules, out, default_flags, sources, debug=False):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='-- %(levelname)s - %(name)s: %(message)s')

    with open(path.expanduser(rules)) as f:
        rules = JSONDecoder(object_pairs_hook=list).decode(f.read())

    with open(path.expanduser(out), 'w') as f:
        for source in sources:
            log.debug(source)
            flags = default_flags.split()
            for pattern, op in rules:
                match(source, pattern, op, flags)

            if flags:
                log.debug(' ==> setting flags for %s to %s', source, ' '.join(flags))
                f.write('set_source_files_properties(%s PROPERTIES COMPILE_FLAGS "%s")\n'
                        % (source, ' '.join(flags)))


def main():
    """Parse arguments"""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('rules', metavar='RULES.json', help='JSON rules file')
    parser.add_argument('out', metavar='OUT.cmake', help='CMake script to generate')
    parser.add_argument('default_flags', help='Default compiler flags to use')
    parser.add_argument('sources', metavar='file', nargs='+', help='Path to file to apply rules to')
    parser.add_argument('--debug', '-d', action='store_true', help='Log debug messages')
    generate(**vars(parser.parse_args()))

if __name__ == '__main__':
    main()
