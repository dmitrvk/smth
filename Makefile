help:
	@echo 'Possible targets:'
	@echo '  help    display this help message'
	@echo '  test    run unit tests'

isort:
	isort --recursive --atomic smth tests

test:
	@coverage run --source smth -m unittest
	@coverage html
	@coverage xml
	@flake8 smth tests

