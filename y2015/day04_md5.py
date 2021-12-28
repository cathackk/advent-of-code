from itertools import count

from common.md5 import md5

if __name__ == '__main__':
    key = 'ckczppom'

    k1 = next(k for k in count(1) if md5(key + str(k)).startswith('00000'))
    print(f"part 1: k = {k1}")

    k2 = next(k for k in count(1) if md5(key + str(k)).startswith('000000'))
    print(f"part 2: k = {k2}")
