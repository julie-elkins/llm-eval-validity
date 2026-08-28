# The offline analyses need no dependencies, no network and no credentials -- `make analyse`
# runs the whole study except the judge stage. That separation is deliberate: a reader should
# be able to reproduce every number in the write-ups without an API key, and only the judge
# validation should cost anything.

.PHONY: analyse test precision discrimination docs clean

analyse: precision discrimination

precision:
	uv run python -m validity.precision

discrimination:
	uv run python -m validity.discrimination

test:
	uv run --with pytest python -m pytest tests/ -q

# Regenerates the committed reports from the fixture, so a stale doc is a visible diff rather
# than something a reader has to take on trust.
docs:
	uv run python -m validity.precision > docs/precision.md
	uv run python -m validity.discrimination > docs/item-analysis.md

clean:
	rm -rf .pytest_cache **/__pycache__
