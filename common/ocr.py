from textwrap import dedent
from typing import Iterable


PIXELS = {pix: True for pix in '1XH#*█'} | {pix: False for pix in ' .·_-0'}
DEFAULT_ON = "#"
DEFAULT_OFF = "·"


class Font:
    def __init__(self, char_height: int, char_width: int, chars: dict[str, int]):
        self.char_height = char_height
        self.char_width = char_width
        self.chars = dict(chars)
        self.chars_lookup = {code: char for char, code in self.chars.items()}

    @property
    def char_area(self) -> int:
        return self.char_width * self.char_height

    def _lookup_by_code(self, code: int) -> str:
        try:
            return self.chars_lookup[code]
        except KeyError as exc:
            raise KeyError(hex(code)) from exc

    def _char_lines(self, char: str, off: str, on: str) -> Iterable[str]:
        assert len(char) == len(off) == len(on) == 1
        pixels = bin(self.chars[char])[2:].zfill(self.char_area).replace('0', off).replace('1', on)
        return (pixels[k:k + self.char_width] for k in range(0, self.char_area, self.char_width))

    def write_string(self, string: str, off: str = DEFAULT_OFF, on: str = DEFAULT_ON) -> str:
        """
            >>> print(FONT_6X5.write_string("ABCDEFGHIJKL", off=" ", on="█"))
             ██  ███   ██  ███  ████ ████  ██  █  █  ███   ██ █  █ █
            █  █ █  █ █  █ █  █ █    █    █  █ █  █   █     █ █ █  █
            █  █ ███  █    █  █ ███  ███  █    ████   █     █ ██   █
            ████ █  █ █    █  █ █    █    █ ██ █  █   █     █ █ █  █
            █  █ █  █ █  █ █  █ █    █    █  █ █  █   █  █  █ █ █  █
            █  █ ███   ██  ███  ████ █     ███ █  █  ███  ██  █  █ ████

            >>> print(FONT_6X5.write_string("OPRSTUYZ", off=" ", on="█"))
             ██  ███  ███   ███  ███ █  █ █   █████
            █  █ █  █ █  █ █      █  █  █ █   █   █
            █  █ █  █ █  █ █      █  █  █  █ █   █
            █  █ ███  ███   ██    █  █  █   █   █
            █  █ █    █ █     █   █  █  █   █  █
             ██  █    █  █ ███    █   ██    █  ████

            >>> print(FONT_6X5.write_string("BEACH DOG STORE"))
            ###··####··##···##··#··#······###···##···##········###··###··##··###··####·
            #··#·#····#··#·#··#·#··#······#··#·#··#·#··#······#······#··#··#·#··#·#····
            ###··###··#··#·#····####······#··#·#··#·#·········#······#··#··#·#··#·###··
            #··#·#····####·#····#··#······#··#·#··#·#·##·······##····#··#··#·###··#····
            #··#·#····#··#·#··#·#··#······#··#·#··#·#··#·········#···#··#··#·#·#··#····
            ###··####·#··#··##··#··#······###···##···###······###····#···##··#··#·####·
        """

        return "\n".join(
            "".join(lines).rstrip()
            for lines in zip(*(self._char_lines(char, off=off, on=on) for char in string))
        )

    def read_string(self, ascii_text: str) -> str:
        """
            >>> FONT_6X5.read_string('''
            ...     .██..████.███..█..█.███..████.███....██.███...███.
            ...     █..█.█....█..█.█..█.█..█....█.█..█....█.█..█.█....
            ...     █..█.███..███..█..█.█..█...█..███.....█.█..█.█....
            ...     ████.█....█..█.█..█.███...█...█..█....█.███...██..
            ...     █..█.█....█..█.█..█.█....█....█..█.█..█.█.......█.
            ...     █..█.█....███...██..█....████.███...██..█....███..
            ... ''')
            'AFBUPZBJPS'
            >>> FONT_6X5.read_string('''
            ...     XXXX.XXXX.XXXX.X...XX..X.XXXX.XXX..XXXX..XXX...XX.
            ...     X....X....X....X...XX.X..X....X..X.X......X.....X.
            ...     XXX..XXX..XXX...X.X.XX...XXX..X..X.XXX....X.....X.
            ...     X....X....X......X..X.X..X....XXX..X......X.....X.
            ...     X....X....X......X..X.X..X....X.X..X......X..X..X.
            ...     XXXX.X....XXXX...X..X..X.X....X..X.X.....XXX..XX..
            ... ''')
            'EFEYKFRFIJ'
            >>> FONT_6X5.read_string('''
            ...     ####   ## #  # ###  #  #  ##  ###  #    #   #  ##
            ...        #    # #  # #  # # #  #  # #  # #    #   #   #
            ...       #     # #### #  # ##   #    #  # #     # #    #
            ...      #      # #  # ###  # #  #    ###  #      #     #
            ...     #    #  # #  # # #  # #  #  # #    #      #  #  #
            ...     ####  ##  #  # #  # #  #  ##  #    ####   #   ##
            ... ''')
            'ZJHRKCPLYJ'
            >>> FONT_6X5.read_string('''
            ...      HH  HHHH H    HHHH H     HH  H   HHHHH  HH   HHH
            ...     H  H H    H    H    H    H  H H   HH    H  H H
            ...     H    HHH  H    HHH  H    H  H  H H HHH  H    H
            ...     H    H    H    H    H    H  H   H  H    H     HH
            ...     H  H H    H    H    H    H  H   H  H    H  H    H
            ...      HH  H    HHHH HHHH HHHH  HH    H  H     HH  HHH
            ... ''')
            'CFLELOYFCS'
            >>> FONT_6X5.read_string('''
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
            >>> FONT_6X5.read_string('''
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
            self._lookup_by_code(
                int(''.join(str(int(PIXELS[char])) for char in ''.join(letter)), 2)
            )
            for letter in zip(*(
                [line[k:k + self.char_width].ljust(self.char_width) for k in
                 range(0, len(line), self.char_width)]
                for line in dedent(ascii_text.strip('\n')).splitlines()
            ))
        )


FONT_6X5 = Font(
    char_height=6,
    char_width=5,
    chars={
        'A': 0x19297a52,
        'B': 0x392e4a5c,
        'C': 0x1928424c,
        'D': 0x39294a5c,
        'E': 0x3d0e421e,
        'F': 0x3d0e4210,
        'G': 0x19285a4e,
        'H': 0x252f4a52,
        'I': 0x1c42108e,
        'J': 0x0c210a4c,
        'K': 0x254c5292,
        'L': 0x2108421e,
        'O': 0x19294a4c,
        'P': 0x39297210,
        'R': 0x39297292,
        'S': 0x1d08305c,
        'T': 0x1c421084,
        'U': 0x25294a4c,
        'Y': 0x23151084,
        'Z': 0x3c22221e,
        ' ': 0x00000000,
        '☐': 0x01f8c63f,
    }
)

FONT_8X6 = Font(
    char_height=8,
    char_width=6,
    chars={
        'H': 0x8a28be8a28a2,
        'I': 0x70820820821c,
    }
)


FONT_10X8 = Font(
    char_height=10,
    char_width=8,
    chars={
        'A': 0x3048848484fc84848484,
        'C': 0x78848080808080808478,
        'F': 0xfc808080f88080808080,
        'G': 0x78848080809c84848c74,
        'H': 0x84848484fc8484848484,
        'J': 0x1c080808080808888870,
        'K': 0x848890a0c0c0a0908884,
        'L': 0x808080808080808080fc,
        'N': 0x84c4c4a4a494948c8c84,
        'P': 0xf8848484f88080808080,
        'R': 0xf8848484f89088888484,
        'X': 0x84844848303048488484,
        'Z': 0xfc0404081020408080fc,
    }
)
