import re
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

compiled_graph_path = "output.json"
output_directory = "queries"
introduction = [
    "Starting fluffer.py",
    f"This runs sqlfluff against the compiled graph, found in {output_directory}",
    f"If sqlfluff is installed in VS Code, you can also visually inspect each file in {output_directory}, which follows the same structure as /definitions",
]
for line in introduction:
    logging.info(line)


if not (os.path.exists(output_directory)):
    logging.info(f"Output directory not found, creating {output_directory}")
    os.makedirs(output_directory)

try:
    f = open(compiled_graph_path, "r")
    compiledGraph = json.load(f)
except FileNotFoundError:
    logging.critical(
        f'File "{compiled_graph_path}" not found. Have you run dataform compile? Usually this is `npm run dataform:output`'
    )
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
    for operation in compiledGraph.get(area) or []:
        operations_to_write.append(parse_graph(operation))

logging.info(f"Writing {len(operations_to_write)} operations to {output_directory}")

for path, contents in operations_to_write:
    os.makedirs(os.path.dirname(path.split(".")[0]), exist_ok=True)
    with open(path, "w") as f:
        f.write(contents)

logging.info("Finished writing files")

# Run sqlfluff on the output directory
logging.info(f"Running sqlfluff on {output_directory}")
os.system(f"sqlfluff --config .sqlfluff")
