set dotenv-load := true
set unstable := true

[private]
default:
    @just --list

[private]
cog:
    uv run --with cogapp --with nox --no-project cog -r CONTRIBUTING.md README.md pyproject.toml

[private]
fmt:
    @just --fmt

[private]
nox SESSION *ARGS:
    uv run noxfile.py --session "{{ SESSION }}" -- "{{ ARGS }}"

bootstrap:
    uv python install
    uv sync --frozen

bump *ARGS:
    uv run --with bumpver bumpver {{ ARGS }}

lint:
    uv run --with pre-commit-uv pre-commit run --all-files
    just fmt

lock *ARGS:
    uv lock {{ ARGS }}

test *ARGS:
    @just nox test {{ ARGS }}

testall *ARGS:
    @just nox tests {{ ARGS }}
