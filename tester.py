import unittest

import tests.test_lexer_1.test_current_lexer
import tests.test_lexer_1.test_future_lexer_extensions


def performTesting():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(tests.test_lexer_1.test_current_lexer))
    suite.addTests(loader.loadTestsFromModule(tests.test_lexer_1.test_future_lexer_extensions))

    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)