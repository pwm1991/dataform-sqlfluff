import re
import os
import json
import logging
import subprocess
import argparse

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

parser = argparse.ArgumentParser(
    prog="Fluffer", description="Run sqlfluff on compiled Dataform graph"
)
parser.add_argument(
    "--format",
    default="human",
    help="Set the output format of sqlfluff. Default human",
)
parser.add_argument(
    "--mode",
    default="fluff",
    choices=["fluff", "diff"],
    help="Set the mode of the script. Default fluff",
)
args = parser.parse_args()

compiled_graph_path = "output.json"
output_directory = "queries"
sqlfluff_confg = ".sqlfluff"

default_format_level = args.format
run_diff_quality = args.mode == "diff"


introduction = [
    "Starting fluffer.py",
    f"Received arguments: {args}",
    f"This runs sqlfluff against the compiled graph, found in {output_directory}",
    f"When sqlfluff is installed in VS Code, you can also visually inspect each file in {output_directory}.",
    f"This follows the same structure as /definitions",
]
for line in introduction:
    logging.info(line)

if not (os.path.exists(sqlfluff_confg)):
    logging.warning(f"sqlfluff config not found.")

if not (os.path.exists(output_directory)):
    logging.info(f"Output directory not found, creating {output_directory}")
    os.makedirs(output_directory)

try:
    initial_compile = subprocess.check_output(
        "dataform compile --json",
        shell=True,
        encoding="utf-8",
    )
    compiled_graph = json.loads(initial_compile)
except subprocess.CalledProcessError:
    logging.critical(f"Error running dataform compile.")
    exit(1)
except json.JSONDecodeError:
    logging.critical(
        f'File "{compiled_graph_path}" is not a valid JSON file. Is the DAG valid?'
    )
    exit(1)


def set_file_path(path):
    new_path = path.replace(".sqlx", ".sql")
    new_path = re.sub(r"^definitions", output_directory, new_path)
    return new_path


def get_operation_contents(operation):
    parsed_operation = operation.get("query") or ";\n".join(operation.get("queries"))
    new_contents = "\n".join(
        [
            "-- Source: file://./../definitions/assert.sqlx",
            re.sub(r"^\n", "", parsed_operation),
        ]
    )
    return new_contents


def parse_graph(operation):
    path = set_file_path(operation.get("fileName"))
    contents = get_operation_contents(operation)
    return path, contents


areas = ["operations", "tables", "assertions"]

operations_to_write = []
for area in areas:
    logging.info(f"Parsing {area}")
    for operation in compiled_graph.get(area) or []:
        operations_to_write.append(parse_graph(operation))

logging.info(f"Writing {len(operations_to_write)} operations to /{output_directory}")

for path, contents in operations_to_write:
    os.makedirs(os.path.dirname(path.split(".")[0]), exist_ok=True)
    with open(path, "w") as f:
        f.write(contents)

logging.info("Finished writing files")


# Dunno why i put this in a method
def run_sqlfluff():
    logging.info(f"Running sqlfluff on {output_directory}")
    base = f"sqlfluff lint {output_directory}"
    # We should support github-annotations mode
    args = [f"--format='{default_format_level}'", " --warn-unused-ignores"]
    try:
        subprocess.run(f"{base} {' '.join(args)}", shell=True)
    except subprocess.CalledProcessError:
        logging.critical(f"Error running sqlfluff.")
        exit(1)


run_sqlfluff()

if run_diff_quality:
    logging.info("Running diff-quality")
    try:
        subprocess.run(
            "diff-quality --violations=sqlfluff --compare-branch=origin/main",
            shell=True,
        )
    except subprocess.CalledProcessError:
        logging.critical(f"Error running diff-quality.")
        exit(1)
else:
    logging.info("Skipping diff-quality. Run with mode=diff to enable.")

logging.info("Finished fluffer.py")
