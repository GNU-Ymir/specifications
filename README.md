# Ymir Documentation

This repository contains the full documentation for the Ymir language:
specifications, roadmap, design notes, and versioned change history.

Documentation is written primarily in **Org mode**, transformed to **Markdown**
with pandoc, and rendered using **Sphinx** with the **ReadTheDocs theme**.

---

## Directory Structure

```text
src/conf.py    # Sphinx configuration
src/index.rst  # Documentation entry point
src/doc.org    # Root documentation overview 
src/spec/      # Formal language and runtime specifications 
src/roadmap/   # Planned features and version targets 
src/changes/   # Versioned change logs 
src/design/    # Subsystem design documents 
src/rationale/ # Motivations and rejected alternatives

book/ # Ymir language presentation book
```

The `book/` directory contains it's own building toolchain, (cf. `book/README.md`). 

---

## Requirements

Install the documentation toolchain:

```bash
$ python -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r src/requirements.txt
```

## Building the Documentation

From the project root:

``` shell
(.venv) python src/build.py -b
```

The generated site will be available at `.doc/_build/html/index.html`

## Documentation Philosophy

Specifications must remain concise, principled, and implementation‑agnostic.

Every feature has a version lifecycle:
- Implemented in X.Y
- Planned for X.Y
- Under consideration
- Deprecated in X.Y
- Removed in X.Y

Every change is categorized:
- Addition
- Modification
- Extension
- Deprecation
- Removal
- Fix
- Clarification

