check:
	pylint --rcfile=.pylintrc common
	py.test --doctest-modules
