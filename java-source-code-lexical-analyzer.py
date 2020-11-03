# java-source-code-lexical-analyzer.py - the main file of the project.
# By: Trevor D. Brown
# Date: 11/20/2020
#
# In partial fulfillment of credit for:
#       CS 530 (Automata Theory and Compiler Construction)
#       Professor: Dr. Mustafa Atici
#       Institution: Western Kentucky University
#       Semester: Fall 2020
#
# Purpose:  reads in a file containing Java source code, and identifies the components of the source file.
#

# Imports
import os       # File I/O support
import sys      # Supporting in-line arguments when calling script
import json     # JSON I/O support
import re       # Regular Expression support for tokenization

# JavaSourceCodeLexical analyzer - an object representing the entire lexical analyzer "machine".
class JavaSourceCodeLexicalAnalyzer:
    # Attributes
    __sourceFilename = ""           # Source Filename - the filename of the target Java source code file.
    __sourceFileContent = ""        # Source File Content - a dump of the content of the Java source code file specified.
    __fileLexemes = []              # File Lexemes - a list of Token objects, representing the raw lexemes extracted.
    __fileTokens = []               # File Tokens - a list of Token objects, representing interpreted tokens from the lexemes.
    __predefinedTokens = []         # Predefined Tokens - a list of JSON objects, representing known tokens.
    __validFile = False             # Valid File - a flag to indicate to the end user that a provided file is "valid" (i.e. not lexically sound, but can be read)

    # Constructor
    def __init__(self, filename):
        self.__sourceFilename = filename                    # Store the specified Java source code file's filename
        self.__fileLexemes = []                             # Initialize the list
        self.__fileTokens = []                              # Initialize the list
        self.__validFile = self.__readJavaSourceFile()      # See if the file can be read
        self.__loadTokens()                                 # Load the Predefined Tokens List.

    # loadTokens - loads in the predefined tokens from the tokens.json file.
    def __loadTokens(self):
        tokensFilename = "tokens.json"

        try:
            with open(tokensFilename) as f:
                self.__predefinedTokens = json.load(f)

        except Exception as e:
            print(e)
            return False
        
        return True

    # searchPredefinedTokens - searches the list of predefined tokens using a provided target lexeme.
    def __searchPredefinedTokens(self, targetLexeme):
        for entry in self.__predefinedTokens:
            if targetLexeme in entry["values"]:
                return entry["type"], entry["printType"], entry["printTypeValues"]
        
        return "", False, False

    # readJavaSourceFile - read the specified Java source code file, and store its file content in memory.
    def __readJavaSourceFile(self):
        try:
            with open(self.__sourceFilename) as f:
                for line in f:
                    self.__sourceFileContent += line
                
                f.close()

        except Exception as e:
            print(e)
            return False

        return True
    
    # extractLexemes - parses the provided file contents, and splits all words, characters, etc. into lexemes
    def __extractLexemes(self):
        # Regular Expression used to split the string into usable units (lexemes)
        splittingRegularExpression = "(\/\*|\*\/)|(\=|\+|-|\*|\/|\%|\!|\>|\<)+|( )|(\"|\')|(\(|\))|(\{|\})|(\[|\])|(\,|\;|\:)|((?<=[A-Za-z])\.)|(\n|\t)"
        initialLexemeExtract = re.split(splittingRegularExpression, self.__sourceFileContent)

        for entry in initialLexemeExtract:
            newLexeme = Token(entry, "")
            self.__fileLexemes.append(newLexeme)

        # # For each unit found, determine if a combination should be performed, a split, or kept as is.
        # for i, entry in enumerate(initialLexemeExtract):
        #     currentLexemeType, printType, printTypeValues = self.__searchPredefinedTokens(entry)

        #     # If the current lexeme type is not a text formatting character, proceed.
        #     if (currentLexemeType != "textFormattingCharacters" and (entry != None)):
        #         periodIndex = entry.find(".")

        #         # If the current lexeme contains a ".", determine if it is a legitimate float value, or a string with dots.
        #         if (periodIndex >= 0):
        #             try:
        #                 # Attempt to convert the lexeme into a float.
        #                 # If it succeeds, store the entry as a singular lexeme
        #                 floatTest = float(entry)
        #                 newLexeme = Token(entry, "")

        #                 self.__fileLexemes.append(newLexeme)

        #             except Exception as e:
        #                 # If the lexeme fails the float conversion, assume it is an alphanumeric representing a variable,
        #                 # Split the lexeme based on word grouping. 
        #                 wordSplit = re.split("([^a-zA-Z0-9//*/\*])", entry)

        #                 # Store each split value as a new lexeme
        #                 for word in wordSplit:
        #                     newLexeme = Token(word, "")
        #                     self.__fileLexemes.append(newLexeme)
        #         else:
        #             # If the lexeme does not contain a period, store the lexeme "as is".
        #             newLexeme = Token(entry, "")
        #             self.__fileLexemes.append(newLexeme)
        #     else:
        #         newLexeme = Token(entry, "")
        #         newLexeme.setTokenType(currentLexemeType)
        #         self.__fileLexemes.append(newLexeme)
    
    # identifyTokens - parse the file content, and identify the tokens within the file.
    def __identifyTokens(self):
        # Flags that determine if the current lexeme should be ignored/skipped.
        inQuotes = False            # inQuotes - a flag to indicate if the current lexeme should be considered a part of a literal.
        inCommentBlock = False      # inCommentBlock - a flag to indicate if the current lexeme should be considered a part of a comment block (i.e. ignored).

        # Loop through all extracted lexemes.
        for lexeme in self.__fileLexemes:
            if (lexeme.getTokenValue() != None):
                currentTokenType, printType, printTypeValues = self.__searchPredefinedTokens(lexeme.getTokenValue())

                # If the token is not a text formatting character (i.e. space, tab, new line, carriage return, etc.) and the lexeme length is longer than 0 (i.e. not null),
                # proceed with the further checks.
                # Otherwise, ignore the entry as a token.
                if ((currentTokenType != "textFormattingCharacters") and (len(lexeme.getTokenValue()) > 0)):
                    # If the lexeme is identified as a commentBlock token, 
                    # check and see if we need to either enter or exit a comment block.
                    # Set the inCommentBlock flag accordingly.
                    if (currentTokenType == "commentBlock"):
                        if (inCommentBlock):
                            inCommentBlock = False
                        else:
                            inCommentBlock = True
                    else:
                        # If we're not currently in a comment block, proceed with checks.
                        # Otherwise, skip the lexeme.
                        if (not inCommentBlock):
                            # If the lexeme is identified as a doubleQuotes token,
                            # check and see if we need to either enter or exit a literal.
                            # Set the inQuotes flag accordingly.
                            if (currentTokenType == "doubleQuotes"):
                                if (inQuotes):
                                    inQuotes = False

                                    lexeme.setTokenType("literal")
                                    lexeme.setTokenValueVisibility(False)

                                    self.__fileTokens.append(lexeme)
                                else:
                                    inQuotes = True
                            else:
                                # If we're not currently in a set of double quotes, proceed with checks.
                                # Otherwise, skip the lexeme.
                                if (not inQuotes):
                                    # If the token type was found in the predefined tokens list, store it.
                                    # Otherwise, the lexeme is either a variable or a numeric type. Identify it and store.
                                    if (currentTokenType != ""):
                                        # switch statements are not available in Python :/. Alas, we must use if/elif/else...
                                        # If the printType and printTypeValues flags are both set, store the token type as the lexeme itself,
                                        # and set the token value visibility flag as True.
                                        if (printType and printTypeValues):
                                            lexeme.setTokenType(currentTokenType)
                                            lexeme.setTokenValueVisibility(True)
                                        # If the printType flag is set, but the printTypeValues flag is not, 
                                        # store the token type as the found token type, and set the token value visibility flag to False.
                                        elif (printType and not printTypeValues):
                                            lexeme.setTokenType(currentTokenType)
                                            lexeme.setTokenValueVisibility(False)

                                        # Add the Token object (current a lexeme) to the file tokens list.
                                        self.__fileTokens.append(lexeme)

                                    else:
                                        # Test int compatibility
                                        # If successful, store the token as an intValue.
                                        # Otherwise, proceed to next test.
                                        try:
                                            intTest = int(lexeme.getTokenValue())

                                            lexeme.setTokenType("intVal")
                                            lexeme.setTokenValueVisibility(False)

                                            self.__fileTokens.append(lexeme)
                                        except:
                                            try:
                                                # Check float compatibility
                                                # If successful, store the token as a doubleValue. (In Python, float is what other languages consider a double, by default.)
                                                # Otherwise, proceed to next test.
                                                floatTest = float(lexeme.getTokenValue())

                                                lexeme.setTokenType("doubleVal")
                                                lexeme.setTokenValueVisibility(False)

                                                self.__fileTokens.append(lexeme)
                                            except:
                                                # The provided lexeme is not numeric, and has not been identified as any other token type.
                                                # Treat lexeme as a variable token.
                                                lexeme.setTokenType("var")
                                                lexeme.setTokenValueVisibility(False)

                                                self.__fileTokens.append(lexeme)
                else:
                    lexeme.setTokenType("textFormattingCharacters")
                    self.__fileTokens.append(lexeme)
        
        return True

    # parseJavaSourceFile - parse the provided Java source code file's content for lexemes and tokens.
    def parseJavaSourceFile(self):
        # Extract the lexemes from the file content.
        self.__extractLexemes()

        # Identify the tokens
        success = self.__identifyTokens()

        # If the Token Identification process was successful, return True.
        # Otherwise, return False.
        if (success):
            return True
        else:
            return False
    
    # isFileValid - returns the validFile flag value.
    def isFileValid(self):
        return self.__validFile

    # printSourceFile - prints the raw source file content, unadulterated.
    def printSourceFile(self):
        print("File Contents of %s:" % (self.__sourceFilename))
        print(self.__sourceFileContent)

    # printAnalyzedFile - prints the tokenized file, but formatted as close as possible to the source file (for easier comparison)
    def printAnalyzedFile(self):
        print("Analysis of %s:" % (self.__sourceFilename))

        for i, entry in enumerate(self.__fileTokens):
            if (i < len(self.__fileTokens) - 1):
                if (entry.getTokenValueVisibility()):
                    print(entry.getTokenValue(), end="")
                else:
                    print(entry.getTokenType(), end="")
            else:
                if (entry.getTokenValueVisibility()):
                    print(entry.getTokenValue())
                else:
                    print(entry.getTokenType())

    # printFileTokens - prints the tokenized file as a singular string, delimited by space.
    def printFileTokens(self):
        print("\nTokens of %s:" % (self.__sourceFilename))
        print("w =", end=" ")
        for entry in self.__fileTokens:
            if (entry.getTokenType() != "textFormattingCharacters"):
                if (entry.getTokenValueVisibility()):
                    print(entry.getTokenValue(), end=" ")
                else:
                    print(entry.getTokenType(), end=" ")
    
    # printPredefinedTokens - for troubleshooting, prints the stringified JSON content of tokens.json for comparison.
    def __printPredefinedTokens(self):
        for entry in self.__predefinedTokens:
            print(entry)
    
    # printExtractedLexemes - for troubleshooting, prints the lexemes identified within the source file.
    def __printExtractedLexemes(self):
        print("Extracted Lexemes:")
        for entry in self.__fileLexemes:
            entry.print()

    # printExtractedTokens - for troubleshooting, prints the tokens identified within the source file.
    def __printExtractedTokens(self):
        print("Extracted Tokens:")
        for entry in self.__fileTokens:
            entry.print()

# Token - an object representing a Lexeme/Token, and its attributes.
class Token:
    # Attributes
    __tokenValue = ""        # The literal value of the lexeme
    __tokenType = ""         # The token type identified for the lexeme
    __displayAsValue = True  # A flag which determines if the Token should be displayed as its literal value or its token type.

    # Constructor
    def __init__(self, newValue, newTokenType):
        self.__tokenValue = newValue            # Store the new value of the lexeme/token
        self.__tokenType = newTokenType         # Store the token type (or blank)
        self.__displayAsValue = True            # Assume that all tokens are displayed by their value (i.e. Lexeme value)

    # getTokenValue - returns the token/lexeme literal value
    def getTokenValue(self):
        return self.__tokenValue

    # setTokenType - sets the token type of the token/lexeme.
    def setTokenType(self, currentTokenType):
        self.__tokenType = currentTokenType
    
    # getTokenType - returns the token type of the lexeme/token.
    def getTokenType(self):
        return self.__tokenType

    # setTokenValueVisibility - sets the lexeme/token's value visibility (i.e. display the lexeme/token by its literal value or token type)
    def setTokenValueVisibility(self, tokenValueVisibility):
        self.__displayAsValue = tokenValueVisibility

    # getTokenValueVisibility - returns the lexem/token's value visibility
    def getTokenValueVisibility(self):
        return self.__displayAsValue
    
    # print - printst the token in a formatted fashion.
    def print(self):
        print("{tokenValue: %s, tokenType: %s, displayAsValue: %s}" % (repr(self.__tokenValue), self.__tokenType, str(self.__displayAsValue)))

# parseArgs - parses the provided arguments on script call.
def parseArgs():
    filename = ""

    # Parse through any provided arguments
    for i, arg in enumerate(sys.argv):
        if (i != 0):
            if ((arg == '--help') or (arg == '-h')):
                print("Help")
                print("-f, --file: the filename of a Java source code file.")
                print("-h, --help: this help guide.")
                print("The program will ask for a filename, if not provided.")
                exit()
            elif ((arg == '--file') or (arg == '-f')):
                filename = sys.argv[i + 1]

    return filename

# main - the main driver of the script.
def main():
    # Check the provided arguments for a filename.
    filename = parseArgs()

    # If no filename was provided via the call, request a filename at runtime.
    if (filename == ""):
        filename = input("What is the name of the Java soure code file you would like to test?")

    if (filename != ""):
        # Initialize a JavaSourceCodeLexicalAnalyzer object.
        javaSourceCodeLexicalAnalyzer = JavaSourceCodeLexicalAnalyzer(filename)

        javaSourceCodeLexicalAnalyzer.printSourceFile()

        # If the read was successful, proceed with parsing the content.
        if (javaSourceCodeLexicalAnalyzer.isFileValid):
            goodParse = javaSourceCodeLexicalAnalyzer.parseJavaSourceFile()

            if (goodParse):
                javaSourceCodeLexicalAnalyzer.printAnalyzedFile()
                javaSourceCodeLexicalAnalyzer.printFileTokens()
            else:
                print("An error occurred while parsing the file content.")

# Calling the driver...
main()