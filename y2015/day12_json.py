import json


def sumj(d, fv=None) -> int:
    if isinstance(d, int):
        return d

    elif isinstance(d, list):
        return sum(sumj(v, fv) for v in d)

    elif isinstance(d, dict):
        return (
            sum(sumj(v, fv) for k, v in d.items())
            if fv is None or all(v != fv for v in d.values())
            else 0
        )

    elif isinstance(d, str):
        return 0

    else:
        raise ValueError(f"unsupported type {type(d).__name__}")


if __name__ == '__main__':
    data = json.load(open("data/12-input.json"))
    print(f"part 1: {sumj(data)}")
    print(f"part 2: {sumj(data, fv='red')}")
