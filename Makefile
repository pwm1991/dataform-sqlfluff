activate:
	. .venv/bin/activate

install:
	pip install -r requirements.txt

fluff:
	python3 fluffer.py

fluff-diff:
	diff-quality --violations sqlfluff --compare-branch origin/main
