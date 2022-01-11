install:
	pip install -r requirements.txt

make checks: pylint doctests

pylint:
	pylint --rcfile=.pylintrc common y2015

doctests:
	py.test --doctest-modules
