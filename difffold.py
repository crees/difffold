#!/usr/bin/env python
#
# Copyright (c) 2021 Chris Rees. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE PROJECT BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import re
import sys
import textwrap

def wrap(text, output = True):
    global wrapper
    ret = wrapper.wrap(text)
    if output:
        for l in ret:
            print(l)
    return ret

def warn(text):
    global lineNumber
    sys.stdout.write('line %d: %s' % (lineNumber, text))

def err(text):
    warn(text)
    exit(0)

def getLine():
    global lineNumber
    lineNumber += 1
    return sys.stdin.readline()

def skipToPatch():
    '''Output lines that are not patches, and consume the first two lines'''
    line = getLine()
    print(line, end='')
    if line == '':
        exit(0)
    if line[:3] != '---':
        # Hmm...
        return skipToPatch()
    line = getLine()
    print(line, end='')
    if line[:3] != '+++':
        # not actually a patch...
        return skipToPatch()

def foldHunks():
    added = []
    removed = []
    while True:
        (oldlength, newlength) = hunkLength()
        while (oldlength > 0 or newlength > 0):
            line = getLine()
            if line[0] == '+':
                added.append(line)
                newlength -= 1
                continue
            if line[0] == '-':
                removed.append(line)
                oldlength -= 1
                continue
            if line[0] == '@':
                err('Malformed patch file')
            # We have reached the end of the change block
            while len(added) > 0 and len(removed) > 0:
                # OK, so now here's where the folding happens logically.
                # Zip together the wrapped patches.
                r = wrap(removed.pop(0), False)
                a = wrap(added.pop(0), False)
                firstLine = True
                while len(r) > 0:
                    if firstLine:
                        print(r.pop(0))
                        if len(a) > 0:
                            print(a.pop(0))
                        firstLine = False
                    else:
                        print(">-%s" % r.pop(0))
                        if len(a) > 0:
                            print(">+%s" % a.pop(0))
                while len(a) > 0:
                    # Run out of the removed, so just chuck out the added
                    print(a.pop(0))
            while len(removed) > 0:
                wrap(removed.pop(0))
            while len(added) > 0:
                wrap(added.pop(0))
            oldlength -= 1
            newlength -= 1
            wrap(line)

def hunkLength():
    # Returns the old length and new length of the hunk as a tuple
    # Consumes the @@ line
    line = getLine()
    print(line)
    m = re.match('^@@ -[0-9]+,?([0-9]*)[^+]+\+[0-9]+,?([0-9]*)', line)
    if m == None:
        skipToPatch()
        return hunkLength()
    ret = [None] * 2
    for i in range(2):
        ret[i] = m.group(i+1)
        # Apparently GNU feels the length is optional if it's 1
        if ret[i] == '':
            ret[i] = 1
        ret[i] = int(ret[i])
    return ret

wrapper = textwrap.TextWrapper()
lineNumber = -1

while True:
    skipToPatch()
    foldHunks()

