install:
	pip install -r requirements.txt

make checks: pylint doctests

pylint:
	pylint --rcfile=.pylintrc common

doctests:
	py.test --doctest-modules
