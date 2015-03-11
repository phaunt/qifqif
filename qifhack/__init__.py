#!/usr/bin/env python

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import argparse
import json
import os
import readline
import sys

from clint.textui import puts, prompt, colored
from difflib import SequenceMatcher


def prefilled_input(_prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    readline.redisplay()
    try:
        return raw_input(_prompt) or prefill
    finally:
        readline.set_startup_hook()


class InputCompleter(object):  # Custom completer

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:
            if text:
                self.matches = [s for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        try:
            return self.matches[state]
        except IndexError:
            return None


def find_category(categories, payee):
    for (c, keywords) in categories.items():
        if any([k.lower() in payee.lower() for k in keywords]):
            return c


def overwrite(text):
    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'
    return CURSOR_UP_ONE + ERASE_LINE + text
    #  return '\x1b[1A\x1b[1M' + text


def diff(a, b):
    s = SequenceMatcher(None, a, b)
    match = s.find_longest_match(0, len(a) - 1, 0, len(b) - 1)
    return '%s%s%s' % (colored.red(b[:match[1]]),
                       colored.green(b[match[1]:match[1] + match[2]]),
                       colored.red(b[match[2]:]))


def pick_category(payee, categories, default_choice=''):
    category = None

    COMPLETER = InputCompleter(categories.keys())
    while not category:
        readline.set_completer(COMPLETER.complete)
        category = prompt.query('Category', default=default_choice)
        readline.set_completer(None)
        # if not category Skip category [YES, No]
        if category.strip() and category not in categories:
            create = prompt.yn(overwrite("Create new '%s' category" %
                               category))
            if not create:
                category = None
            else:
                categories[category] = []

    if category != default_choice:
        match = None
        while True:
            match = prefilled_input('Match...: ', match or payee)
            if match in payee:
                break
            else:
                puts(overwrite('Match rejected...: %s') % diff(payee, match))
        categories[category].append(match)
    return (category, categories)


def fetch_categories(lines, categories, options):
    readline.parse_and_bind('tab: complete')
    result = []
    for line in lines:
        if line.startswith('T'):
            amount = line[1:].strip()
        payee = line[1:].strip() if line.startswith('P') else None
        if payee:  # write payee line and find category to write on next line
            result.append(line)
            category = find_category(categories, payee)
            puts('Amount..: %s' % (colored.green(amount) if float(amount) > 0
                 else colored.red(amount)))
            puts('Payee...: ' + payee)
            prompt = category
            category = '' if options['audit'] else category
            while not category:
                category, categories = pick_category(payee, categories, prompt)
            result.append('L%s\n' % category)
        elif not line.startswith('L'):  # overwrite previous categories
            result.append(line)
        if line.startswith('^'):
            if options['audit']:
                print('Category: %s' % category)  # erase last line
            print '---'
    return result, categories


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Enrich your .QIF files with categories. '
        'See https://github.com/Kraymer/qifhack for more infos.')
    parser.add_argument('src', metavar='QIF_FILE',
                        help='.QIF file to process', default='')
    parser.add_argument('-a', '--audit-mode', dest='audit',
                        action='store_true', help=('pause after'
                                                   'each transaction'))
    parser.add_argument('-o', '--output', dest='dest',
                        help='Output filename. '
                        'DEFAULT: edit input file in-place', default='')
    parser.add_argument('-c', '--config', dest='config',
                        help='Configuration filename in json format. '
                        'DEFAULT: ~/.qifhack.json',
                        default=os.path.join(os.path.expanduser('~'),
                                             '.qifhack.json'))
    args = vars(parser.parse_args())
    if not args['dest']:
        args['dest'] = args['src']

    if os.path.isfile(args['config']):
        with open(args['config'], 'r') as cfg:
            cfg_dict = json.load(cfg)
    else:
        cfg_dict = {}
    with open(args['src'], 'r') as f:
        lines = f.readlines()
        result, categories = fetch_categories(lines, cfg_dict, options=args)
    with open(args['dest'], 'w') as f:
        f.writelines(result)
    with open(args['config'], 'w+') as cfg:
        cfg.write(json.dumps(categories,
                  sort_keys=True, indent=4, separators=(',', ': ')))

if __name__ == "__main__":
    sys.exit(main())
