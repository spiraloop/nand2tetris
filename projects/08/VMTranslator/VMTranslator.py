#!/usr/local/bin/python3

import sys
from pathlib import Path

import CodeWriter
import Commands
import Parser


def input_error(error):
    print(error)
    print("Usage VMTranslator [<dir>|<file.vm>]")
    sys.exit(2)


def lookup_files(arg):
    if arg.endswith('.vm'):
        return [arg], arg.replace(".vm", ".asm")
    else:
        path = Path(arg)
        return list(Path(arg).glob("*.vm")), arg + "/" + path.name + ".asm"


def translate_files(input_files, output_file):
    code_writer = CodeWriter.CodeWriter(output_file)

    # bootstrap
    code_writer.write_init()

    for file in input_files:
        translate(file, code_writer)


def translate(file, code_writer):
    parser = Parser.Parser(file)
    code_writer.set_file_name(parser.file_path.name)

    scope = ""

    def label_prefix():
        return scope + "$" if len(scope) > 0 else ""

    while parser.has_more_commands():

        if parser.command_type == Commands.CommandTypes.C_PUSH or parser.command_type == Commands.CommandTypes.C_POP:
            code_writer.write_push_pop(parser.command_type, parser.arg1, parser.arg2)

        elif parser.command_type == Commands.CommandTypes.C_ARITHMETIC:
            code_writer.write_arithmetic(parser.arg1)

        elif parser.command_type == Commands.CommandTypes.C_LABEL:
            code_writer.write_label(label_prefix() + parser.arg1)

        elif parser.command_type == Commands.CommandTypes.C_GOTO:
            code_writer.write_goto(label_prefix() + parser.arg1)

        elif parser.command_type == Commands.CommandTypes.C_IF:
            code_writer.write_if(label_prefix() + parser.arg1)

        elif parser.command_type == Commands.CommandTypes.C_FUNCTION:
            scope = str(parser.arg1)
            code_writer.write_function(scope, int(parser.arg2))

        elif parser.command_type == Commands.CommandTypes.C_RETURN:
            code_writer.write_return()

        elif parser.command_type == Commands.CommandTypes.C_CALL:
            code_writer.write_call(str(parser.arg1), int(parser.arg2))

        parser.advance()


def main():
    if len(sys.argv) != 2:
        input_error("Missing input")

    input_files, output_files = lookup_files(sys.argv[1])

    if len(input_files) < 1:
        input_error("No .vm files found")

    translate_files(input_files, output_files)


main()
