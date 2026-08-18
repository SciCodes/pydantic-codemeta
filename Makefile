.PHONY: help sync test clean package check publish-test publish docker-test docker-package

UV ?= uv
DIST_DIR ?= dist
DC ?= docker compose

help:
	@echo "Common targets:"
	@echo "  make sync         - install project + test and dev groups with uv"
	@echo "  make test         - run test suite locally"
	@echo "  make clean        - remove local build/test artifacts"
	@echo "  make package      - build source and wheel distributions"
	@echo "  make check        - run twine checks on built artifacts"
	@echo "  make publish-test - upload package to TestPyPI"
	@echo "  make publish      - upload package to PyPI"
	@echo "  make docker-test  - run test suite in Docker"
	@echo "  make docker-package - build distributions in Docker"

sync:
	$(UV) sync --extra test --group dev

test:
	$(UV) run --extra test python -m pytest -q -s

clean:
	rm -rf $(DIST_DIR) build
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
	find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" \) -prune -exec rm -rf {} +

package: clean
	$(UV) build

check: package
	$(UV) run twine check $(DIST_DIR)/*

publish-test: package
	$(UV) run twine upload --repository testpypi $(DIST_DIR)/*

publish: package
	$(UV) run twine upload $(DIST_DIR)/*

docker-test:
	$(DC) run --rm test

docker-package:
	$(DC) run --rm package
