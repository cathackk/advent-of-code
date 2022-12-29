"""
Advent of Code 2021
Day 16: Packet Decoder
https://adventofcode.com/2021/day/16
"""

from abc import ABC
from abc import abstractmethod
from enum import IntEnum
from math import prod
from typing import Iterable

from common.utils import assert_single_not_none
from meta.aoc_tools import data_path


def part_1(packet: 'Packet') -> int:
    """
    As you leave the cave and reach open waters, you receive a transmission from the Elves back on
    the ship.

    The transmission was sent using the Buoyancy Interchange Transmission System (BITS), a method of
    packing numeric expressions into a binary sequence. Your submarine's computer has saved the
    transmission in hexadecimal (your puzzle input).

    The first step of decoding the message is to convert the hexadecimal representation into binary.
    Each character of hexadecimal corresponds to four bits of binary data.

    The BITS transmission contains a single **packet** at its outermost layer which itself contains
    many other packets. The hexadecimal representation of this packet might encode a few extra `0`
    bits at the end; these are not part of the transmission and should be ignored.

    Every packet begins with a standard header: the first three bits encode the packet **version**,
    and the next three bits encode the packet **type ID**. These two values are numbers; all numbers
    encoded in any packet are represented as binary with the most significant bit first.
    For example, a version encoded as the binary sequence `100` represents the number `4`.

    Packets with type ID `4` represent a **literal value**. Literal value packets encode a single
    binary number. To do this, the binary number is padded with leading zeroes until its length is
    a multiple of four bits, and then it is broken into groups of four bits. Each group is prefixed
    by a `1` bit except the last group, which is prefixed by a `0` bit. These groups of five bits
    immediately follow the packet header. For example, the hexadecimal string `D2FE28` becomes:

        >>> p1 = Packet.from_hex('D2FE28')
        >>> print(p1.explain())
        110100101111111000101000
        VVVTTTAAAAABBBBBCCCCC

    Below each bit is a label indicating its purpose:

      - The three bits labeled `V` (`110`) are the packet version, `6`.
      - The three bits labeled `T` (`100`) are the packet type ID, `4`, which means the packet is
        a literal value.
      - The five bits labeled `A` (`10111`) start with a `1` (not the last group, keep reading)
        and contain the first four bits of the number, `0111`.
      - The five bits labeled `B` (`11110`) start with a `1` (not the last group, keep reading)
        and contain four more bits of the number, `1110`.
      - The five bits labeled `C` (`00101`) start with a `0` (last group, end of packet)
        and contain the last four bits of the number, `0101`.
      - The three unlabeled `0` bits at the end are extra due to the hexadecimal representation and
        should be ignored.

        >>> p1
        ValuePacket(version=6, value=2021)

    So, this packet represents a literal value with binary representation `011111100101`, which is
    `2021` in decimal.

    Every other type of packet (any packet with a type ID other than `4`) represent an **operator**
    that performs some calculation on one or more sub-packets contained within. Right now, the spe-
    cific operations aren't important; focus on parsing the hierarchy of sub-packets.

    An operator packet contains one or more packets. To indicate which subsequent binary data repre-
    sents its sub-packets, an operator packet can use one of two modes indicated by the bit immedia-
    tely after the packet header; this is called the **length type ID**:

      - If the length type ID is `0`, then the next **15** bits are a number that represents the
        **total length in bits** of the sub-packets contained by this packet.
      - If the length type ID is `1`, then the next **11** bits are a number that represents the
        **number of sub-packets immediately contained** by this packet.

    Finally, after the length type ID bit and the 15-bit or 11-bit field, the sub-packets appear.

    For example, here is an operator packet with length type ID `0` that contains two sub-packets:

        >>> p2 = Packet.from_hex('38006F45291200')
        >>> print(p2.explain())
        00111000000000000110111101000101001010010001001000000000
        VVVTTTILLLLLLLLLLLLLLLAAAAAAAAAAABBBBBBBBBBBBBBBB

      - The three bits labeled `V` (`001`) are the packet version, `1`.
      - The three bits labeled `T` (`110`) are the packet type ID, `6`, which means the packet is
        an operator.
      - The bit labeled `I` (`0`) is the length type ID, which indicates that the length is a 15-bit
        number representing the number of bits in the sub-packets.
      - The 15 bits labeled `L` (`000000000011011`) contain length of the sub-packets in bits, 27.
      - The 11 bits labeled `A` contain the first sub-packet, a literal value representing
        the number 10.
      - The 16 bits labeled `B` contain the second sub-packet, a literal value representing
        the number 20.

        >>> p2  # doctest: +NORMALIZE_WHITESPACE
        OperatorPacket(version=1, p_type=LESS_THAN, length_type_id=0,
                       sub_packets=[ValuePacket(version=6, value=10),
                                    ValuePacket(version=2, value=20)])

    After reading 11 and 16 bits of sub-packet data, the total length indicated in `L` (27) is
    reached, and so parsing of this packet stops.

    As another example, here is an operator packet with length type ID `1` that contains three
    sub-packets:

        >>> p3 = Packet.from_hex('EE00D40C823060')
        >>> print(p3.explain())
        11101110000000001101010000001100100000100011000001100000
        VVVTTTILLLLLLLLLLLAAAAAAAAAAABBBBBBBBBBBCCCCCCCCCCC

      - The three bits labeled `V` (`111`) are the packet version, `7`.
      - The three bits labeled `T` (`011`) are the packet type ID, `3`, which means the packet is
        an operator.
      - The bit labeled `I` (`1`) is the length type ID, which indicates that the length is a 11-bit
        number representing the number of sub-packets.
      - The 11 bits labeled `L` (`00000000011`) contain the number of sub-packets, `3`.
      - The 11 bits labeled `A` contain the first sub-packet, a literal value representing num `1`.
      - The 11 bits labeled `B` contain the second sub-packet, a literal value representing num `2`.
      - The 11 bits labeled `C` contain the third sub-packet, a literal value representing num `3`.

        >>> p3  # doctest: +NORMALIZE_WHITESPACE
        OperatorPacket(version=7, p_type=MAXIMUM, length_type_id=1,
                       sub_packets=[ValuePacket(version=2, value=1),
                                    ValuePacket(version=4, value=2),
                                    ValuePacket(version=1, value=3)])

    After reading 3 complete sub-packets, the number of sub-packets indicated in `L` (3) is reached,
    and so parsing of this packet stops.

    For now, parse the hierarchy of the packets throughout the transmission and **add up all of
    the version numbers**.

    Here are a few more examples of hexadecimal-encoded transmissions:

    - Operator packet (version 4) which contains an operator packet (version 1) which contains
      an operator packet (version 5) which contains a literal value (version 6); this packet has
      a version sum of 16:

        >>> (p4 := Packet.from_hex('8A004A801A8002F478'))
        ... # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        OperatorPacket(version=4, ...,
                       sub_packets=[OperatorPacket(version=1, ...,
                                    sub_packets=[OperatorPacket(version=5, ...,
                                                 sub_packets=[ValuePacket(version=6, ...)])])])
        >>> p4.versions_sum()
        16

    - Operator packet (version 3) which contains two sub-packets; each sub-packet is an operator
      packet that contains two literal values. This packet has a version sum of 12.

        >>> (p5 := Packet.from_hex('620080001611562C8802118E34'))
        ... # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
        OperatorPacket(version=3, p_type=SUM, length_type_id=1,
                       sub_packets=[OperatorPacket(...), OperatorPacket(...)])
        >>> p5.versions_sum()
        12

    - This one has the same structure as the previous example, but the outermost packet uses
      a different length type ID. This packet has a version sum of 23.

        >>> Packet.from_hex('C0015000016115A2E0802F182340').versions_sum()
        23

    - This is an operator packet that contains an operator packet that contains an operator packet
      that contains five literal values; it has a version sum of 31.

        >>> Packet.from_hex('A0016C880162017C3686B18A3D4780').versions_sum()
        31

    Decode the structure of your hexadecimal-encoded BITS transmission; **what do you get if you add
    up the version numbers in all packets?**

        >>> part_1(p5)
        part 1: sum of packet versions is 12
        12
    """

    result = packet.versions_sum()

    print(f"part 1: sum of packet versions is {result}")
    return result


def part_2(packet: 'Packet') -> int:
    """
    Now that you have the structure of your transmission decoded, you can calculate the value of
    the expression it represents.

    Literal values (type ID `4`) represent a single number as described above. The remaining type
    IDs are more interesting:

      - Packets with type ID `0` are **sum** packets - their value is the sum of the values of
        their sub-packets. If they only have a single sub-packet, their value is the value of
        the sub-packet.
      - Packets with type ID `1` are **product** packets - their value is the result of multiplying
        together the values of their sub-packets. If they only have a single sub-packet, their value
        is the value of the sub-packet.
      - Packets with type ID `2` are **minimum** packets - their value is the minimum of the values
        of their sub-packets.
      - Packets with type ID `3` are **maximum** packets - their value is the maximum of the values
        of their sub-packets.
      - Packets with type ID `5` are **greater than** packets - their value is `1` if the value of
        the first sub-packet is greater than the value of the second sub-packet;
        otherwise, their value is 0. These packets always have exactly two sub-packets.
      - Packets with type ID `6` are less than packets - their value is `1` if the value of
        the first sub-packet is less than the value of the second sub-packet;
        otherwise, their value is `0`. These packets always have exactly two sub-packets.
      - Packets with type ID `7` are **equal to** packets - their value is `1` if the value of
        the first sub-packet is equal to the value of the second sub-packet;
        otherwise, their value is `0`. These packets always have exactly two sub-packets.

    Using these rules, you can now work out the value of the outermost packet in your BITS trans-
    mission.

    For example:

        >>> print(Packet.from_hex('C200B40A82').expression())
        (1 + 2) = 3
        >>> print(Packet.from_hex('04005AC33890').expression())
        (6 * 9) = 54
        >>> print(Packet.from_hex('880086C3E88112').expression())
        min(7, 8, 9) = 7
        >>> print(Packet.from_hex('CE00C43D881120').expression())
        max(7, 8, 9) = 9
        >>> print(Packet.from_hex('D8005AC2A8F0').expression())
        (5 < 15) = 1
        >>> print(Packet.from_hex('F600BC2D8F').expression())
        (5 > 15) = 0
        >>> print(Packet.from_hex('9C005AC2F8F0').expression())
        (5 == 15) = 0
        >>> print(Packet.from_hex('9C0141080250320F1802104A08').expression())
        ((1 + 3) == (2 * 2)) = 1

    **What do you get if you evaluate the expression represented by your hexadecimal-encoded BITS
    transmission?**

        >>> part_2(Packet.from_hex('04005AC33890'))
        part 2: packet has value 54
        54
    """

    result = packet.value

    print(f"part 2: packet has value {result}")
    return result


class BitStream:
    def __init__(self, bits: Iterable[int] = ()):
        self.bits = list(bits)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.bits!r})'

    def __str__(self) -> str:
        return ''.join(str(b) for b in self.bits)

    def __bool__(self) -> bool:
        return bool(self.bits)

    def __len__(self) -> int:
        return len(self.bits)

    @classmethod
    def from_binary_string(cls, binary: str) -> 'BitStream':
        return cls(int(b) for b in binary)

    @classmethod
    def from_hex(cls, hex_string: str) -> 'BitStream':
        return cls(
            b
            for h in hex_string
            for b in cls._encode(int(h, 16), rpad=4)
        )

    def pop(self, length: int) -> int:
        if length > len(self.bits):
            raise IndexError(f'cannot pop {length} bits, only {len(self.bits)} remaining')

        value = self._decode(self.bits[:length])
        self.bits = self.bits[length:]
        return value

    def push(self, value: int, rpad=None, ralign=None, lalign=None) -> None:
        bits = self._encode(value=value, rpad=rpad, ralign=ralign, lalign=lalign)
        self.bits.extend(bits)

    def lalign(self, m: int) -> None:
        # add a number of zero bits so that the number of bits is divisible by m
        if (pad_length := complement(len(self), m)) > 0:
            self.push(0, rpad=pad_length)

    @staticmethod
    def _encode(value: int, rpad=None, ralign=None, lalign=None) -> Iterable[int]:
        assert_single_not_none(rpad=rpad, ralign=ralign, lalign=lalign)

        bins = bin(value)[2:]

        if rpad is not None:
            assert rpad > 0
            if (pad_length := rpad - len(bins)) > 0:
                bins = ('0' * pad_length) + bins

        elif ralign is not None:
            assert ralign > 0
            if (pad_length := complement(len(bins), ralign)) > 0:
                bins = ('0' * pad_length) + bins

        elif lalign is not None:
            assert lalign > 0
            if (pad_length := complement(len(bins), lalign)) > 0:
                bins = bins + ('0' * pad_length)

        return (int(b) for b in bins)

    @staticmethod
    def _decode(bits: Iterable[int]) -> int:
        return int(''.join(str(b) for b in bits), 2)

    @classmethod
    def concat(cls, streams: Iterable['BitStream']) -> 'BitStream':
        bits = BitStream()
        for stream in streams:
            bits.append(stream)
        return bits

    def append(self, other: 'BitStream') -> None:
        self.bits += other.bits


class PacketType(IntEnum):
    SUM = 0
    PRODUCT = 1
    MINIMUM = 2
    MAXIMUM = 3
    VALUE = 4
    GREATER_THAN = 5
    LESS_THAN = 6
    EQUAL_TO = 7


class Packet(ABC):
    def __init__(self, version: int, p_type: PacketType):
        self.version = version
        self.p_type = p_type

    @classmethod
    def from_file(cls, fn: str) -> 'Packet':
        return cls.from_hex(open(fn).readline().strip())

    @classmethod
    def from_hex(cls, hex_string: str) -> 'Packet':
        return cls.from_bits(BitStream.from_hex(hex_string))

    @classmethod
    def from_bits(cls, bits: BitStream) -> 'Packet':
        version = bits.pop(3)
        p_type = PacketType(bits.pop(3))
        if p_type is PacketType.VALUE:
            return ValuePacket.impl_from_bits(version, p_type, bits)
        else:
            return OperatorPacket.impl_from_bits(version, p_type, bits)

    def bits(self) -> BitStream:
        bits = BitStream()
        bits.append(self.bits_impl())
        bits.lalign(8)
        return bits

    def explain(self) -> str:
        return f'{self.bits()}\n{self.bits_labels()}'

    def bits_impl(self) -> BitStream:
        bits = BitStream()
        bits.push(self.version, rpad=3)
        bits.push(self.p_type.value, rpad=3)
        return bits

    def bits_labels(self) -> str:
        return 'VVVTTT'

    @property
    @abstractmethod
    def value(self) -> int:
        ...

    @abstractmethod
    def expression(self, with_result: bool = True) -> str:
        ...

    def versions_sum(self) -> int:
        return self.version


class ValuePacket(Packet):
    def __init__(self, version: int, p_type: PacketType, value: int):
        assert p_type is PacketType.VALUE
        super().__init__(version, p_type)
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def expression(self, with_result: bool = True) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        tn = type(self).__name__
        return f'{tn}(version={self.version!r}, value={self.value!r})'

    @classmethod
    def impl_from_bits(cls, version: int, p_type: PacketType, bits: BitStream) -> 'ValuePacket':
        value = 0
        while True:
            should_continue = bits.pop(1)
            chunk = bits.pop(4)
            value = value * 16 + chunk
            if not should_continue:
                break

        return cls(version=version, p_type=p_type, value=value)

    def bits_impl(self) -> BitStream:
        bits = super().bits_impl()

        value_bits = BitStream()
        value_bits.push(self.value, ralign=4)
        while value_bits:
            chunk_value = value_bits.pop(4)
            has_more = bool(value_bits)
            bits.push(has_more * 16 + chunk_value, rpad=5)

        return bits

    def bits_labels(self) -> str:
        value_chunks_count = (len(bin(self.value)[2:]) + 3) // 4
        value_chunks_labels = ''.join(abc(n) * 5 for n in range(value_chunks_count))
        return super().bits_labels() + value_chunks_labels


class OperatorPacket(Packet):
    def __init__(
        self,
        version: int,
        p_type: PacketType,
        length_type_id: int,
        sub_packets: Iterable[Packet],
    ):
        assert p_type is not PacketType.VALUE
        super().__init__(version, p_type)
        assert length_type_id in (0, 1)
        self.length_type_id = length_type_id
        self.sub_packets = list(sub_packets)

    def __repr__(self) -> str:
        return f'{type(self).__name__}(' \
               f'version={self.version!r}, ' \
               f'p_type={self.p_type.name}, ' \
               f'length_type_id={self.length_type_id!r}, ' \
               f'sub_packets={self.sub_packets!r})'

    @classmethod
    def impl_from_bits(cls, version: int, p_type: PacketType, bits: BitStream) -> 'OperatorPacket':
        length_type_id = bits.pop(1)
        if length_type_id == 0:
            # 15 bits of sub-packets bit length
            sp_bits_length = bits.pop(15)
            original_bits_length = len(bits)
            sub_packets = []
            while len(bits) > original_bits_length - sp_bits_length:
                sub_packets.append(Packet.from_bits(bits))

        else:
            # 11 bits of sub-packets count
            sp_count = bits.pop(11)
            sub_packets = [Packet.from_bits(bits) for _ in range(sp_count)]

        return cls(
            version=version,
            p_type=p_type,
            length_type_id=length_type_id,
            sub_packets=sub_packets,
        )

    def bits_impl(self) -> BitStream:
        bits = super().bits_impl()
        bits.push(self.length_type_id, rpad=1)
        sub_packets_bits = BitStream.concat(
            sub_packet.bits_impl()
            for sub_packet in self.sub_packets
        )

        if self.length_type_id == 0:
            # 15 bits of total sub-packet length
            bits.push(len(sub_packets_bits), rpad=15)
        elif self.length_type_id == 1:
            # 11 bits of immediate sub-packet count
            bits.push(len(self.sub_packets), rpad=11)

        bits.append(sub_packets_bits)
        return bits

    def bits_labels(self) -> str:
        length_bits_count = 15 if self.length_type_id == 0 else 11
        length_labels = 'I' + ('L' * length_bits_count)
        sub_packets_labels = ''.join(
            abc(i) * len(sub_packet.bits_labels())
            for i, sub_packet in enumerate(self.sub_packets)
        )
        return super().bits_labels() + length_labels + sub_packets_labels

    def versions_sum(self) -> int:
        return self.version + sum(sp.versions_sum() for sp in self.sub_packets)

    @property
    def value(self) -> int:
        # pylint: disable=too-many-return-statements
        match self.p_type:
            case PacketType.SUM:
                return sum(sp.value for sp in self.sub_packets)
            case PacketType.PRODUCT:
                return prod(sp.value for sp in self.sub_packets)
            case PacketType.MINIMUM:
                return min(sp.value for sp in self.sub_packets)
            case PacketType.MAXIMUM:
                return max(sp.value for sp in self.sub_packets)
            case PacketType.GREATER_THAN:
                a, b = self.sub_packets
                return int(a.value > b.value)
            case PacketType.LESS_THAN:
                a, b = self.sub_packets
                return int(a.value < b.value)
            case PacketType.EQUAL_TO:
                a, b = self.sub_packets
                return int(a.value == b.value)
            case _:
                raise ValueError(f'unsupported packet type {self.p_type.name}')

        # TODO: remove when mypy realizes this is unreachable
        assert False

    def expression(self, with_result: bool = True) -> str:
        expr = self._expression_base()
        if with_result:
            return f'{expr} = {self.value}'
        else:
            return expr

    def _expression_base(self) -> str:
        # pylint: disable=too-many-return-statements
        match self.p_type:
            case PacketType.SUM:
                return '(' + ' + '.join(sp.expression(False) for sp in self.sub_packets) + ')'
            case PacketType.PRODUCT:
                return '(' + ' * '.join(sp.expression(False) for sp in self.sub_packets) + ')'
            case PacketType.MINIMUM:
                return 'min(' + ', '.join(sp.expression(False) for sp in self.sub_packets) + ')'
            case PacketType.MAXIMUM:
                return 'max(' + ', '.join(sp.expression(False) for sp in self.sub_packets) + ')'
            case PacketType.GREATER_THAN:
                a, b = self.sub_packets
                return '(' + a.expression(False) + ' > ' + b.expression(False) + ')'
            case PacketType.LESS_THAN:
                a, b = self.sub_packets
                return '(' + a.expression(False) + ' < ' + b.expression(False) + ')'
            case PacketType.EQUAL_TO:
                a, b = self.sub_packets
                return '(' + a.expression(False) + ' == ' + b.expression(False) + ')'
            case _:
                raise ValueError(f'unsupported packet type {self.p_type.name}')

        # TODO: remove when mypy realizes this is unreachable
        assert False


def complement(value: int, n: int) -> int:
    """
    How much must be added to `value` so it is divisible by `n`?

        >>> complement(14, 5), complement(15, 5), complement(16, 5)
        (1, 0, 4)
    """
    return (n - (value % n)) % n


def abc(n: int) -> 'str':
    """
        >>> abc(0), abc(1), abc(2), abc(26)
        ('A', 'B', 'C', 'A')
    """
    return chr(ord('A') + n % 26)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    packet = Packet.from_file(input_path)
    result_1 = part_1(packet)
    result_2 = part_2(packet)
    return result_1, result_2


if __name__ == '__main__':
    main()
