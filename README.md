Dataform <> Sqlfluff

Compiles the Dataform graph and executes SQlFluff on the compiled SQL files.

Run with: `py fluffer.py`

Requires:

* Node
* Dataform CLI (`npm install -g @dataform/cli`)
* Python 3.11

Yep it's primarily a Node project with a Python script. I'm sorry, but SQLFluff doesn't support Dataform and the Dataform built in-linter kind of sucks.
