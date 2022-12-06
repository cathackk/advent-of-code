"""
Advent of Code 2022
Day 6: Tuning Trouble
https://adventofcode.com/2022/day/6
"""

from common.file import relative_path


def part_1(data: str) -> int:
    """
    The preparations are finally complete; you and the Elves leave camp on foot and begin to make
    your way toward the ***star*** fruit grove.

    As you move through the dense undergrowth, one of the Elves gives you a handheld **device**.
    He says that it has many fancy features, but the most important one to set up right now is
    the **communication system**.

    However, because he's heard you have significant experience dealing with signal-based systems,
    he convinced the other Elves that it would be okay to give you their one malfunctioning device
    - surely you'll have no problem fixing it.

    As if inspired by comedic timing, the device emits a few colorful sparks.

    To be able to communicate with the Elves, the device needs to **lock on to their signal**.
    The signal is a series of seemingly-random characters that the device receives one at a time.

    To fix the communication system, you need to add a subroutine to the device that detects
    a **start-of-packet marker** in the datastream. In the protocol being used by the Elves, the
    start of a packet is indicated by a sequence of **four characters that are all different**.

    The device will send your subroutine a datastream buffer (your puzzle input); your subroutine
    needs to identify the first position where the four most recently received characters were all
    different. Specifically, it needs to report the number of characters from the beginning of the
    buffer to the end of the first such four-character marker.

    For example, suppose you receive the following datastream buffer:

        >>> datastream = 'mjqjpqmgbljsphdztnvjfqwrcgsmlb'

    After the first three characters (`mjq`) have been received, there haven't been enough
    characters received yet to find the marker. The first time a marker could occur is after the
    fourth character is received, making the most recent four characters `mjqj`. Because `j` is
    repeated, this isn't a marker.

    The first time a marker appears is after the seventh character arrives. Once it does, the last
    four characters received are `jpqm`, which are all different. In this case, your subroutine
    should report the value **`7`**, because the first start-of-packet marker is complete after 7
    characters have been processed.

        >>> start_of_packet(datastream)
        7

    Here are a few more examples:

        >>> start_of_packet('bvwbjplbgvbhsrlpgdmjqwftvncz')
        5
        >>> start_of_packet('nppdvjthqldpwncqszvftbrmjlhg')
        6
        >>> start_of_packet('nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg')
        10
        >>> start_of_packet('zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw')
        11

    **How many chars need to be processed before the first start-of-packet marker is detected?**

        >>> part_1(datastream)
        part 1: start-of-packet marker appears after processing 7 characters
        7
    """

    result = start_of_packet(data)

    print(f"part 1: start-of-packet marker appears after processing {result} characters")
    return result


def part_2(data: str) -> int:
    """
    Your device's communication system is correctly detecting packets, but still isn't working.
    It looks like it also needs to look for **messages**.

    A **start-of-message marker** is just like a start-of-packet marker, except it consists of
    **14 distinct characters** rather than 4.

    Here are the first positions of start-of-message markers for all of the above examples:

        >>> start_of_message('mjqjpqmgbljsphdztnvjfqwrcgsmlb')
        19
        >>> start_of_message('bvwbjplbgvbhsrlpgdmjqwftvncz')
        23
        >>> start_of_message('nppdvjthqldpwncqszvftbrmjlhg')
        23
        >>> start_of_message('nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg')
        29
        >>> start_of_message('zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw')
        26

    **How many chars need to be processed before the first start-of-message marker is detected?**

        >>> part_2('mjqjpqmgbljsphdztnvjfqwrcgsmlb')
        part 2: start-of-message marker appears after processing 19 characters
        19
    """

    result = start_of_message(data)

    print(f"part 2: start-of-message marker appears after processing {result} characters")
    return result


def start_of_packet(data: str) -> int:
    return find_distinct_chars(data, 4)


def start_of_message(data: str) -> int:
    return find_distinct_chars(data, 14)


def find_distinct_chars(data: str, count: int) -> int:
    c = count
    return next(k + c for k in range(len(data) - c + 1) if len(set(data[k:k+c])) == c)


def data_from_file(fn: str) -> str:
    return open(relative_path(__file__, fn)).read().strip()


if __name__ == '__main__':
    data_ = data_from_file('data/06-input.txt')
    part_1(data_)
    part_2(data_)
