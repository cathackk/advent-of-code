install:
	pip install -r requirements.txt

checks: mypy pylint doctests

mypy:
	# TODO: y2017 y2018 y2019 y2020
	mypy -p common -p meta -p y2015 -p y2016 -p y2021

pylint:
	# TODO: y2017 y2018 y2019
	pylint --rcfile=.pylintrc common meta y2015 y2016 y2020 y2021

doctests:
	py.test --doctest-modules
