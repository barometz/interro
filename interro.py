# A module to interactively extract information from users.
#
# Copyright (c) 2012 Dominic van Berkel.  See LICENSE for details.
#

class InterroQ:
    """Base class for Interro questions.  

    InterroQ has some infrastructure for validation checks, type checks that
    more specific question types can use and answer-dependant branching.

    Usage: 
    Create an instance with whatever parameters you like.  When you've got an
    answer, run it through .validate() to make sure it's of the right format.
    When that's done it can be stored with .store(), which will automatically
    run the value through .parse() in order to convert it to an appropriate
    type, format or otherwise.  Mostly it's expected that values thrown at 
    InterroQ are all strings.

    Interesting functions to override: 
    - parse: Takes a value and returns a format-appropriate representiation.
      See YesNoQ for an example.
    - add_typechecks: This is where subclasses can specify their type checks.
    - preprocess: General processing that should be done first, such as
      str.strip() and .lower()

    """

    name = ''
    question = None
    message = None
    default = None
    onanswer = None
    validation = None
    confirm = False
    type_validation = None
    error = None
    value = None

    def __init__(self, name, question=None, message=None, default=None, 
                 onanswer=None, validation=None, confirm=False):
        """Create an InterroQ instance.

        Parameters:
        - name: name of the question.  Can be used to identify the information.
        - question: The question to be asked.  
        - message: A message that will be shown when a question comes up for the
          first time.
        - default: The name of the question that should come after by default.
        - onanswer: a dictionary of {value: InterroQ}.  If the stored and
          parsed answer matches a value, this indicates what question to pull
          up next.
        - validation: A list of (method: error) tuples. 
        - confirm: Indicates whether the question requires confirmation.

        """
        self.name = name
        self.question = question
        self.message = message
        self.default = default
        self.onanswer = onanswer or {}
        self.validation = validation or []
        self.confirm = confirm
        self.add_typechecks()

    def add_typechecks(self, *args):
        """Add typechecks.

        The advice for subclasses is to construct a list of (method, error)
        and throw that at super() together with *args.

        """
        self.type_validation = args

    def preprocess(self, value):
        """Cleanup and essential formatting of input.

        Should be called by validate() and parse() before doing anything with
        the input.

        """
        return value

    def validate(self, value):
        """Runs the value through all known tests.

        Starts with type validation, then moves on to user-configured 
        requirements.

        """
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
        """Convert the value to someting appropriate for the question type.

        For example, YesNoQ turns it into a boolean, while a NumberQ might
        change it into an integer or float.  It's okay if this raises an
        exception on failure, as the type-specific validation checks should
        already make sure that it can be converted in the first place.

        """
        return self.preprocess(value)

    def store(self, value):
        """Parse and store the input."""
        self.value = self.parse(value)

    def nextq(self):
        """Find out what the next question is based on the current value."""
        if self.onanswer and self.value in self.onanswer:
            return self.onanswer[self.value]
        else:
            return self.default
            

class TextQ(InterroQ):
    """Text question class.

    Does very little, other than - if desired - making sure the input isn't
    empty and trimming the sides.

    """

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
    """Yes/No-question class."""

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
