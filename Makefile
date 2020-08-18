help:
	@echo 'Possible targets:'
	@echo '  dist    generate distribution archives'
	@echo '  help    display this help message'
	@echo '  isort   sort imports'
	@echo '  test    run unit tests and linter'

dist:
	python3 setup.py sdist bdist_wheel
	twine check dist/*

isort:
	isort --atomic smth tests

test:
	@coverage run --source smth -m unittest
	@coverage html
	@coverage xml
	@flake8 smth tests
