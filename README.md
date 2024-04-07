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

The main issue is the PROJECT_ID, which is in `dataform.json` anyway. When we move to DF 3.0 and release configs via Terraform, we can set `dataform.json` as some base values and have all the proper vars elsewhere. Many (digital squad) repos are already doing envs properly.

The other neat thing is now that we have the compiled queries in the repo, chucking it into something like SonarCloud or any other tooling is pretty easy.

### Will someone try to commit code after editing the queries directory?

I guarantee it.

We *want* to commit /queries in, because we want to be able to run diff-quality on the branch. This will help to enforce standards. But it will lead to some weirdness for newbies. Could push it into a specific branch.

### Will it work?

It works on this simple thing!

I reckon it will struggle with more complicated JS insertions - mainly within my products (BDP etc) that make heavy use of JavaScript to insert/modify SQL. It will complain about indentations, so we'll have add sqfluff rules in these areas. Or just sort the indenting.

So we could try it on:

* BDP Utils (most programmatic SQL)
* BDP Core (most complex JS)
* Sales Online (most complex SQL)

### Actionable?

Yup! We can chuck this into gh-actions nicely and use the diff-mode to enforce standards.

TODO:

1. Tests!
2. Type checking etc
3. Probably more than 1 file lol
4. Speak to AB about private package store
5. Requirements.txt probably isn't fully up to date
