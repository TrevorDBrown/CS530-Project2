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
    sourceFilename = ""
    sourceFileContent = ""
    fileLexemes = []
    fileTokens = []
    predefinedTokens = []
    validFile = False

    def __init__(self, filename):
        self.sourceFilename = filename
        self.sourceFileContent = ""
        self.fileLexemes = []
        self.fileTokens = []
        self.validFile = False
        self.__loadTokens()

    def __loadTokens(self):
        tokensFilename = "tokens.json"

        try:
            with open(tokensFilename) as f:
                self.predefinedTokens = json.load(f)

        except Exception as e:
            print(e)
            return False
        
        return True

    def __searchPredefinedTokens(self, targetToken):
        for entry in self.predefinedTokens:
            if targetToken in entry["values"]:
                return entry["type"], entry["printType"], entry["printTypeValues"]
        
        return "", False, False

        
    def readJavaSourceFile(self):
        try:
            with open(self.sourceFilename) as f:
                for line in f:
                    self.sourceFileContent += line
                
                f.close()

        except Exception as e:
            print(e)
            return False

        return True
    
    def __extractLexemes(self):
        # Regex used to split the file content into usable lexemes.
        initialLexemeExtract = re.split('([^a-zA-Z0-9//*/\*\%\+\-\!\.\=])', self.sourceFileContent)

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
                        self.fileLexemes.append(entry)
                    except Exception as e:
                        # If the lexeme fails the float conversion, assume it is an alphanumeric representing a variable,
                        # Split the lexeme based on word grouping. 
                        wordSplit = re.split("([^a-zA-Z0-9//*/\*])", entry)

                        # Store each split value as a new lexeme
                        for word in wordSplit:
                            self.fileLexemes.append(word)
                else:
                    # If the lexeme does not contain a period, store the lexeme "as is".
                    self.fileLexemes.append(entry)
            else:
                self.fileLexemes.append(entry)


    def parseJavaSourceFile(self):
        # Flags that determine if the current lexeme should be ignored/skipped.
        inQuotes = False
        inCommentBlock = False
        
        # Extract the lexemes from the file content.
        self.__extractLexemes()

        # Loop through all extracted lexemes.
        for lexeme in self.fileLexemes:
            currentTokenType, printType, printTypeValues = self.__searchPredefinedTokens(lexeme)

            if ((currentTokenType != "textFormattingCharacters") and (len(lexeme) >= 1)):
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
                                self.fileTokens.append("literal")
                            else:
                                inQuotes = True
                        else:
                            if (not inQuotes):
                                if (currentTokenType != ""):
                                    # switch statements are not available in Python. Alas, we must use if/elif/else...
                                    if (printType and printTypeValues):
                                        self.fileTokens.append(lexeme)
                                    elif (printType and not printTypeValues):
                                        self.fileTokens.append(currentTokenType)
                                else:
                                    # Token is most likely a variable or a numeric
                                    # Test int compatibility
                                    try:
                                        intTest = int(lexeme)
                                        self.fileTokens.append("intVal")
                                    except:
                                        try:
                                            # Check float compatibility
                                            floatTest = float(lexeme)
                                            self.fileTokens.append("doubleVal")
                                        except:
                                            # Treat as variable
                                            self.fileTokens.append("var")
        
        return True

    def printSourceFile(self):
        print(self.sourceFileContent)

    # def printAnalyzedFile(self):
    #     print("Analysis of %s:" % (self.sourceFilename))

    #     for entry in self.fileTokens:
    #         print(entry, end=" ")

    def printFileTokens(self):
        print("w =", end=" ")
        for entry in self.fileTokens:
            print(entry, end=" ")
    
    def __printPredefinedTokens(self):
        for entry in self.predefinedTokens:
            print(entry)
    
    def __printExtractedLexemes(self):
        for entry in self.fileLexemes:
            print(entry)

# class Token:
#     __tokenValue = ""
#     __tokenType = ""
#     __displayAsValue = True

#     def __init__(self, newValue):
#         self.tokenValue = newValue
#         self.tokenType = ""
#         self.displayAsValue = False

#     def getTokenValue(self):
#         return self.__tokenValue

def parseArgs():
    print("parseArgs")

def main():
    # Initialize a JavaSourceCodeLexicalAnalyzer object.
    filename = "Test.java"
    javaSourceCodeLexicalAnalyzer = JavaSourceCodeLexicalAnalyzer(filename)

    # Read the defined file into the JavaSourceCodeLexicalAnalyzer object.
    goodRead = javaSourceCodeLexicalAnalyzer.readJavaSourceFile()

    # If the read was successful, proceed with parsing the content.
    if (goodRead):
        goodParse = javaSourceCodeLexicalAnalyzer.parseJavaSourceFile()

        if (goodParse):
            javaSourceCodeLexicalAnalyzer.printFileTokens()
        else:
            print("An error occurred while parsing the file content.")

# Calling the driver...
main()