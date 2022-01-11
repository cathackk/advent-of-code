install:
	pip install -r requirements.txt

make checks: pylint doctests

pylint:
	# TODO: y2016 y2017 y2018 y2019 y2020
	pylint --rcfile=.pylintrc common y2015 y2021

doctests:
	py.test --doctest-modules
