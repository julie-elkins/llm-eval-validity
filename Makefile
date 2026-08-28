# The offline analyses need no dependencies, no network and no credentials -- `make analyse`
# runs the whole study except the judge stage. That separation is deliberate: a reader should
# be able to reproduce every number in the write-ups without an API key, and only the judge
# validation should cost anything.

.PHONY: analyse test precision discrimination reliability cutscore judge docs clean

analyse: precision discrimination reliability cutscore

precision:
	uv run python -m validity.precision

discrimination:
	uv run python -m validity.discrimination

# Reads the recorded verdicts in runs/. Free and offline; says so and stops if runs/ is empty.
reliability:
	uv run python -m validity.reliability

# Reads the fixture only. The standards it judges against are declared in the module, not
# derived from the data, so this target is deterministic and free.
cutscore:
	uv run python -m validity.cutscore

# The only target that costs money and needs credentials. Dry-runs by default: it prints the
# planned call count and the estimated spend, and sends nothing until `--go`. Resumable, so an
# interrupted run does not re-bill the turns it already answered.
#   make judge JUDGE=sonnet-5 ARGS="--runs 5 --go"
JUDGE ?= sonnet-5
judge:
	uv run --extra judge python -m validity.judge $(JUDGE) $(ARGS)

test:
	uv run --with pytest python -m pytest tests/ -q

# Regenerates the committed reports from the fixture, so a stale doc is a visible diff rather
# than something a reader has to take on trust. docs/methodology.md and
# docs/executive-summary.md are written by hand and are not touched by this target.
docs:
	uv run python -m validity.precision > docs/precision.md
	uv run python -m validity.discrimination > docs/item-analysis.md
	uv run python -m validity.reliability > docs/judge-validation.md
	uv run python -m validity.cutscore > docs/cut-score.md

clean:
	rm -rf .pytest_cache **/__pycache__
