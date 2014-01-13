import nose
from nose.case import FunctionTestCase
from nose.plugins import Plugin
from nose.loader import TestLoader
from nose.pyversion import ismethod
from nose.util import (
    isclass,
    isgenerator
)


class NewFunctionTestCase(FunctionTestCase):
    """
    Rewrite part of class FunctionTestCase, to get same format of output
    test results for generators, like other tests of class.
    """

    def __init__(
            self, cls, test, setUp=None, tearDown=None, arg=tuple(),
            descriptor=None
    ):
        self.cls = cls
        FunctionTestCase.__init__(self, test, setUp, tearDown, arg, descriptor)

    def __str__(self):
        func, _ = self._descriptors()
        if hasattr(func, 'compat_func_name'):
            name = func.compat_func_name
        else:
            name = func.__name__
        name = "%s.%s.%s" % (
            self.cls.__module__,
            self.cls.__name__,
            name
        )
        return name
    __repr__ = __str__


class CustomLoader(TestLoader):
    """
    Based on nose function: loadTestsFromGenerator from loader.py,
    which Lazy-load tests from a generator function.
    """

    def load_tests_from_generator_method_with_set_up(self, generator, cls):
        test_class_instance = cls()
        test_class_instance.setUp()

        def generate():
            for test in generator(test_class_instance):

                test_func, arg = self.parseGeneratedTest(test)
                yield NewFunctionTestCase(test=test_func, arg=arg, cls=cls)

        return self.suiteClass(generate, context=generator, can_split=False)


class YieldWithSetUp(Plugin):
    """
    Main plugin yield class definition. Features: Run setUp on generators
    and display full path in output during test.
    """
    name = 'yield'

    def __init__(self):
        super(YieldWithSetUp, self).__init__()

    def makeTest(self, obj, cls):
        if ismethod(obj) and isgenerator(obj) and isclass(cls):
            x = CustomLoader()
            return x.load_tests_from_generator_method_with_set_up(obj, cls)

if __name__ == '__main__':
    nose.main()
