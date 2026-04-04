# Ymir Documentation

This repository contains the full documentation for the Ymir language:
specifications, roadmap, design notes, and versioned change history.

Documentation is written primarily in **Org mode**, rendered using **Sphinx**
with the **ReadTheDocs theme**.

---

## Directory Structure

```text
conf.py              # Sphinx configuration
index.rst            # Documentation entry point
doc/doc.org          # Root documentation overview 
doc/spec/            # Formal language and runtime specifications 
doc/roadmap/         # Planned features and version targets 
doc/changes/         # Versioned change logs 
doc/design/          # Subsystem design documents 
doc/rationale/       # Motivations and rejected alternatives

```

All Org files are automatically included through the Sphinx `toctree`.

---

## Requirements

Install the documentation toolchain:

```bash
pip install sphinx sphinx-rtd-theme sphinxcontrib-org
pip install sphinx-autobuild
```

▶️ Building the Documentation

From the project root:

``` shell
sphinx-build -b html doc/ doc/_build/html
```

The generated site will be available at `doc/_build/html/index.html`

### Live Reload

For automatic rebuilds while editing:

``` shell
sphinx-autobuild doc/ doc/_build/html
```

This starts a local server and refreshes the page on every file save.

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

Roadmap entries, specs, and change logs must remain consistent.

