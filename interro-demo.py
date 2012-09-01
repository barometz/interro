#!/usr/bin/env python3
#
# Demonstration script for interro.py
#

import interro

interrogation = interro.Interro()

emailcheck = [(lambda x: x != '',     'Email cannot be empty.'),
              (lambda x: '@' in x,    'This is not a valid email address.')]
agecheck =   [(lambda x: x.isdigit(), 'Please enter only whole numbers.')]

interrogation.adddatum('email', 'What is your email address?', 
                       confirm=True, validation=emailcheck)
interrogation.adddatum('age', 'What is your age?', 
                       validation=agecheck)

print(interrogation.data)
print(interrogation.data[0].validation)
print(interrogation.data[1].validation)

interrogation.start()
q = interrogation.question()
while q:
    print(q)
    interrogation.answer(input('> '))
    q = interrogation.question()

print(interrogation.results())
