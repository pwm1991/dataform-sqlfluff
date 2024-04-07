# Dataform <> SQLFluff

Compiles the Dataform graph and executes SQLFluff on the compiled SQL files, with the option to get a diff-quality score.

This was a 2am thought and a Sunday-afternoon project while unbelievably hungover so there's some work to do (it's one big file)

``` python
py fluffer.py --mode=[fluff,diff] --format=[human,github-annotations etc]
```

Or, for the lols: `make fluffer`

Requires:

* Node (`npm i`)
* Dataform CLI (`npm install -g @dataform/cli`)
* Python 3.11

Yep it's primarily a Node project with a Python script. SQLFluff doesn't support Dataform and the Dataform built in-linter kind of sucks.

## FAQs

### Why not just use the Dataform linter?

It uses `sql-formatter`, which is great, but the rules are hardcoded into `dataform/cli` and I don't want to do Google's work. It's also not as good as sqlfluff.

### Is it okay to write the full queries to the repo?

Well...

We *want* to commit /queries in, because the benefits of doing so are:
1. Comparing branch sql to main and diffing
2. Being able to use the compilation elsewhere (Sonarcloud, other static analysers)

The security downside is the PROJECT_ID, but that is in `dataform.json` anyway. When we move to DF 3.0 and release configs via Terraform, we can set `dataform.json` as some base values and override via TF..

### Will someone try to commit code after editing the queries directory?

100%.

### Will it work?

Yeah its great. It will struggle on JS-inserted code by Dataform, because Dataform doesn't do any indentions. Easy to fix - we can just put a method into Storm that does lpad and sql-formatter in one, which isn't the worst idea in the world.

So we could try it on:

* BDP Utils (most programmatic SQL)
* BDP Core (most complex JS)
* Sales Online (most complex SQL)

### Actionable?

Kind of. We will be assessing the *queries* directory rather than /definitions, which is why I've put a relative link at the top of each file, so there's a bit of gymnastics to do.

TODO:

1. Tests!
2. Type checking etc
3. Probably more than 1 file lol
4. Speak to AB about private package store
5. Requirements.txt probably isn't fully up to date
