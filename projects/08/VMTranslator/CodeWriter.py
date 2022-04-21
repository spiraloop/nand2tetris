import Commands


class CodeWriter:
    def __init__(self, output_file):
        self.label_counters = {}
        self.file = None
        self.output_file = open(output_file, "w")

    def set_file_name(self, file):
        self.file = file

    def write_init(self):
        self.__get_address("256")
        self.__set_value("SP")
        self.write_call("Sys.init", 0)
        # self.__jump_to("Sys.init")

    def write_arithmetic(self, cmd):

        if cmd == "add":
            self.__binary_op("A+D")
        elif cmd == "sub":
            self.__binary_op("A-D")
        elif cmd == "neg":
            self.__unary_op("-D")
        elif cmd == "eq":
            self.__binary_boolean_op("JEQ")
        elif cmd == "gt":
            self.__binary_boolean_op("JGT")
        elif cmd == "lt":
            self.__binary_boolean_op("JLT")
        elif cmd == "and":
            self.__binary_op("D&A")
        elif cmd == "or":
            self.__binary_op("D|A")
        elif cmd == "not":
            self.__unary_op("!D")

    def write_push_pop(self, command_type, segment, index):
        if segment == "constant":
            self.__push_address(index)
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

    def write_label(self, label):
        self.__label(label)

    def write_goto(self, label):
        self.__goto(label)

    def write_if(self, label):
        self.__pop("D")
        self.__at(label)
        self.__comp("", "D", "JNE")

    def write_call(self, f, n):
        return_label = self.__get_new_label("RETURN_")
        self.__push_address(return_label)
        self.__push_value("LCL")
        self.__push_value("ARG")
        self.__push_value("THIS")
        self.__push_value("THAT")
        self.__get_value("SP")
        self.__at_comp(str(n), "D", "D-A")
        self.__at_comp("5", "D", "D-A")
        self.__set_value("ARG")
        self.__get_value("SP")
        self.__set_value("LCL")
        self.__goto(f)
        self.__label(return_label)

    def write_return(self):
        # store frame in temp var
        self.__get_value("LCL")
        frame = "R13"
        self.__set_value(frame)

        # store return-address (frame-5) in temp var
        self.__at_comp("5", "A", "D-A")
        self.__comp("D", "M")
        ret = "R14"
        self.__set_value(ret)

        # set the return value in ARG
        self.__pop("D")
        self.__get_value("ARG", "A")
        self.__comp("M", "D")

        # restore SP
        self.__at_comp("ARG", "D", "M+1")
        self.__set_value("SP")

        def restore(label, offset):
            self.__get_value(frame)
            self.__at_comp(offset, "A", "D-A")
            self.__comp("D", "M")
            self.__set_value(label)

        restore("THAT", "1")
        restore("THIS", "2")
        restore("ARG", "3")
        restore("LCL", "4")

        self.__get_value(ret, "A")
        self.__comp("", "0", "JMP")

    def write_function(self, f, k):
        self.__label(f)
        self.__comp("D", "0")
        for _ in range(k):
            self.__push()

    def __get_value(self, at, dest="D"):
        self.__at_comp(at, dest, "M")

    def __get_address(self, at, dest="D"):
        self.__at_comp(at, dest, "A")

    def __set_value(self, at, source="D"):
        self.__at_comp(at, "M", source)

    def __at_comp(self, at, dest, comp, jump=""):
        self.__at(at)
        self.__comp(dest, comp, jump)

    # doesn't make sense, right?
    # def __set_address(self, at, source):
    #     self.__get_set(at, "A", source)

    def __goto(self, label):
        self.__at(label)
        self.__comp("", "0", "JMP")

    def __push_pop(self, command_type):
        if command_type == Commands.CommandTypes.C_PUSH:
            self.__comp("D", "M")
            self.__push()
        else:
            self.__comp("D", "A")
            self.__at("R13")
            self.__comp("M", "D")
            self.__pop("D")
            self.__at("R13")
            self.__comp("A", "M")
            self.__comp("M", "D")

    def __write(self, line):
        self.output_file.write(line + "\n")

    def __push_address(self, label):
        self.__at(label)
        self.__comp("D", "A")
        self.__push()

    def __push_value(self, label):
        self.__at(label)
        self.__comp("D", "M")
        self.__push()

    def __pop(self, dest):
        self.__sp_dec("A")
        self.__comp(dest, "M")

    def __push(self):
        self.__at("SP")
        self.__comp("A", "M")
        self.__comp("M", "D")
        self.__sp_inc("A")

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

    def __unary_op(self, op):
        self.__pop("D")
        self.__comp("D", op)
        self.__push()

    def __binary_op(self, op):
        self.__pop("D")
        self.__pop("A")
        self.__comp("D", op)
        self.__push()

    def __binary_boolean_op(self, op):
        label = self.__get_new_label("BRANCH_")
        label_true = label + "_TRUE"
        label_done = label + "_END"
        self.__binary_op("A-D")
        self.__pop("D")
        self.__at(label_true)
        self.__comp("", "D", op)
        self.__comp("D", "0")  # false
        self.__jump_to(label_done)
        self.__label(label_true)
        self.__comp("D", "-1")  # true
        self.__label(label_done)
        self.__push()

    def __jump_to(self, label):
        self.__at(label)
        self.__comp("", "0", "JMP")

    def __get_new_label(self, prefix):
        self.label_counters[prefix] = self.label_counters.get(prefix, 0) + 1
        return prefix + str(self.label_counters[prefix])

    def __label(self, label):
        self.__write("(" + label + ")")
