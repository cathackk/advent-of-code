## To Be Done

- [ ] integrate **black**
- [ ] use [ocr](common/ocr.py) where applicable
- [ ] rework [2017](y2017)
- [ ] rework and finish [2018](y2018)
- [ ] rework [2019](y2019)
- [ ] finish [linter integration TODOs](Makefile) for all packages
- [ ] `make run` to run all years all days
- [ ] use `click` in [create_readme.py](meta/create_readme.py)


## Done

- [x] `.split('\n')` -> `.splitlines()`
- [x] integrate [direnv](.envrc)
- [x] index in [readme](README.md)
- [x] automatic [creation](meta/create_readme.py) of [readme](README.md) via git [hooks](.hooks/pre-commit)
- [x] split [utils](common/utils.py)
- [x] integrate **mypy**
- [x] include the **mypy** release with `match` support
