# CS530-Project2
An implementation of a lexical analyzer for Java source code. Written for CS 530 (Automata Theory and Compiler Construction), Fall 2020 semester, Western Kentucky University.

## Motivation
This project is designed to read in a Java source code file (.java files), identify lexemes within the file, as well as tokens. 

## Technical Requirements
In order to run the script as intended, you must have Python 3 installed. No additional modules are required.

## Installation
To install and run this application:
1. Install Python 3
2. Clone this repository to your local machine
3. Run python3 ./java-source-code-lexical-analyzer.py

## Usage
A few flags are available upon execution, to bypass direct input into the application on run.

**-f (or --file)** - the filename of your DFA file.
**-h (or --help)** - a listing of these flags.

If no flags are specified, prompts are given for the needed input.

## Java Source Code File Input
This application will analyze any general structure of a Java source code file. Since this is not a syntax analyzer, we can analyze an entire file with a class definition, or just a set of methods.

## Output
Once a valid Java source code file is read, the file's contents are printed in the console. Then, as parsing and analysis are performed on the file, two token listings are provided. One listing replaces the lexemes within the original source printing with the identified tokens, providing a mirrored printing formatted exactly like the source. The other listing is formatted as:

w = token0 token1 token2 ... tokenN

