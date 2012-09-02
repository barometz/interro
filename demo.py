#!/usr/bin/env python3
#
# Demonstration of Interro
#
# Copyright (c) 2012 Dominic van Berkel.  See LICENSE for details.
#

import interro as inter

c = inter.Interro(start='TOS')

c.add(inter.YesNoQ('TOS',
                   question='Do you agree to the TOS?',
                   onanswer={True: 'email'},
                   default='noTOS'))
c.add(inter.StringQ('email',
                    question='What is your email address?',
                    message='We will not share this with bad people',
                    validation=[(lambda x: '@' in x, 'Invalid address.'),
                                (lambda x: x != None, 'Cannot be empty')],
                    confirm=True))
c.add(inter.InterroQ('noTOS',
                     message='Well, that\'s unfortunate. Bye!'))

c.start()

while c.messages:
    print(c.messages.pop(0))
while not c.complete:
    response = input('> ')
    c.answer(response)
    while c.messages:
        print(c.messages.pop(0))

print(c.results())
