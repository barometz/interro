# A module to interactively extract information from users.
#
# Copyright (c) 2012 Dominic van Berkel.  See LICENSE for details.
#


class InterroQ:
    name = ''
    question = ''
    message = ''
    default = None
    onanswer = None
    validation = None
    confirm = False
    type_validation = None
    error = None
    value = None

    def __init__(self, name, question='', message='', default=None, 
                 onanswer=None, validation=None, confirm=False):
        self.name = name
        self.question = question
        self.message = message
        self.default = default
        self.onanswer = onanswer or {}
        self.validation = validation or []
        self.confirm = confirm
        self.add_typechecks()

    def add_typechecks(self, *args):
        self.type_validation = args

    def preprocess(self, value):
        return value

    def validate(self, value):
        value = self.preprocess(value)
        for test, error in self.type_validation:
            if not test(value):
                self.error = error
                return False
        for test, error in self.validation:
            if not test(value):
                self.error = error
                return False
        self.error = None
        return True

    def parse(self, value):
        return self.preprocess(value)

    def store(self, value):
        self.value = self.parse(value)

    def nextq(self):
        if self.onanswer and self.value in self.onanswer:
            return self.onanswer[self.value]
        else:
            return self.default
            

class StringQ(InterroQ):
    empty_allowed = False

    def __init__(self, name, empty_allowed=False, **kwargs):
        self.empty_allowed = empty_allowed
        super().__init__(name, **kwargs)

    def add_typechecks(self, *args):
        empty = (self.test_empty, 'This may not be empty.')
        super().add_typechecks(empty, *args)

    def preprocess(self, value):
        return value.strip()

    def test_empty(self, value):
        if self.empty_allowed:
            return True
        else:
            if value not in [None, '']:
                return True
            else:
                return False


class YesNoQ(InterroQ):
    def add_typechecks(self, *args):
        yesno = (lambda x: x in ['y', 'yes', 'n', 'no'], 'Please enter yes or no.')
        super().add_typechecks(yesno, *args)

    def preprocess(self, value):
        return value.strip().lower()

    def parse(self, value):
        value = self.preprocess(value)
        if value in ['y', 'yes']:
            return True
        else:
            return False


class Interro:
    tree = None
    current = None
    messages = None
    complete = False
    _start = ''
    _pendinganswer = None
    _pendingconfirmation = False
    
    def __init__(self, start='start'):
        self.messages = []
        self.tree = {}
        self._start = start

    def results(self):
        res = {}
        for q in self.tree.values():
            if q.value is not None:
                res[q.name] = q.value
        return res

    def add(self, datum):
        self.tree[datum.name] = datum

    def start(self):
        self._nextdatum(goto=self._start)

    def answer(self, value):
        cur = self.current
        if self._pendingconfirmation:
            value = value.strip().lower()
            if value in ['yes', 'y']:
                self._nextdatum()
            else:
                self.messages.append(cur.question)
            self._pendingconfirmation = False
        else:
            if cur.validate(value):
                cur.store(value)
                if cur.confirm:
                    self._pendingconfirmation = True
                    confirmq = 'You entered {value}.  Are you certain? [yes/no]'
                    self.messages.append(confirmq.format(value=value))
                else:
                    self._nextdatum()
            else:
                self.messages.append('Error: {0}'.format(cur.error))
                self.messages.append(cur.question)

    def _nextdatum(self, goto=None):
        if self.current:
            nextq = self.current.nextq()
        else:
            nextq = None
        if goto is None and nextq is None:
            self.complete = True
        else:
            goto = goto or nextq
            self.current = self.tree[goto]
            if self.current.question:
                self.messages.append(self.current.question)
            if self.current.message:
                self.messages.append(self.current.message)
            else:
                self.complete = True
