install:
	pip install --upgrade pip wheel setuptools
	pip install -r requirements.txt


checks: mypy pylint doctests

mypy:
	# TODO: y2019
	mypy -p common -p meta -p y2015 -p y2016 -p y2017 -p y2018 -p y2020 -p y2021 -p y2022 -p y2023

pylint:
	# TODO: y2019
	pylint --rcfile=.pylintrc common meta y2015 y2016 y2017 y2018 y2020 y2021 y2022 y2023

doctests:
    # TODO: y2019
	py.test --doctest-modules common meta y2015 y2016 y2017 y2018 y2020 y2021 y2022 y2023


checks-2023: mypy-2023 pylint-2023 doctests-2023

mypy-2023:
	mypy -p common -p meta -p y2023

pylint-2023:
	pylint --rcfile=.pylintrc common meta y2023

doctests-2023:
	py.test --doctest-modules common meta y2023


create-readme:
	python3 -m meta.create_readme


run-day:
	python3 -m meta.run --year $(YEAR) --day $(DAY)


run-year:
	python3 -m meta.run --year $(YEAR) --day all


run:
	# TODO: meta.run --all
	python3 -m meta.run --year 2015 --day all
	python3 -m meta.run --year 2016 --day all
	python3 -m meta.run --year 2017 --day all
	# TODO: python3 -m meta.run --year 2018 --day all
	# TODO: python3 -m meta.run --year 2019 --day all
	python3 -m meta.run --year 2020 --day all
	python3 -m meta.run --year 2021 --day all
	python3 -m meta.run --year 2022 --day all
	python3 -m meta.run --year 2023 --day all
