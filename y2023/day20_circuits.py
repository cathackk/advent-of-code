"""
Advent of Code 2023
Day 20: Pulse Propagation
https://adventofcode.com/2023/day/20
"""

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Self

from common.file import relative_path
from common.iteration import dgroupby_pairs, diffs, single_value
from common.maths import lcm
from common.text import parse_line


def part_1(configuration: 'Configuration', pushes: int = 1000) -> int:
    """
    With your help, the Elves manage to find the right parts and fix all of the machines. Now, they
    just need to send the command to boot up the machines and get the sand flowing again.

    The machines are far apart and wired together with long **cables**. The cables don't connect to
    the machines directly, but rather to communication **modules** attached to the machines that
    perform various initialization tasks and also act as communication relays.

    Modules communicate using **pulses**. Each pulse is either a **high pulse** or a **low pulse**.
    When a module sends a pulse, it sends that type of pulse to each module in its list of
    **destination modules**.

    There are several different types of modules:

    **Flip-flop** modules (prefix `%`) are either **on** or **off**; they are initially **off**.
    If a flip-flop module receives a high pulse, it is ignored and nothing happens. However, if
    a flip-flop module receives a low pulse, it **flips between on and off**. If it was off, it
    turns on and sends a high pulse. If it was on, it turns off and sends a low pulse.

    **Conjunction** modules (prefix `&`) **remember** the type of the most recent pulse received
    from **each** of their connected input modules; they initially default to remembering a **low
    pulse** for each input. When a pulse is received, the conjunction module first updates its
    memory for that input. Then, if it remembers **high pulses** for all inputs, it sends a **low
    pulse**; otherwise, it sends a **high pulse**.

    There is a single **broadcast module** (named `broadcaster`). When it receives a pulse, it sends
    the same pulse to all of its destination modules.

    Here at Desert Machine Headquarters, there is a module with a single button on it called, aptly,
    the **button module**. When you push the button, a single **low pulse** is sent directly to the
    `broadcaster` module.

    After pushing the button, you must wait until all pulses have been delivered and fully handled
    before pushing it again. Never push the button if modules are still processing pulses.

    Pulses are always processed **in the order they are sent**. So, if a pulse is sent to modules
    `a`, `b`, and `c`, and then module `a` processes its pulse and sends more pulses, the pulses
    sent to modules `b` and `c` would have to be handled first.

    The module configuration (your puzzle input) lists each module. The name of the module is
    preceded by a symbol identifying its type, if any. The name is then followed by an arrow and
    a list of its destination modules. For example:

        >>> configuration_1 = Configuration.from_text('''
        ...     broadcaster -> a, b, c
        ...     %a -> b
        ...     %b -> c
        ...     %c -> inv
        ...     &inv -> a
        ... ''')

    In this module configuration, the broadcaster has three destination modules:

        >>> configuration_1.destinations['broadcaster']
        ['a', 'b', 'c']

    Each of these modules is a flip-flop module (as indicated by the `%` prefix):

        >>> {name: configuration_1.types[name] for name in ['a', 'b', 'c']}
        {'a': '%', 'b': '%', 'c': '%'}

    `a` outputs to `b` which outputs to `c` which outputs to another module named `inv`.

        >>> {name: configuration_1.destinations[name] for name in ['a', 'b', 'c']}
        {'a': ['b'], 'b': ['c'], 'c': ['inv']}


    `inv` is a conjunction module (as indicated by the `&` prefix):

        >>> configuration_1.types['inv']
        '&'

    It acts like an inverter because it has only one input (it sends the opposite of the pulse type
    it receives); it outputs to `a`.

        >>> configuration_1.destinations['inv']
        ['a']

    By pushing the button once, the following pulses are sent:

        >>> machine_1 = Machine(configuration_1)
        >>> _ = machine_1.push(log=True)
        button -low-> broadcaster
        broadcaster -low-> a
        broadcaster -low-> b
        broadcaster -low-> c
        a -high-> b
        b -high-> c
        c -high-> inv
        inv -low-> a
        a -low-> b
        b -low-> c
        c -low-> inv
        inv -high-> a

    After this sequence, the flip-flop modules all end up **off**, so pushing the button again
    repeats the same sequence.

        >>> machine_1.memory_flip_flops
        {'a': False, 'b': False, 'c': False}

    Here's a more interesting example:

        >>> configuration_2 = Configuration.from_text('''
        ...     broadcaster -> a
        ...     %a -> inv, con
        ...     &inv -> b
        ...     %b -> con
        ...     &con -> output
        ... ''')

    This module configuration includes the `broadcaster`, two flip-flops (named `a` and `b`),
    a single-input conjunction module (`inv`), a multi-input conjunction module (`con`), and
    an untyped module named `output` (for testing purposes).

        >>> configuration_2.types
        {'broadcaster': None, 'a': '%', 'inv': '&', 'b': '%', 'con': '&'}

    The multi-input conjunction module `con` watches the two flip-flop modules and, if they're both
    on, sends a **low pulse** to the `output` module.

        >>> {name: configuration_2.destinations[name] for name in ['a', 'b', 'con']}
        {'a': ['inv', 'con'], 'b': ['con'], 'con': ['output']}
        >>> machine_2 = Machine(configuration_2)
        >>> machine_2.memory_flip_flops
        {'a': False, 'b': False}
        >>> machine_2.memory_conjunctions
        {'inv': {'a': False}, 'con': {'a': False, 'b': False}}

    Here's what happens if you push the button once:

        >>> _ = machine_2.push(log=True)
        button -low-> broadcaster
        broadcaster -low-> a
        a -high-> inv
        a -high-> con
        inv -low-> b
        con -high-> output
        b -high-> con
        con -low-> output

    Both flip-flops turn on and a low pulse is sent to `output`! However, now that both flip-flops
    are on and `con` remembers a high pulse from each of its two inputs ...

        >>> machine_2.memory_flip_flops
        {'a': True, 'b': True}
        >>> machine_2.memory_conjunctions
        {'inv': {'a': True}, 'con': {'a': True, 'b': True}}

    ... pushing the button a second time does something different:

        >>> _ = machine_2.push(log=True)
        button -low-> broadcaster
        broadcaster -low-> a
        a -low-> inv
        a -low-> con
        inv -high-> b
        con -high-> output

    Flip-flop `a` turns off! Now, `con` remembers a low pulse from module `a`, and so it sends only
    a high pulse to `output`.

        >>> machine_2.memory_flip_flops
        {'a': False, 'b': True}
        >>> machine_2.memory_conjunctions
        {'inv': {'a': False}, 'con': {'a': False, 'b': True}}

    Push the button a third time:

        >>> _ = machine_2.push(log=True)
        button -low-> broadcaster
        broadcaster -low-> a
        a -high-> inv
        a -high-> con
        inv -low-> b
        con -low-> output
        b -low-> con
        con -high-> output

    This time, flip-flop `a` turns on, then flip-flop `b` turns off. However, before `b` can turn
    off, the pulse sent to `con` is handled first, so it **briefly remembers all high pulses** for
    its inputs and sends a low pulse to `output`. After that, flip-flop `b` turns off, which causes
    `con` to update its state and send a high pulse to `output`.

        >>> machine_2.memory_flip_flops
        {'a': True, 'b': False}
        >>> machine_2.memory_conjunctions
        {'inv': {'a': True}, 'con': {'a': True, 'b': False}}

    Finally, with `a` on and `b` off, push the button a fourth time:

        >>> _ = machine_2.push(log=True)
        button -low-> broadcaster
        broadcaster -low-> a
        a -low-> inv
        a -low-> con
        inv -high-> b
        con -high-> output

    This completes the cycle: `a` turns off, causing `con` to remember only low pulses and restoring
    all modules to their original states.

        >>> machine_2.memory_flip_flops
        {'a': False, 'b': False}
        >>> machine_2.memory_conjunctions
        {'inv': {'a': False}, 'con': {'a': False, 'b': False}}

    To get the cables warmed up, the Elves have pushed the button `1000` times. How many pulses got
    sent as a result (including the pulses sent by the button itself)?

    In the first example, the same thing happens every time the button is pushed: `8` low pulses and
    `4` high pulses are sent.

        >>> machine_1.push()
        (8, 4)

    So, after pushing the button `1000` times, `8000` low pulses and `4000` high pulses are sent:

        >>> machine_1.push(times=1000)
        (8000, 4000)

    Multiplying these together gives:

        >>> pulse_score(8000, 4000)
        32000000

    In the second example, after pushing the button `1000` times, `4250` low pulses and `2750` high
    pulses are sent:

        >>> machine_2.push(times=1000)
        (4250, 2750)

    Multiplying these together gives:

        >>> pulse_score(4250, 2750)
        11687500

    Consult your module configuration; determine the number of low pulses and high pulses that would
    be sent after pushing the button `1000` times, waiting for all pulses to be fully handled after
    each push of the button. **What do you get if you multiply the total number of low pulses sent
    by the total number of high pulses sent?**

        >>> part_1(configuration_2)
        part 1: by pushing the button 1000 times, 4250 low and 2750 high pulses are sent: 11687500
        11687500
    """

    machine = Machine(configuration)
    low, high = machine.push(times=pushes)
    result = pulse_score(low, high)

    print(
        f"part 1: by pushing the button {pushes} times, "
        f"{low} low and {high} high pulses are sent: {result}"
    )
    return result


def part_2(configuration: 'Configuration', target_module: 'ModuleName' = 'rx') -> int:
    """
    The final machine responsible for moving the sand down to Island Island has a module attached
    named `rx`. The machine turns on when a **single low pulse** is sent to `rx`.

    Reset all modules to their default states. Waiting for all pulses to be fully handled after each
    button press, **what is the fewest number of button presses required to deliver a single low
    pulse to the module named `rx`?**
    """

    result = calculate_pushes_needed(configuration, target_module)

    print(f"part 2: low pulse is sent to {target_module} after {result} button pushes")
    return result


ModuleName = str
ModuleType = str | None
Pulse = bool
Signal = tuple[ModuleName, Pulse, ModuleName]


@dataclass(frozen=True)
class Configuration:
    types: dict[ModuleName, ModuleType]
    destinations: dict[ModuleName, list[ModuleName]]

    def sources(self) -> dict[ModuleName, list[ModuleName]]:
        return dgroupby_pairs(
            (target, source)
            for source, targets in self.destinations.items()
            for target in targets
        )

    @classmethod
    def from_file(cls, fn: str) -> Self:
        return cls.from_lines(open(relative_path(__file__, fn)))

    @classmethod
    def from_text(cls, text: str) -> Self:
        return cls.from_lines(text.strip().splitlines())

    @classmethod
    def from_lines(cls, lines: Iterable[str]) -> Self:
        types: dict[ModuleName, ModuleType] = {}
        destinations: dict[ModuleName, list[ModuleName]] = {}

        for line in lines:
            source, targets = parse_line(line.strip(), '$ -> $')

            if source[0] in ('%', '&'):
                source_name, source_type = source[1:], source[0]
            else:
                source_name, source_type = source, None

            types[source_name] = source_type
            destinations[source_name] = targets.split(', ')

        return cls(types, destinations)

    def graphviz(self) -> str:
        def lines() -> Iterable[str]:
            yield 'digraph {'
            yield '    button [shape=rect style=filled fillcolor=lightblue]'
            yield '    button -> broadcaster'
            yield '    rx [style=filled fillcolor=red]'
            yield ''
            yield '    node [style=filled fillcolor=lightgray]'
            yield '    ' + ' '.join(mn for mn, mt in self.types.items() if mt == '%')
            yield ''
            yield '    node [style=filled fillcolor=yellow]'
            yield '    ' + ' '.join(mn for mn, mt in self.types.items() if mt == '&')
            yield ''
            yield '    node [style=plain]'
            for source, targets in self.destinations.items():
                targets_str = '{' + ' '.join(targets) + '}'
                yield f'    {source} -> {targets_str}'
            yield '}'
        return '\n'.join(lines())


class Machine:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration
        self.memory_flip_flops = {
            ff: False for ff, mt in configuration.types.items()
            if mt == '%'
        }
        self.memory_conjunctions = {
            con: {input_: False for input_ in inputs}
            for con, inputs in configuration.sources().items()
            if configuration.types.get(con) == '&'
        }
        self.pushes_count = 0
        self.watches: dict[ModuleName, set[bool]] = {}
        self.watch_results: dict[ModuleName, list[int]] = {}

    def push(
        self,
        times: int = 1,
        button_signal: Signal = ('button', False, 'broadcaster'),
        log: bool = False,
    ) -> tuple[int, int]:
        signals_queue: list[Signal] = []
        pulses_counter: Counter[Pulse] = Counter()

        for _ in range(times):
            self.pushes_count += 1
            signals_queue.append(button_signal)

            while signals_queue:
                src, pulse, module = signals_queue.pop(0)
                pulses_counter[pulse] += 1

                if log:
                    print(f"{src} -{pulse_str(pulse)}-> {module}")

                new_pulse = self._process_pulse(src, pulse, module)
                if new_pulse is not None:
                    signals_queue.extend(
                        (module, new_pulse, dest)
                        for dest in self.configuration.destinations.get(module, [])
                    )

        return pulses_counter[False], pulses_counter[True]

    def _process_pulse(self, src: ModuleName, pulse: bool, dest: ModuleName) -> bool | None:
        if dest in self.watches and pulse in self.watches[dest]:
            self.watch_results[dest].append(self.pushes_count)

        match self.configuration.types.get(dest):
            case None:
                # repeat
                return pulse
            case '%':
                # flip-flop
                if not pulse:
                    # flip on low pulse
                    self.memory_flip_flops[dest] = not self.memory_flip_flops[dest]
                    return self.memory_flip_flops[dest]
                else:
                    # nothing sent on high pulse
                    return None
            case '&':
                # conjunction
                self.memory_conjunctions[dest][src] = pulse
                # send low pulse if all pulses were high, high otherwise
                return not all(self.memory_conjunctions[dest].values())
            case unsupported:
                raise ValueError(unsupported)

    def add_watch(self, module: ModuleName, pulse: Pulse) -> None:
        self.watches.setdefault(module, set()).add(pulse)
        self.watch_results.setdefault(module, [])


def pulse_str(pulse: Pulse) -> str:
    return 'high' if pulse else 'low'


def pulse_score(low_pulses: int, high_pulses: int) -> int:
    return low_pulses * high_pulses


def calculate_pushes_needed(configuration: Configuration, target_module: str) -> int:
    sources = configuration.sources()

    # the target module is preceded by a single conjunction (&) module
    final_conjunction, = sources[target_module]
    assert configuration.types[final_conjunction] == '&'

    # the conjunction module takes input from N inverters (& with single input)
    final_converters = sources[final_conjunction]
    assert all(configuration.types[conv] == '&' for conv in final_converters)
    assert all(len(sources[conv]) == 1 for conv in final_converters)

    # we will watch these N converters for low pulse:
    machine = Machine(configuration)
    for conv in final_converters:
        machine.add_watch(conv, False)

    # run the machine for some time, until there are at least 4 values for each watched module,
    # so that we can establish their low-pulse periods
    while any(len(wr) < 4 for wr in machine.watch_results.values()):
        machine.push(100)

    # determine periods from these data
    periods = [single_value(set(diffs(machine.watch_results[conv]))) for conv in final_converters]
    # and return their LCM
    return lcm(*periods)


def main(input_fn: str = 'data/20-input.txt') -> tuple[int, int]:
    configuration = Configuration.from_file(input_fn)
    result_1 = part_1(configuration)
    result_2 = part_2(configuration)
    return result_1, result_2


if __name__ == '__main__':
    main()
