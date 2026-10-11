# Development

## Project Layout

There are a number of files for build, test, and continuous integration in the root of the project, but in general, the
project is broken up like so.

```
├── docs
│   └── src
│       ├── dictionary
│       └── markdown
├── bracex
├── requirements
└── tests
```

Directory             | Description
--------------------- | -----------
`docs/src/dictionary` | Contains the spell check wordlist(s) for the project.
`docs/src/markdown`   | Contains the content for the documentation.
`bracex`              | Contains the source code for the project.
`requirements`        | Contains files with lists of dependencies that are required for the project, and required for continuous integration.
`tests`               | Contains unit test files.

## Coding Standards

Coding standards are enforced using @astral-sh/ruff. The environment can be setup and run as shown below.

```console
$ hatch run +py=3.14 dev:lint
```

## Coding Types

We use @python/mypy to enforce typing. It can be run as shown below.

```console
$ hatch run +py=3.14 dev:mypy
```

## Building and Editing Documents

Documents are in Markdown (with some additional syntax) and converted to HTML via Python Markdown and this extension
bundle. The documentation site is built with @zensical/zensical.

To build docs:

```console
$ hatch run docs:build
```

To serve docs and to live preview in a browser:

```console
$ hatch run docs:serve
```

To clean the documents:

```console
$ hatch run docs:clean
```

## Spell Checking Documents

During validation, we build the docs and run a spell checker on them.  The spell checker uses @facelessuser/pyspelling
and [Aspell][aspell]. As it can be trickier to run Aspell under Windows, it is not expected that everyone will install
and run the spell checker locally.  In order to perform the spell check, just run the following command:

```console
$ hatch run docs:spellcheck
```

## Validation Tests

In order to preserve good code health, a test suite has been put together with pytest (@pytest-dev/pytest). There are
currently two kinds of tests: syntax and targeted.  To run these tests, you can use the following command:

If you wish to run the tests locally, just run:

```console
$ hatch run +py=3.14 dev:tests
```

## Code Coverage

When running the validation tests, it is setup to track code coverage via the Coverage
(@bitbucket:ned/coveragepy) module.  Coverage is run on each Python environment.  If you've made changes to
the code, you can clear the old coverage data, assuming coverage is installed, by running:

```console
$ coverage erase
```

Then run each unit test environment to and coverage will be calculated. All the data from each run is merged together.
HTML is output for each file in `.cov`.  You can use these to see areas that are not covered/exercised yet with testing.

--8<-- "links.txt"
