from Lexer.tester import performTesting
from Lexer.configurations import configuration
from Lexer.Lexer import Lexer

# Run the test suite.
performTesting()

# Execute the lexer.

""" with open(configuration.SOURCE_CODE_PATH, "r") as source_code_file:
    source_code = source_code_file.read()
    lexer = Lexer(source_code)
    results = lexer.get_results()
    print(results) """
