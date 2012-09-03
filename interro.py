# A module to interactively extract information from users.
#
# Copyright (c) 2012 Dominic van Berkel.  See LICENSE for details.
#

from questions import *

class Interro:
    """Core "interrogation" class.

    Keeps track of the questions in what is essentially a singly-linked list.
    Spits out questions, descriptive messages and errors, passes answers on to
    the InterroQ objects and asks for confirmation as needed.

    Usage:
    After instantiation InterroQ instances can be passed to add() which will
    add them to the list.  After start() is called, messages will be
    chronologically filled with messages from questions as they roll in.
    Submit answers through answer() as long as complete isn't True, then call
    results() to get a dictionary of results.  Terminates when an InterroQ is
    processed that doesn't actually have a question attached to it.

    """
    questions = None
    current = None
    messages = None
    _msg = None
    complete = False
    _pendinganswer = None
    _pendingconfirmation = False
    
    def __init__(self, msg_callback=None):
        self.messages = []
        self.questions = {}
        self._msg = msg_callback or self.messages.append

    def results(self):
        """Get a dictionary of {name: value} with the results so far"""
        res = {}
        for q in self.questions.values():
            if q.value is not None:
                res[q.name] = q.value
        return res

    def add(self, question):
        """Add an InterroQ instance to the list."""
        self.questions[question.name] = question

    def start(self, start='start'):
        """Start pulling questions."""
        self._nextquestion(goto=start)

    def answer(self, value):
        """Process an answer.

        If we're waiting for confirmation, handle that and move to the next
        question if the answer is yes.  Otherwise, throw the answer at the
        current InterroQ to see if it validates, then store it and maybe ask
        for confirmation.

        """
        cur = self.current
        if self._pendingconfirmation:
            value = value.strip().lower()
            if value in ['yes', 'y']:
                self._nextquestion()
            else:
                self._msg(cur.question)
            self._pendingconfirmation = False
        else:
            # Throw the answer at the current question
            if cur.validate(value):
                cur.store(value)
                if cur.confirm:
                    self._pendingconfirmation = True
                    confirmq = 'You entered {value}.  Are you certain? [yes/no]'
                    self._msg(confirmq.format(value=value))
                else:
                    self._nextquestion()
            else:
                self._msg('Error: {0}'.format(cur.error))
                self._msg(cur.question)

    def _nextquestion(self, goto=None):
        """Move to the next question, if any.

        Sets self.complete to true if the new InterroQ doesn't actually have a
        question, but does add its message - if any - to the message queue.

        """
        if self.current:
            nextq = self.current.nextq()
        else:
            nextq = None
        if goto is None and nextq is None:
            self.complete = True
        else:
            goto = goto or nextq
            self.current = self.questions[goto]
            if self.current.question:
                self._msg(self.current.question)
            if self.current.message:
                self._msg(self.current.message)
            if not self.current.question:
                self._nextquestion()
