#!/usr/bin/env python3

import argparse
import json
import logging
import os
import subprocess
from pathlib import Path
from venv import logger

import httpx
from httpx import HTTPStatusError, RequestError
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


class OpenAPIDiscovery:
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        version: str,
        verbose: bool,
        use_cache: bool,
    ):
        self.base_url = "https://api.github.com/repos/eda-labs/openapi"
        self.raw_base = f"https://raw.githubusercontent.com/eda-labs/openapi/{version}"
        self.gh_token = os.environ.get("GH_AUTH_TOKEN")
        if self.gh_token == "":
            logger.error("GH_AUTH_TOKEN environment variable is not set.")
            exit(1)

        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {self.gh_token}",
        }
        self.cache_file = Path("cached_specs.json")
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.use_cache = use_cache
        self.version = version

        if self.verbose:
            logger.setLevel(logging.DEBUG)

        # Configure retry strategy with httpx
        transport = httpx.HTTPTransport(
            retries=3,
        )

        self.client = httpx.Client(
            timeout=30.0,
            transport=transport,
            headers=self.headers,
            follow_redirects=True,
        )

    def get_contents(self, path=""):
        url = f"{self.base_url}/contents/{path}"
        logger.info(f"Fetching contents from: {url}")

        try:
            response = self.client.get(url)
            response.raise_for_status()

            # Rate limiting info
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining:
                logger.info(f"API calls remaining: {remaining}")

            content = response.json()
            if isinstance(content, str):
                raise ValueError(f"Unexpected response format: {content}")
            return content

        except HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            raise
        except RequestError as e:
            logger.error(f"Request error occurred: {e}")
            raise

    def load_cached_specs(self) -> dict[str, list[dict[str, str]]]:
        try:
            if self.cache_file.exists() and self.cache_file.stat().st_size > 0:
                with open(self.cache_file) as f:
                    cached = json.load(f)
                    return cached
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Cache read error: {e}")
        return {"": []}

    def save_specs_cache(self, specs):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(specs, f, indent=2)
        except OSError as e:
            logger.error(f"Failed to save cache: {e}")

    def discover_specs(self, use_cache=True) -> dict[str, list[dict[str, str]]]:
        if use_cache:
            cached = self.load_cached_specs()
            if cached:
                logger.info("Using cached specs")
                return cached

        specs = {self.version: []}
        specs_for_version = specs[self.version]

        # Check core path
        core_specs = self.get_contents("core")
        for spec in core_specs:
            if spec.get("type") == "file" and spec.get("name", "").endswith(".json"):
                specs_for_version.append(
                    {
                        "name": Path(spec["name"]).stem,
                        "url": f"{self.raw_base}/core/{spec['name']}",
                    }
                )

        # Check apps path
        apps = self.get_contents("apps")
        for app in apps:
            if app.get("type") == "dir":
                versions = self.get_contents(app["path"])
                for version in versions:
                    if version.get("type") == "dir":
                        files = self.get_contents(version["path"])
                        for file in files:
                            if file.get("name", "").endswith(".json"):
                                specs_for_version.append(
                                    {
                                        "name": app["name"].split(".")[0],
                                        "url": f"{self.raw_base}/{file['path']}",
                                    }
                                )

        if specs:
            self.save_specs_cache(specs)

        return specs

    def generate_models(self):
        output_dir = self.output_dir
        output_dir.mkdir(exist_ok=True)
        specs: dict[str, list[dict[str, str]]] = self.discover_specs(
            use_cache=self.use_cache
        )

        if not specs:
            logger.warning("No specs found!")
            return

        if self.version not in specs:
            logger.warning(f"No specs found for version {self.version}")
            return

        for spec in specs[self.version]:
            url_parts = spec["url"].split("/")
            module_name = url_parts[-1].replace(".json", "")

            cmd = [
                "datamodel-codegen",
                "--url",
                spec["url"],
                "--output-model-type",
                "pydantic_v2.BaseModel",
                "--use-annotated",
                "--enum-field-as-literal",
                "all",
                "--output",
                str(output_dir),
            ]

            # the core API should use the file name as the output of the DMCG command
            # the core app does not have apps dir in its URL
            if "apps" not in url_parts and module_name == "core":
                cmd[-1] = str(output_dir) + "/core.py"

            try:
                logger.info(f"Generating models for {module_name}...")
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Error generating models for {module_name}: {e}")

    def __del__(self):
        self.client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Discover OpenAPI specifications and generate Pydantic models."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="./openapi_specs",
        help="Path to the OpenAPI specifications directory. Default: ./openapi_specs",
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
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Force fresh discovery by ignoring the cache. Default: False",
    )

    args = parser.parse_args()

    discovery = OpenAPIDiscovery(
        input_dir=args.input,
        output_dir=args.output,
        version=args.version,
        verbose=args.verbose,
        use_cache=not args.no_cache,
    )
    discovery.generate_models()
