import Commands


class CodeWriter:
    def __init__(self, output_file):
        self.label_counters = {}
        self.file = None
        self.output_file = open(output_file, "w")

    def set_file_name(self, file):
        self.file = file

    def write_arithmetic(self, cmd):

        if cmd == "add":
            self.__stack_binary_op("A+D")
        elif cmd == "sub":
            self.__stack_binary_op("A-D")
        elif cmd == "neg":
            self.__stack_unary_op("-D")
        elif cmd == "eq":
            self.__stack_binary_boolean_op("JEQ")
        elif cmd == "gt":
            self.__stack_binary_boolean_op("JGT")
        elif cmd == "lt":
            self.__stack_binary_boolean_op("JLT")
        elif cmd == "and":
            self.__stack_binary_op("D&A")
        elif cmd == "or":
            self.__stack_binary_op("D|A")
        elif cmd == "not":
            self.__stack_unary_op("!D")

    def write_push_pop(self, command_type, segment, index):
        if segment == "constant":
            self.__at(index)
            self.__comp("D", "A")
            self.__push_stack()
            return

        if segment == "static":
            self.__at(self.file + "." + index)
            self.__comp("D", "M")
            self.__push_pop(command_type)
            return

        (segment_label, segment_type) = Commands.segment_label_type_map.get(segment)
        if segment_label:
            self.__at(segment_label)
            self.__comp("D", "M" if segment_type == Commands.SegmentType.POINTER else "A")
            self.__at(index)
            self.__comp("A", "D+A")
            self.__push_pop(command_type)
            return

    def __push_pop(self, command_type):
        if command_type == Commands.CommandTypes.C_PUSH:
            self.__comp("D", "M")
            self.__push_stack()
        else:
            self.__comp("D", "A")
            self.__at("pop_temp")
            self.__comp("M", "D")
            self.__pop_stack("D")
            self.__at("pop_temp")
            self.__comp("A", "M")
            self.__comp("M", "D")

    def __write(self, line):
        self.output_file.write(line + "\n")

    def __pop_stack(self, dest):
        self.__sp_dec("A")
        self.__comp(dest, "M")

    def __push_stack(self):
        self.__at("SP")
        self.__comp("A", "M")
        self.__comp("M", "D")
        self.__sp_inc("A")
        pass

    def __sp_dec(self, dest=""):
        self.__sp_op("-1", dest)

    def __sp_inc(self, dest=""):
        self.__sp_op("+1", dest)

    def __sp_op(self, op, dest=""):
        self.__at("SP")
        self.__comp(dest + "M", "M" + op)

    def __at(self, symbol_or_number):
        self.__write("\t@" + symbol_or_number)

    def __comp(self, dest, comp, jump=""):
        if dest:
            dest = dest + "="
        if jump:
            jump = ";" + jump
        self.__write("\t" + dest + comp + jump)

    def __stack_unary_op(self, op):
        self.__pop_stack("D")
        self.__comp("D", op)
        self.__push_stack()

    def __stack_binary_op(self, op):
        self.__pop_stack("D")
        self.__pop_stack("A")
        self.__comp("D", op)
        self.__push_stack()

    def __stack_binary_boolean_op(self, op):
        label = self.__get_new_label("BOOL_OP_")
        label_true = label + "_TRUE"
        label_done = label + "_DONE"
        self.__stack_binary_op("A-D")
        self.__pop_stack("D")
        self.__at(label_true)
        self.__comp("", "D", op)
        self.__comp("D", "0")  # false
        self.__jump_to(label_done)
        self.__label(label_true)
        self.__comp("D", "-1")  # true
        self.__label(label_done)
        self.__push_stack()

    def __jump_to(self, label):
        self.__at(label)
        self.__comp("", "0", "JMP")

    def __get_new_label(self, prefix):
        self.label_counters[prefix] = self.label_counters.get(prefix, 0) + 1
        return prefix + str(self.label_counters[prefix])

    def __label(self, label):
        self.__write("(" + label + ")")
