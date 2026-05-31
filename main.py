from tester import performTesting
from configurations import configuration
from Lexer import Lexer

# Run the test suite.
performTesting()

# Execute the lexer.

""" with open(configuration.SOURCE_CODE_PATH, "r") as source_code_file:
    source_code = source_code_file.read()
    lexer = Lexer(source_code)
    reults = lexer.get_results()
    print(reults)
 """