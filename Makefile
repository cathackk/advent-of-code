install:
	pip install --upgrade pip wheel setuptools
	pip install -r requirements.txt

checks: mypy pylint doctests

mypy:
	# TODO: y2019
	mypy -p common -p meta -p y2015 -p y2016 -p y2017 -p y2018 -p y2020 -p y2021

pylint:
	# TODO: y2019
	pylint --rcfile=.pylintrc common meta y2015 y2016 y2017 y2018 y2020 y2021

doctests:
	py.test --doctest-modules


create-readme:
	python3 -m meta.create_readme
