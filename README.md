# Pydantic EDA

Pydantic models for EDA OpenAPI spec. Models are generated for the EDA Core API as well as for the apps shipped with EDA Playground at the time of the generation.

## Usage

## Generation

Install dev dependencies:

```bash
uv sync --all-groups
```

Generate models for a specific version of the openapi repo (git ref):

```bash
python gen_models.py --version v25.4.1
```

The generation script clones the eda-labs/openapi repo at the provided ref and generated models from there.

## Modifications

The generation script transforms all schema objects in the source openapi files by removing `com.nokia.eda.<name>.<version>`, as DMCG project has issues with treating schema nodes with dots in their names as module-based schemas. Therefore, the original schema nodes undergo that mutation by the script.

## Versions

The following table matches the project version with the version of the EDA delivery from which the models were generated.

| pydantic_eda | EDA release |
| ------------ | ----------- |
| 0.3.2        | 25.4.1      |
| 0.4.0        | 25.8.1      |
