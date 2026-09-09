.PHONY: help sync test clean package check publish-test docker-test docker-package cff-check cff-validate format json-check json-format version release-check release release-test smoke-test

UV ?= uv
DIST_DIR ?= dist
DC ?= docker compose
CFFCONVERT_IMAGE ?= ghcr.io/scicodes/cffconvert:v2026.08
CFF_FILE ?= CITATION.cff
JSON_FILES ?= codemeta.json
VERSION ?= $(shell grep -m1 '^version = ' pyproject.toml | sed 's/.*"\(.*\)".*/\1/')
SMOKE_VERSION ?= $(VERSION)

help:
	@echo "Common targets:"
	@echo "  make sync         - install project + test and dev groups with uv"
	@echo "  make test         - run test suite locally"
	@echo "  make clean        - remove local build/test artifacts"
	@echo "  make package      - build source and wheel distributions"
	@echo "  make check        - run twine checks on built artifacts"
	@echo "  make publish-test - upload package to TestPyPI"
	@echo "  make release-test - full TestPyPI rehearsal: clean, test, package, check, upload"
	@echo "  make smoke-test  - install from TestPyPI and import in an isolated env"
	@echo "  make docker-test  - run test suite in Docker"
	@echo "  make docker-package - build distributions in Docker"
	@echo "  make cff-check    - validate $(CFF_FILE) with cffconvert"
	@echo "  make cff-validate - alias for cff-check"
	@echo "  make format       - format Python and Markdown with ruff and mdformat"
	@echo "  make json-check   - validate JSON files with python -m json.tool"
	@echo "  make json-format  - canonicalize JSON files in place with json.tool"
	@echo "  make version      - print the current package version"
	@echo "  make release-check - verify release prerequisites for v$(VERSION)"
	@echo "  make release      - tag and push release v$(VERSION)"

sync:
	$(UV) sync

test:
	$(UV) run python -m pytest -q -s

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

version:
	@echo $(VERSION)

release-check:
	@test -n "$(VERSION)" || { echo "error: could not read version from pyproject.toml"; exit 1; }
	@echo "$(VERSION)" | grep -Eq '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$$' \
		|| { echo "error: $(VERSION) is not a valid SemVer 2.0.0 version"; exit 1; }
	@git tag --list "v$(VERSION)" | grep -q . \
		&& { echo "error: tag v$(VERSION) already exists"; exit 1; } || true
	@grep -q "## \[$(VERSION)\]" CHANGELOG.md \
		|| { echo "error: CHANGELOG.md has no entry for $(VERSION)"; exit 1; }
	@echo "Release v$(VERSION) is ready to tag."

release: release-check test check
	git add pyproject.toml CHANGELOG.md
	git commit -m "release v$(VERSION)"
	git tag "v$(VERSION)"
	git push origin main
	git push origin "v$(VERSION)"

release-test: clean test package check publish-test
	@echo "TestPyPI release v$(VERSION) complete."
	@echo "Run 'make smoke-test' to verify the published package installs."

smoke-test:
	@echo "Installing pydantic-codemeta==$(SMOKE_VERSION) from TestPyPI..."
	UV_INDEX_URL="https://test.pypi.org/simple/" \
	UV_EXTRA_INDEX_URL="https://pypi.org/simple/" \
	$(UV) run --no-project --with "pydantic-codemeta==$(SMOKE_VERSION)" \
		python -c "from pydantic_codemeta import CodeMeta; print('smoke test OK:', CodeMeta.__name__)"
