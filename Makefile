PYTHON_RUN := uv run --frozen

.PHONY: sync verify

sync:
	uv sync --frozen

verify: sync
	rm -rf dist
	$(PYTHON_RUN) python scripts/verify_bundle_pin.py
	$(PYTHON_RUN) python -m pytest -q
	$(PYTHON_RUN) python scripts/validate_agents.py --output dist/catalog-a/index.json
	$(PYTHON_RUN) python scripts/validate_agents.py --output dist/catalog-b/index.json
	cmp dist/catalog-a/index.json dist/catalog-b/index.json
	$(PYTHON_RUN) python scripts/generate_oasf_projection.py --output dist/catalog-a/oasf.json
	$(PYTHON_RUN) python scripts/generate_oasf_projection.py --output dist/catalog-b/oasf.json
	cmp dist/catalog-a/oasf.json dist/catalog-b/oasf.json
	install -m 0644 dist/catalog-a/index.json catalog/index.json
	install -m 0644 dist/catalog-a/oasf.json catalog/oasf.json
