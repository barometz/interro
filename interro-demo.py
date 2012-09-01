#!/usr/bin/env python3
#
# Demonstration script for interro.py
#

import interro

c = interro.Interro()

emailcheck = [(lambda x: x != '', 'Email cannot be empty.'),
              (lambda x: '@' in x, 'This is not a valid email address.')]
agecheck = [(lambda x: x.isdigit(), 'Please enter only whole numbers.')]

c.data.append(interro.Datum('email', 
                            'What is your email address?', 
                            confirm=True, 
                            validation=emailcheck))
c.data.append(interro.Datum('age',
                            'What is your age?',
                            validation=agecheck))
print(c.data)
print(c.data[0].validation)
print(c.data[1].validation)
c.start()

q = c.nextquestion()

while q:
    print(q)
    c.answer(input('> '))
    q = c.nextquestion()

print(c.results())
