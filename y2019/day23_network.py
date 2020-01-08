from typing import List
from typing import Optional

from y2019.intcode import IOState
from y2019.intcode import load_tape
from y2019.intcode import Machine
from y2019.intcode import MachineIO


class Packet:
    def __init__(self, address: int, x: int, y: int):
        self.address = address
        self.x = x
        self.y = y

    def __repr__(self):
        return f'{type(self).__name__}({self.address}, {self.x}, {self.y})'

    def __str__(self):
        return f"[{self.x}:{self.y} @ M{self.address:02}]"

    def __iter__(self):
        yield self.x
        yield self.y


def run_network() -> int:
    tape = load_tape("data/23-program.txt")

    def create_network_io(address: int, debug: bool = False) -> MachineIO:
        machine = Machine(tape, name=f"M{address:02}", debug=debug)
        io = machine.run_io()
        # this is your address
        io.write_single(address)
        # and queue is empty
        io.write_single(-1)
        return io

    network: List[MachineIO] = [create_network_io(address) for address in range(50)]
    queue: List[Packet] = []
    nat_packet: Optional[Packet] = None
    nat_sent_history: List[Packet] = []

    # initialize queue
    for address, io in enumerate(network):
        while io.state == IOState.OUTPUT:
            packet_out = Packet(*io.read(3))
            queue.append(packet_out)
            print(f"M{address:02}:{len(queue):02} queued {packet_out}")

    while True:
        # process queue until it's empty
        while queue:
            packet = queue.pop()
            address = packet.address

            if address == 255:
                nat_packet = packet
                print(f"NAT:{len(queue):02} receiving {packet}")
                continue

            io = network[address]
            assert io.state == IOState.INPUT
            io.write(packet)
            print(f"M{address:02}:{len(queue):02} receiving {packet}")

            while io.state == IOState.OUTPUT:
                packet_out = Packet(*io.read(3))
                queue.append(packet_out)
                print(f"M{address:02}:{len(queue):02} queued {packet_out}")

        if nat_packet:
            if nat_sent_history:
                previous_nat_packet = nat_sent_history[-1]
                if nat_packet.y == previous_nat_packet.y:
                    print(
                        f"NAT:{len(queue):02} repeating NAT packet Y detected: "
                        f"now={nat_packet}, prev={previous_nat_packet}"
                    )
                    return nat_packet.y
            nat_packet.address = 0
            print(f"NAT:{len(queue):02} queue is empty, queueing {nat_packet} to M00")
            queue.append(nat_packet)
            nat_sent_history.append(nat_packet)
            nat_packet = None
        else:
            print(f"NAT:{len(queue):02} queue is empty and there's no NAT packet available")
            return -1


if __name__ == '__main__':
    print(run_network())
