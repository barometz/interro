#!/usr/bin/env python3
#
# Demonstration of Interro
#
# Copyright (c) 2012 Dominic van Berkel.  See LICENSE for details.
#

import interro as inter

def output(value):
    """A little wrapper to print things.

    Necessary to have the msg_callback work in Python 2.7, where print isn't a
    function.

    """
    print(value)

c = inter.Interro(msg_callback=output)

c.add(inter.YesNoQ('TOS',
                   question='Do you agree to the TOS?',
                   onanswer={True: 'email'},
                   default_next='noTOS'))
c.add(inter.TextQ('email',
                  question='What is your email address?',
                  message='We will not share this with bad people',
                  validation=[(lambda x: '@' in x, 'Invalid address.')],
                  confirm=True,
                  default_next='age'))
c.add(inter.NumberQ('age',
                    question='How old are you?',
                    req_positive=True))
c.add(inter.MessageQ('noTOS',
                     message='Well, that\'s unfortunate. Bye!'))

c.start('TOS')

while not c.complete:
    response = input('> ')
    c.answer(response)

print(c.results())
