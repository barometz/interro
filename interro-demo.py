#!/usr/bin/env python3
#
# Copyright (c) 2012 Dominic van Berkel.  See LICENSE for details.
#
# Demonstration script for interro.py.  This will always work with the version
# of interro.py in the same revision.
#

import interro

# First, create an Interro object.
interrogation = interro.Interro()

# Here the validation rules are constructed.  This example uses lambdas
# because they're neat and demonstrate the functionality well enough, but any
# function that takes one argument and spits out True or False will do.  
# 
# For two reasons you should make tests pretty specific: first, the more
# specific a test is, the more specific the error message can be that the user
# receives.  Second, every time an answer is given all tests for that answer
# are looped through until one fails, so having more specific tests tends to
# lighten the load when a tiny condition isn't met.  Tests are executed in the
# order in which they were added, so if you have any that create a lot of
# system load or take a lot of time, put those towards the end.
emailcheck = [(lambda x: x != '',     'Email cannot be empty.'),
              (lambda x: '@' in x,    'This is not a valid email address.')]
agecheck =   [(lambda x: x.isdigit(), 'Please enter only whole numbers.')]

interrogation.adddatum('email', 'What is your email address?', 
                       confirm=True, validation=emailcheck, 
                       message='We will not share you email with bad people.')
interrogation.adddatum('age', 'What is your age?', 
                       validation=agecheck)

# Some debug noise
print(interrogation.data)
print(interrogation.data[0].validation)
print(interrogation.data[1].validation)

# Interro.start() creates or resets the list of questions that weren't asked
# yet.  It has to be called before trying to retrieve any questions.
interrogation.start()

# Unfortunately Interro can't (shouldn't) expose an iterator interface because
# that would be useless to asynchronous systems like an IRC bot, which can't
# just stick around in a for loop until all questions have been answered.
# Additionally it's semantically weird to do this sort of call/response with
# an iterator.
q = interrogation.question()
while q:
    print(q)
    interrogation.answer(input('> '))
    q = interrogation.question()

print(interrogation.results())
