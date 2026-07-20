PYTHON_RUN := uv run --frozen

.PHONY: sync verify

sync:
	uv sync --frozen

verify: sync
	rm -rf dist
	$(PYTHON_RUN) python scripts/build_catalog.py --output dist/catalog-a/index.json
	$(PYTHON_RUN) python scripts/build_catalog.py --output dist/catalog-b/index.json
	cmp dist/catalog-a/index.json dist/catalog-b/index.json
	$(PYTHON_RUN) python -m pytest -q
