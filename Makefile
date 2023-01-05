install:
	pip install --upgrade pip wheel setuptools
	pip install -r requirements.txt

checks: mypy pylint doctests

mypy:
	# TODO: y2019
	mypy -p common -p meta -p y2015 -p y2016 -p y2017 -p y2018 -p y2020 -p y2021 -p y2022

pylint:
	# TODO: y2019
	pylint --rcfile=.pylintrc common meta y2015 y2016 y2017 y2018 y2020 y2021 y2022

doctests:
    # TODO: y2019
	py.test --doctest-modules common meta y2015 y2016 y2017 y2018 y2020 y2021 y2022


create-readme:
	python3 -m meta.create_readme


run:
	python3 -m meta.run --year $(YEAR) --day $(DAY)
