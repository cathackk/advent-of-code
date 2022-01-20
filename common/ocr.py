from textwrap import dedent
from typing import Iterable

LETTERS = {
    'A': 0x19297A52,
    'B': 0x392E4A5C,
    'C': 0x1928424C,
    'D': 0x39294A5C,
    'E': 0x3D0E421E,
    'F': 0x3D0E4210,
    'G': 0x19285A4E,
    'H': 0x252F4A52,
    'I': 0x1C42108E,
    'J': 0x0C210A4C,
    'K': 0x254C5292,
    'L': 0x2108421E,
    'O': 0x19294A4C,
    'P': 0x39297210,
    'R': 0x39297292,
    'S': 0x1D08305C,
    'T': 0x1C421084,
    'U': 0x25294A4C,
    'Y': 0x23151084,
    'Z': 0x3C22221E,
    ' ': 0x00000000,
}

LETTERS_LOOKUP = {code: char for char, code in LETTERS.items()}

LETTER_WIDTH = 5
LETTER_HEIGHT = 6
LETTER_AREA = LETTER_WIDTH * LETTER_HEIGHT

DEFAULT_ON = "#"
DEFAULT_OFF = "·"

PIXELS = {pix: True for pix in '1XH#█'} | {pix: False for pix in ' .·_-0'}


def write_string(string: str, off: str = DEFAULT_OFF, on: str = DEFAULT_ON) -> str:
    """
        >>> print(write_string("ABCDEFGHIJKL", off=" ", on="█"))
         ██  ███   ██  ███  ████ ████  ██  █  █  ███   ██ █  █ █
        █  █ █  █ █  █ █  █ █    █    █  █ █  █   █     █ █ █  █
        █  █ ███  █    █  █ ███  ███  █    ████   █     █ ██   █
        ████ █  █ █    █  █ █    █    █ ██ █  █   █     █ █ █  █
        █  █ █  █ █  █ █  █ █    █    █  █ █  █   █  █  █ █ █  █
        █  █ ███   ██  ███  ████ █     ███ █  █  ███  ██  █  █ ████

        >>> print(write_string("OPRSTUYZ", off=" ", on="█"))
         ██  ███  ███   ███  ███ █  █ █   █████
        █  █ █  █ █  █ █      █  █  █ █   █   █
        █  █ █  █ █  █ █      █  █  █  █ █   █
        █  █ ███  ███   ██    █  █  █   █   █
        █  █ █    █ █     █   █  █  █   █  █
         ██  █    █  █ ███    █   ██    █  ████

        >>> print(write_string("BEACH DOG STORE"))
        ###··####··##···##··#··#······###···##···##········###··###··##··###··####·
        #··#·#····#··#·#··#·#··#······#··#·#··#·#··#······#······#··#··#·#··#·#····
        ###··###··#··#·#····####······#··#·#··#·#·········#······#··#··#·#··#·###··
        #··#·#····####·#····#··#······#··#·#··#·#·##·······##····#··#··#·###··#····
        #··#·#····#··#·#··#·#··#······#··#·#··#·#··#·········#···#··#··#·#·#··#····
        ###··####·#··#··##··#··#······###···##···###······###····#···##··#··#·####·
    """
    return "\n".join(
        "".join(lines).rstrip()
        for lines in zip(*(_letter_lines(char, off=off, on=on) for char in string))
    )


def _letter_lines(letter: str, off: str, on: str) -> Iterable[str]:
    assert len(letter) == len(off) == len(on) == 1
    pixels = bin(LETTERS[letter])[2:].zfill(LETTER_AREA).replace('0', off).replace('1', on)
    return (pixels[k:k + LETTER_WIDTH] for k in range(0, LETTER_AREA, LETTER_WIDTH))



def read_string(ascii_text: str) -> str:
    """
        >>> read_string('''
        ...     .██..████.███..█..█.███..████.███....██.███...███.
        ...     █..█.█....█..█.█..█.█..█....█.█..█....█.█..█.█....
        ...     █..█.███..███..█..█.█..█...█..███.....█.█..█.█....
        ...     ████.█....█..█.█..█.███...█...█..█....█.███...██..
        ...     █..█.█....█..█.█..█.█....█....█..█.█..█.█.......█.
        ...     █..█.█....███...██..█....████.███...██..█....███..
        ... ''')
        'AFBUPZBJPS'
        >>> read_string('''
        ...     XXXX.XXXX.XXXX.X...XX..X.XXXX.XXX..XXXX..XXX...XX.
        ...     X....X....X....X...XX.X..X....X..X.X......X.....X.
        ...     XXX..XXX..XXX...X.X.XX...XXX..X..X.XXX....X.....X.
        ...     X....X....X......X..X.X..X....XXX..X......X.....X.
        ...     X....X....X......X..X.X..X....X.X..X......X..X..X.
        ...     XXXX.X....XXXX...X..X..X.X....X..X.X.....XXX..XX..
        ... ''')
        'EFEYKFRFIJ'
        >>> read_string('''
        ...     ####   ## #  # ###  #  #  ##  ###  #    #   #  ##
        ...        #    # #  # #  # # #  #  # #  # #    #   #   #
        ...       #     # #### #  # ##   #    #  # #     # #    #
        ...      #      # #  # ###  # #  #    ###  #      #     #
        ...     #    #  # #  # # #  # #  #  # #    #      #  #  #
        ...     ####  ##  #  # #  # #  #  ##  #    ####   #   ##
        ... ''')
        'ZJHRKCPLYJ'
        >>> read_string('''
        ...      HH  HHHH H    HHHH H     HH  H   HHHHH  HH   HHH
        ...     H  H H    H    H    H    H  H H   HH    H  H H
        ...     H    HHH  H    HHH  H    H  H  H H HHH  H    H
        ...     H    H    H    H    H    H  H   H  H    H     HH
        ...     H  H H    H    H    H    H  H   H  H    H  H    H
        ...      HH  H    HHHH HHHH HHHH  HH    H  H     HH  HHH
        ... ''')
        'CFLELOYFCS'
        >>> read_string('''
        ...
        ...     █  █ ███   ██    ██ ████ █    ███   ██  ████ ████
        ...     █  █ █  █ █  █    █ █    █    █  █ █  █ █       █
        ...     █  █ █  █ █  █    █ ███  █    ███  █    ███    █
        ...     █  █ ███  █  █    █ █    █    █  █ █    █     █
        ...     █  █ █    █  █ █  █ █    █    █  █ █  █ █    █
        ...      ██  █     ██   ██  █    ████ ███   ██  ████ ████
        ...
        ... ''')
        'UPOJFLBCEZ'
        >>> read_string('''
        ...
        ...     ███  ████  ██   ██  █  █      ###   ##   ##
        ...     █  █ █    █  █ █  █ █  █      #  # #  # #  #
        ...     ███  ███  █  █ █    ████      #  # #  # #
        ...     █  █ █    ████ █    █  █      #  # #  # # ##
        ...     █  █ █    █  █ █  █ █  █      #  # #  # #  #
        ...     ███  ████ █  █  ██  █  █      ###   ##   ###
        ...
        ... ''')
        'BEACH DOG'
    """

    return ''.join(
        LETTERS_LOOKUP[int(''.join(str(int(PIXELS[char])) for char in ''.join(letter)), 2)]
        for letter in zip(*(
            [line[k:k + LETTER_WIDTH].ljust(LETTER_WIDTH) for k in
             range(0, len(line), LETTER_WIDTH)]
            for line in dedent(ascii_text.strip('\n')).split('\n')
        ))
    )
