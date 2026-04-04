# Ymir Book

This directory contains the building of the Ymir presentation book. This book is
aiming new developpers who may have no knowledge of compute science, and want to
start learning the language. It's not a specification - but a training course.

## Requirements

The book is written in latex, and uses `lualatex` as builder to produce the pdf
file.

## Building the book

```
$ make # simple checking build, no toc, no bib, building
$ make refs # full build with toc and bib

$ make clean
```

The result book is `main.pdf`.


## Progress

The file `progress.org` is the roadmap of the book, it defines the chapters that
have been written, the concept that have been explained (and where) - and what
is still missing, using a kanban system.
