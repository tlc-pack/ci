tests:
	PYTHONPATH=. pytest --tb=native test/

prepare:
	zip tvm_bot.zip lambda_function.py

lint:
	git ls-files . | xargs pre-commit run --files
