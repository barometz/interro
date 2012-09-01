#!/usr/bin/env python3

class Datum:
    """Stores the value and validation checks for one piece of information.
    
    validation is a list of (test, error) tuples.  In this list, test must be 
    a function taking one argument, evaluating to True or False depending on 
    whether the argument is considered valid.
    """
    name = None
    error = None
    value = None
    question = None
    confirm = False
    validation = None

    def __init__(self, name, question, confirm=False, validation=[]):
        """Create a new Datum.

        name: the name of this Datum
        question: the question to ask the user.
        confirm: Whether the system should ask for confirmation before 
                 committing this Datum.
        """
        self.name = name
        self.question = question
        self.confirm = confirm
        self.validation = []
        for test, error in validation:
            self.validation.append((test, error))

    def validate(self):
        """Check the current value for compliance with all validation tests.

        Returns false immediately when any test fails, otherwise True.
        """
        for test, error in self.validation:
            if not test(self.value):
                self.error = error
                return False
        self.error = None
        return True

    def setandcheck(self, value):
        """Set a new value, and return True if the value is valid."""
        self.value = value
        return self.validate()
                

class Interro:
    """The "interrogation" class.

    Keeps track of the desired Datum objects and keeps asking until it's
    satisfied that all of them validate.

    The interface to the outside is rather procedural, mostly in an attempt to
    support asynchronous users such as IRC bots that can't just stick around
    in a for loop until the conversation's done.
    """
    data = None
    _todo = None
    _current = None
    _pendingconfirmation = False

    def __init__(self):
        self.data = []
        self._todo = []

    def adddatum(self, name, question, confirm=False, validation=[]):
        """Convenience wrapper for Datum.__init__()"""
        self.data.append(Datum(name, question, confirm, validation))

    def start(self):
        """Fresh start, creating a fresh queue of unasked questions."""
        self._todo = list(self.data)
        self.nextdatum()

    def results(self):
        """Returns all results that have been collected so far"""
        res = {}
        for item in self.data:
            if (item.value != None):
                res[item.name] = item.value
        return res

    def question(self):
        """Returns the current question or None when all is done."""
        if self._current:
            message = ''
            if self._pendingconfirmation:
                message = '{0} is valid.  Are you sure? [yes/no]'.format(self._current.value)
            else:
                if self._current.error:
                    message = 'Error: {0}\n'.format(self._current.error)
                message += self._current.question
            return message
        else:
            return None
        
    def answer(self, value):
        """Provide an answer for the last question asked.  

        Returns nothing, but may advance the Interro object to the next datum
        when the answer is valid and/or confirmed."""
        if self._pendingconfirmation:
            value = value.lower()
            if value in ['yes', 'y']:
                self._pendingconfirmation = False
                self.nextdatum()
            elif value in ['no', 'n']:
                self._pendingconfirmation = False
        else:
            if self._current.setandcheck(value):
                if self._current.confirm:
                    self._pendingconfirmation = True
                else:
                    self.nextdatum()
    
    def nextdatum(self):
        """Go to the next required Datum, or set it to None when done."""
        if len(self._todo):
            self._current = self._todo.pop(0)
        else:
            self._current = None
