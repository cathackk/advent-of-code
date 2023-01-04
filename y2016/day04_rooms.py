"""
Advent of Code 2016
Day 4: Security Through Obscurity
https://adventofcode.com/2016/day/4
"""

from collections import Counter
from typing import Iterable

from meta.aoc_tools import data_path


def part_1(rooms: list['Room']) -> int:
    """
    Finally, you come across an information kiosk with a list of rooms. Of course, the list is
    encrypted and full of decoy data, but the instructions to decode the list are barely hidden
    nearby. Better remove the decoy data first.

    Each room consists of an encrypted name (lowercase letters separated by dashes) followed by
    a dash, a sector ID, and a checksum in square brackets.

    A room is real (not a decoy) if the checksum is the five most common letters in the encrypted
    name, in order, with ties broken by alphabetization. For example:

      - `aaaaa-bbb-z-y-x-123[abxyz]` is a real room because the most common letters are
        `a` (5), `b` (3), and then a tie between `x`, `y`, and `z`, which are listed alphabetically:

        >>> (room_1 := Room.from_str('aaaaa-bbb-z-y-x-123[abxyz]'))
        Room('aaaaa-bbb-z-y-x', sector_id=123, checksum='abxyz')
        >>> room_1.is_real()
        True

      - `a-b-c-d-e-f-g-h-987[abcde]` is a real room because although the letters are all tied
        (1 of each), the first five are listed alphabetically:

        >>> (room_2 := Room.from_str('a-b-c-d-e-f-g-h-987[abcde]'))
        Room('a-b-c-d-e-f-g-h', sector_id=987, checksum='abcde')
        >>> room_2.is_real()
        True

    Two more examples:

        >>> (room_3 := Room.from_str('not-a-real-room-404[oarel]')).is_real()
        True
        >>> (room_4 := Room.from_str('totally-real-room-200[decoy]')).is_real()
        False

    Of the real rooms from the list above, the sum of their sector IDs is `1514`.

    What is the **sum of the sector IDs of the real rooms**?

        >>> part_1([room_1, room_2, room_3, room_4])
        part 1: 3 out of 4 rooms are real and sum of their sector IDs is 1514
        1514
    """

    real_rooms = [room for room in rooms if room.is_real()]
    result = sum(room.sector_id for room in real_rooms)
    print(
        f"part 1: {len(real_rooms)} out of {len(rooms)} rooms are real "
        f"and sum of their sector IDs is {result}"
    )
    return result


def part_2(rooms: Iterable['Room']) -> int:
    """
    With all the decoy data out of the way, it's time to decrypt this list and get moving.

    The room names are encrypted by a state-of-the-art shift cipher, which is nearly unbreakable
    without the right software. However, the information kiosk designers at Easter Bunny HQ were not
    expecting to deal with a master cryptographer like yourself.

    To decrypt a room name, rotate each letter forward through the alphabet a number of times equal
    to the room's sector ID. `A` becomes `B`, `B` becomes `C`, `Z` becomes `A`, and so on.
    Dashes become spaces.

    For example:

        >>> Room.from_str('qzmt-zixmtkozy-ivhz-343[zmtih]').decrypted_name
        'very encrypted name'

    **What is the sector ID** of the room where North Pole objects are stored?

        >>> part_2(rooms_from_file(data_path(__file__, 'example.txt')))
        part 2: room 'northpole objects' has sector ID 698
        698
    """

    storage_room = next(room for room in rooms if "northpole" in room.decrypted_name)
    result = storage_room.sector_id
    print(f"part 2: room {storage_room.decrypted_name!r} has sector ID {result}")
    return result


class Room:
    def __init__(self, name, sector_id, checksum):
        self.encrypted_name = str(name)
        self.sector_id = int(sector_id)
        self.checksum = str(checksum)

    def __repr__(self) -> str:
        return (
            f'{type(self).__name__}('
            f'{self.encrypted_name!r}, '
            f'sector_id={self.sector_id!r}, '
            f'checksum={self.checksum!r})'
        )

    def __str__(self) -> str:
        return f"{self.encrypted_name}-{self.sector_id}[{self.checksum}]"

    @classmethod
    def from_str(cls, line: str):
        # "aaaaa-bbb-z-y-x-123[abxyz]"
        name_and_sector_id, checksum = line.rstrip(']').split('[')
        name, sector_id = name_and_sector_id.rsplit('-', 1)
        return cls(name, sector_id, checksum)

    def expected_checksum(self) -> str:
        name_chars = [char for char in self.encrypted_name if char != '-']
        counts = Counter(name_chars)
        return ''.join(sorted(set(name_chars), key=lambda char: (-counts[char], char)))[:5]

    def is_real(self) -> bool:
        return self.expected_checksum() == self.checksum

    @property
    def decrypted_name(self) -> str:
        assert self.encrypted_name.islower()
        return ''.join(rot(char, self.sector_id) for char in self.encrypted_name)


ORD_A = ord('a')


def rot(char: str, times: int) -> str:
    assert len(char) == 1
    if char == '-':
        return ' '

    return chr(ORD_A + (ord(char) - ORD_A + times) % 26)


def rooms_from_file(fn: str) -> list[Room]:
    return list(rooms_from_lines(open(fn)))


def rooms_from_lines(lines: Iterable[str]) -> Iterable[Room]:
    return (Room.from_str(line.strip()) for line in lines)


def main(input_path: str = data_path(__file__)) -> tuple[int, int]:
    rooms = rooms_from_file(input_path)
    result_1 = part_1(rooms)
    result_2 = part_2(rooms)
    return result_1, result_2


if __name__ == '__main__':
    main()
