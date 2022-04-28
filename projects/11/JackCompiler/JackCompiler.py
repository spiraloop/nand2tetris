#!/usr/local/bin/python3
import os.path
import sys
import xml.etree.ElementTree as xml
from pathlib import Path
import argparse


import Tokenizer
import CompilationEngine


def lookup_files(arg):
    if arg.endswith('.jack'):
        return [Path(arg)]
    else:
        path = Path(arg)
        return list(Path(arg).resolve().glob("*.jack"))


def parse_tokens(file_path):
    with open(file_path, "r") as file:
        tokenizer = Tokenizer.Tokenizer(file, file_path)
        token_list = []
        while tokenizer.type is not None:
            token_list.append(tokenizer.get_token())
            tokenizer.advance()
        return token_list


def export_tokens(token_list, file_path):
    tokens = xml.Element("tokens")
    tokens.text = "\n"
    for token in token_list:
        node = xml.SubElement(tokens, str(token.type))
        node.text = " " + str(token.value) + " "
        node.tail = "\n"
    with open(file_path, "wb") as output_file:
        xml.ElementTree(tokens).write(output_file)
        output_file.write('\n'.encode('utf-8'))


def compile_to_file(token_list, output_file_path='out'):
    with open(output_file_path, "w") as out_file:
        compilation_engine = CompilationEngine.CompilationEngine(token_list, out_file)
        compilation_engine.compile()


def main():
    parser = argparse.ArgumentParser(description='Jack compiler.')
    parser.add_argument('target', help="Path to jack file or folder to compile")
    parser.add_argument('-t', '--export_tokens', action='store_true', help="Export the tokens to an XML file")
    parser.add_argument('-o', '--output_folder', help="Relative path for output folder", default="out")
    args = parser.parse_args()

    input_files = lookup_files(args.target)

    if len(input_files) < 1:
        print("No .jack files found")
        sys.exit(2)

    output_folder = os.path.join(args.target if os.path.isdir(args.target) else os.path.dirname(args.target), args.output_folder)
    os.makedirs(output_folder, exist_ok=True)

    for input_file_path in input_files:
        print("# Compiling " + input_file_path.name + "...")
        token_list = parse_tokens(input_file_path)
        if args.export_tokens:
            output_file_name = input_file_path.name.replace(".jack", "T.xml")
            export_tokens(token_list, os.path.join(output_folder, output_file_name))
        try:
            output_file_name = input_file_path.name.replace(".jack", ".vm")
            compile_to_file(token_list, os.path.join(output_folder, output_file_name))

        except CompilationEngine.CompilationError as error:
            print("Error in " + input_file_path.__str__() + (":" + error.token.line_number.__str__() if error.token is not None else ""))
            print(error.message)


main()
