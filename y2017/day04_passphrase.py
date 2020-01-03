from typing import Iterable


def load_passphrases(fn: str) -> Iterable[str]:
    return (line.strip() for line in open(fn))


def is_valid(passphrase: str) -> bool:
    """
    >>> is_valid("aa bb cc dd ee")
    True
    >>> is_valid("aa bb cc dd aa")
    False
    >>> is_valid("aa bb cc dd aaa")
    True
    """
    words = passphrase.split(' ')
    return len(words) == len(set(words))


def is_valid2(passphrase: str) -> bool:
    """
    >>> is_valid2("abcde fghij")
    True
    >>> is_valid2("abcde xyz ecdab")
    False
    >>> is_valid2("a ab abc abd abf abj")
    True
    >>> is_valid2("iiii oiii ooii oooi oooo")
    True
    >>> is_valid2("oiii ioii iioi iiio")
    False
    """
    words = [''.join(sorted(word)) for word in passphrase.split(' ')]
    return len(words) == len(set(words))


def part_1(fn: str) -> int:
    result = sum(1 for pp in load_passphrases(fn) if is_valid(pp))
    print(f"part 1: {result} valid passphrases")
    return result


def part_2(fn: str) -> int:
    result = sum(1 for pp in load_passphrases(fn) if is_valid2(pp))
    print(f"part 2: {result} valid passphrases")
    return result


if __name__ == '__main__':
    fn = "data/04-input.txt"
    part_1(fn)
    part_2(fn)
