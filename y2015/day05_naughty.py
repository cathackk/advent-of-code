def is_nice(s: str) -> bool:
    return sum(1 for c in s if c in set('aeiou')) >= 3 \
           and any(c1 == c2 for c1, c2 in zip(s, s[1:])) \
           and not any(
               s[k:k+2] in {'ab', 'cd', 'pq', 'xy'}
               for k in range(len(s)-1)
           )


def is_nice2(s: str) -> bool:
    return any(
        s[i:i+2] == s[j:j+2]
        for i in range(len(s) - 3)
        for j in range(i + 2, len(s) - 1)
    ) and any(
        s[k-1] == s[k+1]
        for k in range(1, len(s) - 1)
    )


def test_is_nice():
    assert is_nice("ugknbfddgicrmopn")
    assert is_nice("aaa")
    assert not is_nice("jchzalrnumimnmhp")
    assert not is_nice("haegwjzuvuyypxyu")
    assert not is_nice("dvszwmarrgswjxmb")


def test_is_nice_2():
    assert is_nice2("qjhvhtzxzqqjkmpb")
    assert is_nice2("xxyxx")
    assert not is_nice2("uurcxstgmygtbstg")
    assert not is_nice2("ieodomkazucvgmuy")


if __name__ == '__main__':
    lines = [line.strip() for line in open("data/05-input.txt") if line.strip()]

    count1 = sum(1 for line in lines if is_nice(line))
    print(f"part 1: nice strings count is {count1}")

    count2 = sum(1 for line in lines if is_nice2(line))
    print(f"part 2: nice strings count is {count2}")
