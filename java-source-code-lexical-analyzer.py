# java-source-lexical-analyzer.py - the main file of the project.
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
import os
import sys
import json
import re

class JavaSourceCodeLexicalAnalyzer:
    __sourceFilename = ""
    __sourceFileContent = ""
    __fileLexemes = []
    __fileTokens = []
    __predefinedTokens = []
    __validFile = False

    def __init__(self, filename):
        self.__sourceFilename = filename
        self.__sourceFileContent = ""
        self.__fileLexemes = []
        self.__fileTokens = []
        self.__validFile = self.__readJavaSourceFile()
        self.__loadTokens()

    def __loadTokens(self):
        tokensFilename = "tokens.json"

        try:
            with open(tokensFilename) as f:
                self.__predefinedTokens = json.load(f)

        except Exception as e:
            print(e)
            return False
        
        return True

    def __searchPredefinedTokens(self, targetToken):
        for entry in self.__predefinedTokens:
            if targetToken in entry["values"]:
                return entry["type"], entry["printType"], entry["printTypeValues"]
        
        return "", False, False

    # readJavaSourceFile
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
        # Regex used to split the file content into usable lexemes.
        initialLexemeExtract = re.split('([^\w//*/\*\%\+\-\!\.\=])', self.__sourceFileContent)

        # Remove blank spaces, split further lexemes where possible (i.e. word.word.word)
        for entry in initialLexemeExtract:
            currentLexemeType, printType, printTypeValues = self.__searchPredefinedTokens(entry)

            # If the current lexeme type is not a text formatting character, proceed.
            if (currentLexemeType != "textFormattingCharacters"):
                periodIndex = entry.find(".")

                # If the current lexeme contains a ".", determine if it is a legitimate float value, or a string with dots.
                if (periodIndex >= 0):
                    try:
                        # Attempt to convert the lexeme into a float.
                        # If it succeeds, store the entry as a singular lexeme
                        floatTest = float(entry)
                        newLexeme = Token(entry)

                        self.__fileLexemes.append(newLexeme)

                    except Exception as e:
                        # If the lexeme fails the float conversion, assume it is an alphanumeric representing a variable,
                        # Split the lexeme based on word grouping. 
                        wordSplit = re.split("([^a-zA-Z0-9//*/\*])", entry)

                        # Store each split value as a new lexeme
                        for word in wordSplit:
                            newLexeme = Token(word)
                            self.__fileLexemes.append(newLexeme)
                else:
                    # If the lexeme does not contain a period, store the lexeme "as is".
                    newLexeme = Token(entry)
                    self.__fileLexemes.append(newLexeme)
            else:
                newLexeme = Token(entry)
                newLexeme.setTokenType(currentLexemeType)
                self.__fileLexemes.append(newLexeme)


    def parseJavaSourceFile(self):
        # Flags that determine if the current lexeme should be ignored/skipped.
        inQuotes = False
        inCommentBlock = False
        
        # Extract the lexemes from the file content.
        self.__extractLexemes()

        # Loop through all extracted lexemes.
        for lexeme in self.__fileLexemes:
            currentTokenType, printType, printTypeValues = self.__searchPredefinedTokens(lexeme.getTokenValue())

            if ((currentTokenType != "textFormattingCharacters") and (len(lexeme.getTokenValue()) >= 1)):
                if (currentTokenType == "commentBlock"):
                    if (inCommentBlock):
                        inCommentBlock = False
                    else:
                        inCommentBlock = True
                else:
                    if (not inCommentBlock):
                        if (currentTokenType == "doubleQuotes"):
                            if (inQuotes):
                                inQuotes = False

                                lexeme.setTokenType("literal")
                                lexeme.setTokenValueVisibility(False)

                                self.__fileTokens.append(lexeme)
                            else:
                                inQuotes = True
                        else:
                            if (not inQuotes):
                                if (currentTokenType != ""):
                                    # switch statements are not available in Python. Alas, we must use if/elif/else...
                                    if (printType and printTypeValues):
                                        lexeme.setTokenType(lexeme)
                                        lexeme.setTokenValueVisibility(True)
                                        
                                    elif (printType and not printTypeValues):
                                        lexeme.setTokenType(currentTokenType)
                                        lexeme.setTokenValueVisibility(False)

                                    self.__fileTokens.append(lexeme)

                                else:
                                    # Token is most likely a variable or a numeric
                                    # Test int compatibility
                                    try:
                                        intTest = int(lexeme.getTokenValue())

                                        lexeme.setTokenType("intVal")
                                        lexeme.setTokenValueVisibility(False)

                                        self.__fileTokens.append(lexeme)
                                    except:
                                        try:
                                            # Check float compatibility
                                            floatTest = float(lexeme.getTokenValue())

                                            lexeme.setTokenType("doubleVal")
                                            lexeme.setTokenValueVisibility(False)

                                            self.__fileTokens.append(lexeme)
                                        except:
                                            # Treat as variable
                                            lexeme.setTokenType("var")
                                            lexeme.setTokenValueVisibility(False)

                                            self.__fileTokens.append(lexeme)
            else:
                lexeme.setTokenType("textFormattingCharacters")
                self.__fileTokens.append(lexeme)
        
        return True
    
    def isFileValid(self):
        return self.__validFile

    def printSourceFile(self):
        print(self.__sourceFileContent)

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

    def printFileTokens(self):
        print("\nTokens of %s:" % (self.__sourceFilename))
        print("w =", end=" ")
        for entry in self.__fileTokens:
            if (entry.getTokenType() != "textFormattingCharacters"):
                if (entry.getTokenValueVisibility()):
                    print(entry.getTokenValue(), end=" ")
                else:
                    print(entry.getTokenType(), end=" ")
    
    def __printPredefinedTokens(self):
        for entry in self.__predefinedTokens:
            print(entry)
    
    def __printExtractedLexemes(self):
        for entry in self.__fileLexemes:
            print(entry)

class Token:
    __tokenValue = ""
    __tokenType = ""
    __displayAsValue = True

    def __init__(self, newValue):
        self.__tokenValue = newValue
        self.__tokenType = ""
        self.__displayAsValue = True

    def getTokenValue(self):
        return self.__tokenValue

    def setTokenType(self, currentTokenType):
        self.__tokenType = currentTokenType
    
    def getTokenType(self):
        return self.__tokenType

    def setTokenValueVisibility(self, tokenValueVisibility):
        self.__displayAsValue = tokenValueVisibility

    def getTokenValueVisibility(self):
        return self.__displayAsValue

def parseArgs():
    print("parseArgs")

def main():
    # Initialize a JavaSourceCodeLexicalAnalyzer object.
    filename = "Test.java"
    javaSourceCodeLexicalAnalyzer = JavaSourceCodeLexicalAnalyzer(filename)

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