poetry_to_requirements:
	poetry export -f requirements.txt --output requirements.txt

poetry_install_deps:
	poetry install
	# Uninstall dataclasses from PyPI
	# https://github.com/allenai/allennlp/issues/4755
	pip uninstall -y dataclasses


build_image:
	docker buildx build -t ayesaac .


.PHONY : check-for-cuda
check-for-cuda :
	@python -c 'import torch; assert torch.cuda.is_available(); print("Cuda is available")'

# Testing helpers.
.PHONY : lint
lint :
	flake8 .

.PHONY : format
format :
	black --check .

.PHONY : typecheck
typecheck :
	mypy .

.PHONY : test
test :
	pytest --color=yes -rf --durations=40

.PHONY : test-with-cov
test-with-cov :
	pytest --color=yes -rf --durations=40 \
			--cov-config=.coveragerc \
			--cov=$(SRC) \
			--cov-report=xml

.PHONY : gpu-test
gpu-test : check-for-cuda
	pytest --color=yes -v -rf -m gpu


.PHONY : clean
clean :
	rm -rf .coverage \
			cov.xml \
			.pytest_cache \
			.allennlp_cache
