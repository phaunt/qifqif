#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2020 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

"""Utilities functions related to terminal display."""

import re
from difflib import SequenceMatcher

try:
    import pyreadline as readline  # Windows
except ImportError:
    try:
        import gnureadline as readline  # Mac OS X
    except ImportError:
        import readline

from qifqif.terminal import TERM

readline.parse_and_bind('tab: complete')


def colorize_match(t, field, matches=None):
    field_val = t[field]
    if not field_val:
        return None
    match = matches.get(field, '') if matches else ''
    seqmatch = SequenceMatcher(None, field_val, match)
    a, b, size = seqmatch.find_longest_match(0, len(field_val), 0, len(match))
    return (field_val[:a] + TERM.green(field_val[a:a + size]) +
            field_val[a + size:])


class InputCompleter(object):
    """Input completer for categories."""

    def __init__(self, options):
        self.options = options

    def complete(self, text, state):
        readline.redisplay()
        if state == 0:
            if text:
                self.matches = [s for s in self.options
                                if s and s.lower().startswith(text.lower())]
            else:
                self.matches = self.options[:]
        try:
            return self.matches[state]
        except IndexError:
            return None


def set_completer(options=None):
    if options:
        completer = InputCompleter(options)
        readline.set_completer_delims('')
        readline.set_completer(completer.complete)
    else:
        readline.set_completer(None)


def complete_matches(payee):
    """Generate a limited set of matches for payee line.

    >>> complete_matches("foo bar spam")
    ['foo', 'bar', 'spam', 'foo bar spam', 'bar spam', 'spam']
    """
    # Append each individual word to result
    matches = [m for m in re.findall(r"\w+", payee) if m]
    select = True
    if len(matches) > 1:
        for (i, c) in enumerate(payee):
            if c.isalnum() and select:
                # Append suffixes to result
                matches.append(payee[i:])
            select = not c.isalnum()
    return matches
