install:
	pip install -r requirements.txt

checks: mypy pylint doctests

mypy:
	# TODO: y2015 y2016 y2017 y2018 y2019 y2020 y2021
	mypy -p common

pylint:
	# TODO: y2017 y2018 y2019
	pylint --rcfile=.pylintrc common y2015 y2016 y2020 y2021

doctests:
	py.test --doctest-modules
