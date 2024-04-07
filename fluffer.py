import re
import os
import json
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

default_format_level = "human"
compiled_graph_path = "output.json"
output_directory = "queries"
sqlfluff_confg = ".sqlfluff"
introduction = [
    "Starting fluffer.py",
    f"This runs sqlfluff against tehe compiled graph, found in {output_directory}",
    f"If sqlfluff is installed in VS Code, you can also visually inspect each file in {output_directory}, which follows the same structure as /definitions",
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
        ["-- file://./../definitions/assert.sqlx", re.sub(r"^\n", "", parsed_operation)]
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

logging.info(f"Writing {len(operations_to_write)} operations to {output_directory}")

for path, contents in operations_to_write:
    os.makedirs(os.path.dirname(path.split(".")[0]), exist_ok=True)
    with open(path, "w") as f:
        f.write(contents)

logging.info("Finished writing files")


def run_sqlfluff():
    logging.info(f"Running sqlfluff on {output_directory}")
    base = f"sqlfluff lint {output_directory}"
    args = [f"--format='{default_format_level}'"]
    log_file = "sqlfluff_logs.txt"
    subprocess.run(f"{base} {' '.join(args)} > {log_file}", shell=True)


run_sqlfluff()
logging.info("Finished!")
