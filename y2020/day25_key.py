"""
Advent of Code 2020
Day 25: Combo Breaker
https://adventofcode.com/2020/day/25
"""

from typing import Iterable
from utils import eprint


def part_1(card_public_key: int, door_public_key: int) -> int:
    """
    The handshake used by the card and the door involves an operation that *transforms* a *subject
    number*. To transform a subject number, start with the value 1. Then, a number of times called
    the *loop size*, perform the following steps:

    - Set the value to itself multiplied by the *subject number*.
    - Set the value to the remainder after dividing the value by *`20201227`*.

    The card always uses a specific, secret *loop size* when it transforms a subject number.
    The door always uses a different, secret loop size.

    The cryptographic handshake works like this:

    - The *card* transforms the subject number of *`7`* according to the card's secret loop size.
      The result is called the *card's public key*.
    - The door transforms the subject number of *`7`* according to the door's secret loop size.
      The result is called the *door's public key*.
    - The card and door use the wireless RFID signal to transmit the two public keys (your puzzle
      input) to the other device. Now, the *card* has the *door's* public key, and the *door* has
      the *card's* public key. Because you can eavesdrop on the signal, you have both public keys,
      but neither device's loop size.
    - The *card* transforms the subject number of *the door's public key* according to the *card's*
      loop size. The result is the *encryption key*.
    - The *door* transforms the subject number of *the card's public key* according to the *door's*
      loop size. The result is the same *encryption key* as the *card* calculated.

    If you can use the two public keys to determine each device's loop size, you will have enough
    information to calculate the secret *encryption key* that the card and door use to communicate;
    this would let you send the unlock command directly to the door!

    For example, suppose you know that the card's public key is `5764801`. With a little trial and
    error, you can work out that the card's loop size must be *`8`*, because transforming the
    initial subject number of `7` with a loop size of `8` produces `5764801`.

        >>> card_pubkey = 5764801
        >>> card_loop = crack_loop_size(card_pubkey, subject_number=7)
        >>> card_loop
        8
        >>> transform(subject_number=7, loop_size=card_loop) == card_pubkey
        True

    Then, suppose you know that the door's public key is `17807724`. By the same process, you can
    determine that the door's loop size is *`11`*, because transforming the initial subject number
    of `7` with a loop size of `11` produces `17807724`.

        >>> door_pubkey = 17807724
        >>> door_loop = crack_loop_size(door_pubkey, subject_number=7)
        >>> door_loop
        11
        >>> transform(subject_number=7, loop_size=door_loop) == door_pubkey
        True

    At this point, you can use either device's loop size with the other device's public key to
    calculate the *encryption key*. Transforming the subject number of `17807724` (the door's
    public key) with a loop size of `8` (the card's loop size) produces the encryption key,
    *`14897079`*.

        >>> transform(door_pubkey, card_loop)
        14897079

    Transforming the subject number of `5764801` (the card's public key) with a loop size of `11`
    (the door's loop size) produces the same encryption key: *`14897079`*.

        >>> transform(card_pubkey, door_loop)
        14897079

    *What encryption key is the handshake trying to establish?*

        >>> part_1(card_pubkey, door_pubkey)
        part 1: encryption key is 14897079
        14897079
    """

    card_loop_size = crack_loop_size(public_key=card_public_key)
    eprint(f"card loop size: {card_loop_size}")
    door_loop_size = crack_loop_size(public_key=door_public_key)
    eprint(f"door loop size: {door_loop_size}")
    encryption_key_1 = transform(card_public_key, door_loop_size)
    encryption_key_2 = transform(door_public_key, card_loop_size)
    assert encryption_key_1 == encryption_key_2

    print(f"part 1: encryption key is {encryption_key_1}")
    return encryption_key_1


MODULO = 20201227


def transform(subject_number: int, loop_size: int, modulo: int = MODULO) -> int:
    return pow(subject_number, loop_size, modulo)


def crack_loop_size(
        public_key: int,
        subject_number: int = 7,
        modulo: int = MODULO
) -> int:
    value = subject_number
    for loop_size in range(1, modulo):
        if value == public_key:
            return loop_size
        value = (value * subject_number) % modulo


def public_keys_from_file(fn: str) -> tuple[int, int]:
    return public_keys_from_lines(open(fn))


def public_keys_from_lines(lines: Iterable[str]) -> tuple[int, int]:
    card_key_line, door_key_line = tuple(lines)
    return int(card_key_line), int(door_key_line)


if __name__ == '__main__':
    card_public_key_, door_public_key_ = public_keys_from_file("data/25-input.txt")
    part_1(card_public_key_, door_public_key_)
