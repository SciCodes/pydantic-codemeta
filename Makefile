.PHONY: help sync test clean package check publish-test publish docker-test docker-package cff-check cff-validate format json-check json-format

UV ?= uv
DIST_DIR ?= dist
DC ?= docker compose
CFFCONVERT_IMAGE ?= ghcr.io/scicodes/cffconvert:v2026.08
CFF_FILE ?= CITATION.cff
JSON_FILES ?= codemeta.json

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
	@echo "  make cff-check    - validate $(CFF_FILE) with cffconvert"
	@echo "  make cff-validate - alias for cff-check"
	@echo "  make format       - format Python and Markdown with ruff and mdformat"
	@echo "  make json-check   - validate JSON files with python -m json.tool"
	@echo "  make json-format  - canonicalize JSON files in place with json.tool"

sync:
	$(UV) sync --extra test

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

cff-check:
	docker run --rm -v "$(CURDIR)":/data -w /data $(CFFCONVERT_IMAGE) \
		cffconvert --validate --infile $(CFF_FILE)

cff-validate: cff-check

format: json-format
	$(UV) run ruff format .
	$(UV) run ruff check --fix .
	$(UV) run mdformat .

json-check:
	@set -e; for f in $(JSON_FILES); do \
		echo "validating $$f"; \
		$(UV) run python -m json.tool "$$f" > /dev/null; \
	done

json-format:
	@set -e; for f in $(JSON_FILES); do \
		echo "formatting $$f"; \
		$(UV) run python -m json.tool --indent 2 "$$f" > "$$f.tmp" && mv "$$f.tmp" "$$f"; \
	done
