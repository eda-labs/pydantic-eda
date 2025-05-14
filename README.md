# Pydantic EDA

**WIP!**

Pydantic models for EDA OpenAPI spec. Models are generated for the EDA Core API as well as for the apps shipped with EDA Playground at the time of the generation.

## Usage

## Generation

Store Github auth token in a `GH_AUTH_TOKEN` environment variable. For example, with `gh` cli:

```
export GH_AUTH_TOKEN=$(gh auth token)
```

Install dev dependencies:

```
uv add --dev 'datamodel-code-generator[http]' rich ruff httpx
```

Generate models for a specific version of openapi repo:

```
python gen_models.py --version v25.4.1 --no-cache
```

Running with `--no-cache` will download the cache file so that subsequent model generation runs could omit the `--no-cache` flag and leverage the local cache.
