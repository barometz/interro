#!/usr/bin/env python3

class Datum:
    name = None
    error = None
    value = None
    question = None
    confirm = False
    # list of (test, errormsg) tuples - semantically more sensible than a dictionary.
    validation = None

    def __init__(self, name, question, confirm=False, validation=[]):
        self.name = name
        self.question = question
        self.confirm = confirm
        self.validation = []
        for test, error in validation:
            self.addvalidation(test, error)

    def addvalidation(self, test, error):
        pair = (test, error)
        self.validation.append(pair)

    def validate(self):
        self.error = None
        for test, error in self.validation:
            try:
                assert(test(self.value))
            except AssertionError:
                self.error = error
                return False
        return True

    def setandcheck(self, value):
        self.value = value
        return self.validate()
                

class Interro:
    data = []
    _todo = []
    _current = None
    _pendingconfirmation = False
    _nextq = None

    def __init__(self):
        pass

    def start(self):
        self._todo = list(self.data)
        self.nextdatum()

    def results(self):
        res = {}
        for item in self.data:
            res[item.name] = item.value
        return res

    def nextquestion(self):
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
        if len(self._todo):
            self._current = self._todo.pop(0)
        else:
            self._current = None

if __name__ == '__main__':
    c = Interro()
    i = Datum('email', 'What is your email address?', confirm=True,
                 validation=[(lambda x: x != '', 'Email cannot be empty.'),
                             (lambda x: '@' in x, 'This is not a valid email address.')])
    c.data.append(i)
    i = Datum('age', 'What is your age?', 
                 validation=[(lambda x: x.isdigit(), 'Please enter only whole numbers.')])
    c.data.append(i)
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
    
