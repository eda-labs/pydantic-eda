#!/usr/bin/env python3

import argparse
import json
import logging
import shutil
import subprocess
import sys
from pathlib import Path

from rich.logging import RichHandler
from rich.traceback import install

# Replace the basic logging config with Rich handler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

logging.getLogger("httpx").setLevel(logging.INFO)

install(show_locals=False)

logger = logging.getLogger(__name__)


class Generator:
    def __init__(
        self,
        output_dir: str,
        version: str,
        verbose: bool,
    ):
        # openapi repo
        self.repo_url = "https://github.com/eda-labs/openapi"

        # a dir to clone the openapi repo
        self.build_dir = Path("./build")
        # delete build dir if it exists before creating an empty one
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(exist_ok=True)

        self.output_dir = Path(output_dir)
        self.verbose = verbose

        self.version = version

        if self.verbose:
            logger.setLevel(logging.DEBUG)

    def clone_repo(self):
        """
        Clone the openapi repo under the build dir
        """
        subprocess.run(
            ["git", "clone", "-b", self.version, self.repo_url, self.build_dir],
            check=True,
            stderr=subprocess.DEVNULL,
        )

    def process_specs(self):
        """
        Process the specs under the build dir
        """

        # Process apps directory
        apps_dir = self.build_dir.joinpath("apps")
        if not apps_dir.exists():
            logger.info("apps dir not found in the cloned specs repo")
            sys.exit(1)

        for spec_file in apps_dir.glob("**/*.json"):
            # uncomment and change to a desired name if you want to generate
            # just one model
            # if spec_file.name != "services.json":
            #     continue

            logger.info(f"Processing {spec_file}")
            api_name, api_version = extract_name_version(spec_file)
            logger.debug(f"API name: {api_name}, API version: {api_version}")

            self.sanitize_schema_objects(spec_file, api_name, api_version)

            self.generate_classes_for_spec(spec_file, api_name, api_version)

        # process the core spec that is a single file in its own dir
        core_dir = self.build_dir.joinpath("core")
        if not core_dir.exists():
            logger.info("core dir not found in the cloned specs repo")
            sys.exit(1)

        for spec_file in core_dir.glob("**/*.json"):
            api_name = "core"
            # core api has a v0.0.1 in the spec but that will change
            # for now use v1alpha1
            api_version = "v1alpha1"
            logger.debug(f"API name: {api_name}, API version: {api_version}")
            self.sanitize_schema_objects(spec_file, api_name, api_version)
            self.generate_classes_for_spec(spec_file, api_name, api_version)

    def generate_classes_for_spec(
        self, spec_file: Path, api_name: str, api_version: str
    ):
        """
        Generate Pydantic classes for the given sanitized spec file
        :param spec_file: Path to the spec file
        :param api_name: Name of the API
        :param api_version: Version of the API
        """

        app_parent_dir = "apps"

        # when generating models for the core api we put it right
        # under the pydantic_eda output dir, while all the apps
        # go under pydantic_eda/apps/
        if spec_file.parts[1] == "core":
            app_parent_dir = ""

        dest_file = self.output_dir.joinpath(
            app_parent_dir, api_name, api_version, "models.py"
        )

        # Create all parent directories of the dest file
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "datamodel-codegen",
            "--input",
            spec_file,
            "--input-file-type",
            "openapi",
            "--openapi-scopes",
            "schemas",
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--formatters",
            "ruff-format",
            "--use-annotated",
            "--parent-scoped-naming",
            "--collapse-root-models",
            "--disable-timestamp",
            "--reuse-model",
            "--keep-model-order",
            "--use-schema-description",
            "--enum-field-as-literal",
            "all",
            "--output",
            dest_file,
        ]

        # the core API should use the file name as the output of the DMCG command
        # the core app does not have apps dir in its URL
        # if "apps" not in url_parts and module_name == "core":
        #     cmd[-1] = str(output_dir) + "/core.py"

        try:
            logger.info(f"Generating models for {spec_file}...")
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error generating models for {spec_file}: {e}")

    def sanitize_schema_objects(self, spec_file: Path, api_name: str, api_version: str):
        """
        Sanitize schema objects by removing extra info like com.nokia.com, app name and api version
        :param spec_file: Path to the spec file
        """
        # Open and load the JSON file
        with open(spec_file, "r") as f:
            spec_data = json.load(f)

            if (
                "components" not in spec_data
                or "schemas" not in spec_data["components"]
            ):
                logger.info(f"No schemas found in {spec_file}")
                return

            for name, data in spec_data["components"]["schemas"].items():
                logger.debug(f"Schema name: {name}")

                # gating flag to track if any schemas were changed
                # when flipped to true it means we need to write the in-mem file to disk in the output dir
                modified = False

                # Check and fix the info.title field if it has a trailing dot
                # if "info" in spec_data and "title" in spec_data["info"]:
                #     title = spec_data["info"]["title"]
                #     if title.endswith("."):
                #         spec_data["info"]["title"] = title.rstrip(".")
                #         logger.debug(
                #             f"Removed trailing dot from title: {title} -> {spec_data['info']['title']}"
                #         )
                #         modified = True

                schemas = spec_data["components"]["schemas"]
                new_schemas = {}

                # Create new schema dictionary with renamed keys
                for schema_name, schema_def in schemas.items():
                    # if we have a dotted module name, dmcg will create bad shit
                    # we need to remove the dotted parts and only keep the name
                    # as this will make the schema clean
                    # so for com.nokia.eda.services.v1alpha1.BridgeDomainList
                    # we will keep only BridgeDomainList
                    # we also need to ensure that all references to the original schema node
                    # are updated to the new name
                    if "com.nokia.eda" in schema_name:
                        new_name = schema_name.split(".")[-1]

                        logger.debug(f"Renaming schema: {schema_name} -> {new_name}")

                        new_schemas[new_name] = schema_def

                        modified = True
                    else:
                        new_schemas[schema_name] = schema_def

                # Replace the original schemas with the renamed ones
                if modified:
                    spec_data["components"]["schemas"] = new_schemas

                    # Remove the paths section entirely as it's not needed for model generation
                    # and it contains old ref links with dots in schema names
                    if "paths" in spec_data:
                        logger.debug(f"Removing paths section from {spec_file}")
                        del spec_data["paths"]

                    # Recursively update all $ref values in the entire spec
                    self._update_refs(spec_data, api_name, api_version)

                    # Write the modified spec back to the file
                    with open(
                        spec_file,
                        "w",
                    ) as f:
                        json.dump(spec_data, f, indent=2)
                    logger.info(f"Wrote schema to {spec_file}")

    def generate_models(self):
        output_dir = self.output_dir
        output_dir.mkdir(exist_ok=True)

        self.clone_repo()

        self.process_specs()

        # for spec in specs[self.version]:
        #     url_parts = spec["url"].split("/")
        #     module_name = url_parts[-1].replace(".json", "")

    def _update_refs(self, obj, api_name: str, api_version: str):
        """
        Recursively update all $ref values in the object to use simplified schema names
        :param obj: The object to update
        """
        if isinstance(obj, dict):
            for key, value in list(obj.items()):
                if (
                    key == "$ref"
                    and isinstance(value, str)
                    and f"#/components/schemas/com.nokia.eda.{api_name}.{api_version}"
                    in value
                ):
                    # replace the unnecessary parts from the ref value
                    new_value = value.replace(
                        f"com.nokia.eda.{api_name}.{api_version}.", ""
                    )
                    obj[key] = new_value
                elif isinstance(value, (dict, list)):
                    self._update_refs(value, api_name, api_version)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    self._update_refs(item, api_name, api_version)


def extract_name_version(file: Path) -> tuple[str, str]:
    """Extract the API name and version from the spec file name.
    Spec filename contains the build dir, e.g.
    build/apps/bootstrap.eda.nokia.com/v1alpha1/bootstrap.json

    This func then extracts the app/api name -> bootstrap
    and api version -> v1alpha1
    """
    # split the file name by the dot
    parts = file.parts
    # the name is the filename without the extension
    name = file.stem
    # the version is the second to last part
    version = parts[-2]

    return name, version


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Discover OpenAPI specifications and generate Pydantic models."
    )

    parser.add_argument(
        "--output",
        type=str,
        default="./pydantic_eda",
        help="Path to the output directory.",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="main",
        help="openapi repo version (tag) to get the models from. Default: main",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging. Default: False",
    )

    args = parser.parse_args()

    generator = Generator(
        output_dir=args.output,
        version=args.version,
        verbose=args.verbose,
    )
    generator.generate_models()
