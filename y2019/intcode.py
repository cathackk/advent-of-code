from enum import Enum
from typing import Any, Callable, Generator, Iterable, Optional, Self

from tqdm import tqdm

Tape = list[int]

class OperationCode(Enum):
    # writes (a1 + a2) to a3
    ADD = (1, 3)
    # writes (a1 * a2) to a3
    MULTIPLY = (2, 3)
    # writes value from input to a1
    INPUT = (3, 1)
    # outputs value from a3
    OUTPUT = (4, 1)
    # if a1 <> 0, jump to a2
    JUMP_IF_TRUE = (5, 2)
    # if a1 == 0, jump to a2
    JUMP_IF_FALSE = (6, 2)
    # write 1 to a3 if a1 < a2; write 0 otherwise
    LESS_THAN = (7, 3)
    # write 1 to a3 if a1 == a2; write 0 otherwise
    EQUALS = (8, 3)
    # adjusts rbase by a1
    ADD_TO_RBASE = (9, 1)
    # halts execution
    HALT = (99, 0)

    def __init__(self, intcode: int, argcount: int):
        self.intcode = intcode
        self.argcount = argcount

    @classmethod
    def from_code(cls, code: int) -> Self:
        opcode = next((op for op in cls if op.intcode == code), None)
        if not opcode:
            raise KeyError(f"OperationCode with code={code} not found")
        return opcode


class Mode(Enum):
    ADDRESS = 0
    VALUE = 1
    RELATIVE = 2


class Argument:
    def __init__(self, value: int, mode: Mode):
        self.value = value
        self.mode = mode

    def __str__(self):
        if self.mode == Mode.ADDRESS:
            return f"[{self.value}]"
        elif self.mode == Mode.VALUE:
            return str(self.value)
        elif self.mode == Mode.RELATIVE:
            return f"[R+{self.value}]"
        else:
            raise ValueError(f"unsupported mode {self.mode}")


class Instruction:
    def __init__(self, opcode: OperationCode, args: Iterable[Argument]):
        self.opcode = opcode
        self.args = tuple(args)
        assert len(self.args) == self.opcode.argcount

    def __str__(self) -> str:
        return f"{self.opcode.name}({', '.join(str(arg) for arg in self.args)})"


class Halt(Exception):
    pass


# yields optional ints:
#   - yielded None = asking for input
#   - yielded int = output
#
# can be sent int (when asking for it by yielding None) = input
RunCoroutine = Generator[int | None, int, None]


class Machine:
    def __init__(
        self,
        tape: Iterable[int],
        name: str = None,
        *,
        debug: bool = False,
        progress: bool = False,
    ):
        self.tape = list(tape)
        self.memory: Tape = []
        self.rbase = 0
        self.head = -1
        self.tick = -1

        self.name = name
        self.debug = debug
        self.progress = progress

    def log(self, message: Any = ""):
        if self.debug:
            if self.name:
                print(f"[{self.name} {self.tick}] {message}")
            else:
                print(f"[{self.tick}] {message}")

    def _restart(self):
        self.memory = list(self.tape)
        self.rbase = 0
        self.head = 0
        self.tick = 0

    def run_coroutine(self) -> RunCoroutine:
        """
        yields None -> asks for input (int) to be sent in
        yields int -> output
        """
        self._restart()

        if self.progress:
            progress = tqdm(
                desc=f"running {self.name or 'intcode'}", unit=" steps", unit_scale=True, delay=1.0
            )
        else:
            progress = None

        try:
            while True:
                out_value = yield from self._step()
                if progress is not None:
                    progress.update()
                if out_value is not None:
                    yield out_value
        except Halt:
            self.log("halting")

    def _step(self) -> Generator[None, int, int]:
        """returns output (if any)"""

        self.tick += 1
        self.log(f"> head={self.head}")

        instr = self.scan_instruction()
        self.log(f"> instr={instr}")

        out_value = yield from self.evaluate(instr)
        if out_value is not None:
            self.log(f"> out={out_value}")

        return out_value

    def run_through(self) -> Tape:
        """
        Simple diagnostic run that assumes no input or output and returns the final memory state.
        """
        co = self.run_coroutine()
        try:
            next(co)
            assert False
        except StopIteration:
            return list(self.memory)

    def run_io(self) -> 'MachineIO':
        return MachineIO(self.run_coroutine())

    def run_output_only(self) -> Iterable[int]:
        return self.run_io().read()

    def run_fixed_input(self, ins: Iterable[int]) -> Generator[int, None, None]:
        ins_it = iter(ins)
        co = self.run_coroutine()
        io = next(co)
        while True:
            if io is not None:
                # output
                yield io
                io = next(co)
            else:
                # input
                io = co.send(next(ins_it))

    def run_control(self, initial_state: int = 0) -> Generator[int, int | None, None]:
        ctrl_state = initial_state
        co = self.run_coroutine()
        io = next(co)
        try:
            while True:
                if io is not None:
                    # signals output
                    # -> output the value check for control change
                    ctrl = yield io
                    if ctrl is not None:
                        ctrl_state = ctrl
                    io = next(co)
                else:
                    # signals input
                    # -> feed it control state
                    io = co.send(ctrl_state)

        except StopIteration:
            return

    def as_function(
        self, *,
        out_count: int = None,
        init: Iterable[int] = (),
        restarting: bool = False
    ) -> Callable[..., tuple[int, ...]]:
        assert out_count is None or out_count > 0

        if restarting:
            def func(*args: int) -> tuple[int, ...]:
                io = self.run_io()
                io.write(init)
                io.write(args)
                return tuple(io.read(max_count=out_count))

            return func

        else:
            io = self.run_io()
            io.write(init)

            def func(*args: int) -> tuple[int, ...]:
                io.write(args)
                return tuple(io.read(max_count=out_count))

            return func

    def as_function_scalar(
        self, *,
        init: Iterable[int] = (),
        restarting: bool = False
    ) -> Callable[..., int]:
        fn_vector = self.as_function(out_count=1, init=init, restarting=restarting)

        def fn_scalar(*args: int) -> int:
            return fn_vector(*args)[0]

        return fn_scalar

    def scan_instruction(self) -> Instruction:
        code = self.scan_single()
        self.log(f"> op={code}")

        opcode = OperationCode.from_code(code % 100)
        # self.log(f"> opcode={opcode}")

        inst_str = str(code).zfill(2 + opcode.argcount)
        arg_values = list(self.scan_multi(opcode.argcount))
        arg_modes = [Mode(int(c)) for c in inst_str[-3::-1]]
        args = [Argument(v, m) for v, m in zip(arg_values, arg_modes)]
        # self.log(f"> args=[{', '.join(str(arg) for arg in args)}]")

        return Instruction(opcode, args)

    def scan_single(self) -> int:
        value = self.read_memory(self.head)
        self.head += 1
        return value

    def scan_multi(self, cnt: int) -> Iterable[int]:
        for _ in range(cnt):
            yield self.scan_single()

    def value(self, arg: Argument) -> int:
        if arg.mode == Mode.ADDRESS:
            address = arg.value
            return self.read_memory(address)
        elif arg.mode == Mode.VALUE:
            return arg.value
        elif arg.mode == Mode.RELATIVE:
            address = self.rbase + arg.value
            return self.read_memory(address)
        else:
            raise ValueError(f"unsupport mode {arg.mode}")

    def read_memory(self, address: int) -> int:
        self._extend_memory_to(address)
        return self.memory[address]

    def write_memory(self, arg: Argument, value: int) -> None:
        if arg.mode == Mode.ADDRESS:
            address = arg.value
        elif arg.mode == Mode.RELATIVE:
            address = self.rbase + arg.value
        else:
            raise ValueError(f"unsupport mode {arg.mode}")
        self._extend_memory_to(address)
        self.memory[address] = value

    def _extend_memory_to(self, address: int):
        assert address >= 0
        if address >= len(self.memory):
            self.memory.extend([0] * (1 + address - len(self.memory)))

    def evaluate(self, instr: Instruction) -> Generator[None, int, int | None]:
        """
        yields  None = asks for input (int) to be sent
        returns int  = output
        returns None = no output
        """

        match instr.opcode:
            case OperationCode.ADD:
                src_1, src_2, target = instr.args
                val_1 = self.value(src_1)
                val_2 = self.value(src_2)
                result = val_1 + val_2
                self.write_memory(instr.args[2], result)
                self.log(f">> {src_1} + {src_2} -> {target} ({val_1} + {val_2} = {result})")

            case OperationCode.MULTIPLY:
                src_1, src_2, target = instr.args
                val_1 = self.value(src_1)
                val_2 = self.value(src_2)
                result = val_1 * val_2
                self.write_memory(target, result)
                self.log(f">> {src_1} * {src_2} -> {target} ({val_1} * {val_2} = {result})")

            case OperationCode.INPUT:
                # yields None = asks for input
                target, = instr.args
                value = yield
                self.write_memory(target, value)
                self.log(f">> input -> {target} ({value})")

            case OperationCode.OUTPUT:
                source, = instr.args
                value = self.value(source)
                self.log(f">> output <- {source} ({value})")
                # returns value = output
                return value

            case OperationCode.JUMP_IF_TRUE:
                cond_src, jump_src = instr.args
                cond_val = self.value(cond_src)
                if cond_val:
                    jump_target = self.value(jump_src)
                    self.log(f">> {cond_src} ?>> {jump_src} ({cond_val} >> {jump_target})")
                    self.head = jump_target
                else:
                    self.log(f">> {cond_src} ?>> {jump_src} ({cond_val})")

            case OperationCode.JUMP_IF_FALSE:
                cond_src, jump_src = instr.args
                cond_val = self.value(cond_src)
                if not cond_val:
                    jump_target = self.value(jump_src)
                    self.log(f">> {cond_src} !>> {jump_src} ({cond_val} >> {jump_target})")
                    self.head = jump_target
                else:
                    self.log(f">> {cond_src} !>> {jump_src} ({cond_val})")

            case OperationCode.LESS_THAN:
                src_1, src_2, target = instr.args
                val_1 = self.value(src_1)
                val_2 = self.value(src_2)
                result = int(val_1 < val_2)
                self.write_memory(target, result)
                self.log(f">> {src_1} < {src_2} -> {target} ({val_1} < {val_2} -> {result})")

            case OperationCode.EQUALS:
                src_1, src_2, target = instr.args
                val_1 = self.value(src_1)
                val_2 = self.value(src_2)
                result = int(val_1 == val_2)
                self.write_memory(target, result)
                self.log(f">> {src_1} = {src_2} -> {target} ({val_1} = {val_2} -> {result})")

            case OperationCode.ADD_TO_RBASE:
                source, = instr.args
                value = self.value(source)
                self.log(f">> R + {source} -> R ({self.rbase} + {value} -> {self.rbase + value})")
                self.rbase += value

            case OperationCode.HALT:
                self.log(f">> HALT")
                raise Halt()

            case other:
                raise ValueError(f"Unsupported opcode {other}")


def load_tape(fn) -> Tape:
    return [int(v) for line in open(fn) for v in line.strip().split(',') if v]


class IOState(Enum):
    INPUT = 1
    OUTPUT = 2
    STOPPED = 3


class MachineIO:
    def __init__(self, coroutine: RunCoroutine):
        self.co = coroutine
        self.last_signal, self._stop = self._send()

    def _send(self, sent_value: int = None) -> tuple[Optional[int], Optional[StopIteration]]:
        try:
            yielded = self.co.send(sent_value)
            return yielded, None
        except StopIteration as exc:
            return None, exc

    def has_more(self):
        return self._stop is None

    def can_write(self) -> bool:
        return self.has_more() and self.last_signal is None

    def can_read(self) -> bool:
        return self.has_more() and self.last_signal is not None

    @property
    def state(self) -> IOState:
        if not self.has_more():
            return IOState.STOPPED
        elif self.can_read():
            return IOState.OUTPUT
        elif self.can_write():
            return IOState.INPUT
        else:
            raise ValueError("wrong state")

    def write(self, values: str | Iterable[int]):
        for value in MachineIO._ints(values):
            self.write_single(value)

    def write_single(self, value: int):
        if self._stop:
            raise self._stop
        assert self.can_write(), f"cannot write: last signal didn't indicate input"
        self.last_signal, self._stop = self._send(value)

    def read(self, max_count: int = None) -> Iterable[int]:
        assert max_count is None or max_count > 0
        yielded_count = 0
        while self.can_read():
            yield self.read_single()
            yielded_count += 1
            if max_count and yielded_count >= max_count:
                return

    def read_str(self) -> str:
        return ''.join(chr(v) for v in self.read())

    def read_single(self) -> int:
        if self._stop:
            raise self._stop
        assert self.can_read(), f"cannot read: last signal didn't indicate output"
        output = self.last_signal
        self.last_signal, self._stop = self._send()
        return output

    @staticmethod
    def _ints(values: str | Iterable[int]) -> Iterable[int]:
        if isinstance(values, str):
            return (ord(c) for c in values)
        else:
            return values


def test_coroutine_repeater():
    m = Machine(name="repeater", tape=[
        3, 7,
        4, 7,
        1105, 1, 0,
        0
    ])

    co = m.run_coroutine()
    assert next(co) is None  # in
    assert co.send(0) == 0   # out
    assert next(co) is None
    assert co.send(5) == 5


def test_as_function_increment_by_1():
    # increments input by 1
    m = Machine(name="incrementer", tape=[
        3, 11,
        101, 1, 11, 11,
        4, 11,
        1105, 1, 0,
        0
    ])

    f = m.as_function_scalar()
    assert f(1) == 2
    assert f(10) == 11
    assert f(100) == 101


def test_as_function_multiply_by_x():
    # initialize with X
    # then multiplies each input by X
    m = Machine(name="multiplier", tape=[
        3, 13,
        3, 14,
        2, 13, 14, 14,
        4, 14,
        1105, 1, 2,
        0, 0
    ])

    multiply_by_4 = m.as_function_scalar(init=[4])
    assert multiply_by_4(2) == 8
    assert multiply_by_4(10) == 40
    assert multiply_by_4(0) == 0

    multiply_by_7 = m.as_function_scalar(init=[7])
    assert multiply_by_7(2) == 14
    assert multiply_by_7(-10) == -70


def test_as_function_sum():
    m = Machine(name="sum", tape=[
        3, 11,          # input -> [11]
        1, 11, 12, 12,  # [11] + [12] -> [12]
        4, 12,          # output <- [12]
        1105, 1, 0,     # goto [0]
        # [11..12]
        0, 0
    ])

    f = m.as_function_scalar()
    assert f(2) == 2
    assert f(8) == 10
    assert f(90) == 100

    f = m.as_function_scalar()
    assert f(0) == 0
    assert f(15) == 15
    assert f(-14) == 1
    assert f(-3) == -2


def test_as_function_2to1():
    m = Machine(name="add two", tape=[
        3, 20,          # in -> [20]
        3, 21,          # in -> [21]
        1, 20, 21, 22,  # [20] + [21] -> [22]
        4, 22,          # out <- [22]
        1105, 1, 0      # goto [0]
    ])

    f = m.as_function_scalar()
    assert f(1, 1) == 2
    assert f(15, 45) == 60
    assert f(-100, 99) == -1
    assert f(0, 0) == 0
    assert f(0, 13) == 13

    f = m.as_function()
    assert f(1, 1) == (2,)
    assert f(100, 200) == (300,)


def test_as_function_1to3():
    m = Machine(name="0T2T4", tape=[
        3, 20,           # int -> [20]
        104, 0,          # out <- 0
        102, 2, 20, 20,  # 2 * [20] -> [20]
        4, 20,           # out <- [20]
        102, 2, 20, 20,  # 2 * [20] -> [20]
        4, 20,           # out <- [20]
        1105, 1, 0       # goto [0]
    ])

    f = m.as_function()
    assert f(1) == (0, 2, 4)
    assert f(10) == (0, 20, 40)
    assert f(-100) == (0, -200, -400)

    f = m.as_function(out_count=3)
    assert f(2) == (0, 4, 8)
    assert f(20) == (0, 40, 80)


def test_as_function_2to_2():
    m = Machine(name="swap", tape=[
        3, 20,
        3, 21,
        4, 21,
        4, 20,
        1105, 1, 0
    ])

    f = m.as_function()
    assert f(1, 2) == (2, 1)
    assert f(-10, 20) == (20, -10)
    assert f(333, 0) == (0, 333)


def test_as_function_0to3():
    m = Machine(name="threes", tape=[
        101, 1, 30, 30,
        4, 30,
        101, 1, 30, 30,
        4, 30,
        101, 1, 30, 30,
        4, 30,
        1105, 1, 0
    ])

    f = m.as_function(out_count=3)
    assert f() == (1, 2, 3)
    assert f() == (4, 5, 6)
    assert f() == (7, 8, 9)


def test_as_function_restarting():
    m = Machine(name="add_single", tape=[
        3, 20,
        3, 21,
        1, 20, 21, 22,
        4, 22,
        99
    ])

    f = m.as_function_scalar(restarting=False)
    assert f(1, 2) == 3
    try:
        f(4, 5)
        assert False
    except StopIteration:
        pass

    fr = m.as_function_scalar(restarting=True)
    assert fr(6, 7) == 13
    assert fr(8, 9) == 17


def test_write_rbase():
    m = Machine([
        109, 50,              # R + 50 -> R (50)
        21101, 666, 777, 40,  # 666 + 777 -> [R+40]
        109, -20,             # R - 20 -> R (30)
        204, 60,              # output <- [R+60]
        99                    # HALT
    ])
    assert list(m.run_output_only()) == [666+777]


def test_run_control():
    m = Machine(name="turbo", tape=[
        3, 31,
        1, 30, 31, 30,
        4, 30,
        1105, 1, 0
    ])

    co = m.run_control(1)
    assert next(co) == 1
    assert next(co) == 2
    assert next(co) == 3
    assert co.send(5) == 8
    assert next(co) == 13
    assert next(co) == 18
    assert co.send(3) == 21
    assert co.send(-1) == 20
    assert next(co) == 19
    assert next(co) == 18
    assert co.send(-10) == 8
    assert next(co) == -2
    assert co.send(1) == -1
    assert next(co) == 0
    assert co.send(0) == 0
    assert next(co) == 0
    assert next(co) == 0


def test_io2():
    m = Machine(name="test_io2", tape=[
        104, 5,
        104, 3,
        104, 10,
        104, 10,
        104, 66,
        104, 10,
        3, 100,
        3, 101,
        4, 100,
        4, 100,
        4, 101,
        1105, 1, 12,
    ])
    io = m.run_io()
    assert list(io.read()) == [5, 3, 10, 10, 66, 10]

    io.write('ab')
    assert io.read_str() == 'aab'

    io.write([666, 777])
    assert list(io.read()) == [666, 666, 777]
