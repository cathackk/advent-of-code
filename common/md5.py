import _md5


def md5(val: str) -> str:
    """
        >>> md5('abc0')
        '577571be4de9dcce85a041ba0410f29f'
    """
    # pylint: disable=unexpected-keyword-arg
    return _md5.md5(val.encode(), usedforsecurity=False).hexdigest()
