from collections import Counter
from typing import Iterable


ord_a = ord('a')
Room = tuple[str, int, str]


def load_rooms(fn: str) -> Iterable[Room]:
    for line in open(fn):
        yield parse_room(line)


def parse_room(line: str) -> Room:
    p1, p2 = line.strip().split('[')
    name, sector = p1.rsplit('-', 1)
    assert p2[-1] == ']'
    checksum = p2[:-1]
    return name, int(sector), checksum


def compute_checksum(name: str) -> str:
    chars = (c for c in name if c != '-')
    counts = Counter(chars)
    cqs = sorted(counts.items(), key=lambda cq: (-cq[1], cq[0]))
    return ''.join(c for c, q in cqs[:5])


def is_real(room: Room) -> bool:
    name, sector, checksum = room
    expected_checksum = compute_checksum(name)
    return expected_checksum == checksum


def decrypt_name(encrypted: str, shift: int) -> str:
    return ''.join(shifted_char(c, shift) for c in encrypted)


def shifted_char(c: str, n: int) -> str:
    if c == '-':
        return ' '

    k = ord(c) - ord_a
    return chr(ord_a + (k + n) % 26)


def test_is_real():
    assert is_real(parse_room('aaaaa-bbb-z-y-x-123[abxyz]')) is True
    assert is_real(parse_room('a-b-c-d-e-f-g-h-987[abcde]')) is True
    assert is_real(parse_room('not-a-real-room-404[oarel]')) is True
    assert is_real(parse_room('totally-real-room-200[decoy]')) is False


def test_decrypt_name():
    assert decrypt_name('qzmt-zixmtkozy-ivhz', 343) == 'very encrypted name'


def part_1(fn: str) -> int:
    sectors_sum = sum(room[1] for room in load_rooms(fn) if is_real(room))
    print(f"part 1: sum of IDs is {sectors_sum}")
    return sectors_sum


def part_2(fn: str) -> int:
    for room in load_rooms(fn):
        if is_real(room):
            encrypted, sector, checksum = room
            decrypted = decrypt_name(encrypted, sector)
            # print(sector, decrypted)
            if decrypted == "northpole object storage":
                print(f"part 2: room {sector} is {decrypted!r}")
                return sector


if __name__ == '__main__':
    fn_ = "data/04-input.txt"
    part_1(fn_)
    part_2(fn_)
