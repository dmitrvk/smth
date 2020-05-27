help:
	@echo 'Possible targets:'
	@echo '  help    display this help message'
	@echo '  test    run unit tests'

test:
	@coverage run --source smth -m unittest
	@coverage html
	@coverage xml

