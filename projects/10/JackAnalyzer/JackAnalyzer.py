#!/usr/local/bin/python3

import sys
import xml.etree.ElementTree as xml
from pathlib import Path

import Tokenizer
import CompilationEngine


def input_error(error):
    print(error)
    print("Usage JackAnalyzer [<dir>|<file.vm>]")
    sys.exit(2)


def lookup_files(arg):
    if arg.endswith('.jack'):
        return [arg]
    else:
        path = Path(arg)
        return list(Path(arg).resolve().glob("*.jack"))


def analyze_tokens(file_path):
    with open(file_path, "r") as file:
        tokenizer = Tokenizer.Tokenizer(file, file_path)
        tokens = xml.Element("tokens")
        tokens.text = "\n"
        token_list = []
        while tokenizer.type is not None:
            token = xml.SubElement(tokens, tokenizer.type.value)
            token.text = " " + str(tokenizer.value) + " "
            token.tail = "\n"
            token_list.append(tokenizer.get_token())
            tokenizer.advance()
        with open(file_path.__str__().replace(".jack", "T.xml"), "wb") as tokens_xml_file:
            xml.ElementTree(tokens).write(tokens_xml_file)
            tokens_xml_file.write('\n'.encode('utf-8'))
        return token_list


def analyze_compilation(file_path, token_list):
    with open(file_path, "r") as file, open(file_path.__str__().replace(".jack", ".xml"), "w") as compilation_xml_file:
        compilation_engine = CompilationEngine.CompilationEngine(token_list, compilation_xml_file)
        compilation_engine.compile()


def main():
    if len(sys.argv) != 2:
        input_error("Missing input")

    input_files = lookup_files(sys.argv[1])

    if len(input_files) < 1:
        input_error("No .jack files found")

    for file in input_files:
        print("# Analyzing " + file.name + "...")
        token_list = analyze_tokens(file)
        try:
            analyze_compilation(file, token_list)

        except CompilationEngine.CompilationError as error:
            print("Error in " + file.__str__() + (":" + error.token.line_number.__str__() if error.token is not None else ""))
            print(error.message)


main()
