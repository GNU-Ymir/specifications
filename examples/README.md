# Examples of the Ymir book

The complete programs of the course, one file per program, grouped by chapter.
They are distributed with each release of the book, as
`ymir-book-examples_<version>.zip`, on the
[release page](https://github.com/GNU-Ymir/specifications/releases).

Each file is a whole program. Compile it with `gyc` and run it:

```
$ gyc calendar.yr -o calendar
$ ./calendar
```

| Directory | Chapter |
|---|---|
| `functions/` | Part I, chapter 4, *Functions* |
| `functions/solutions/` | the solutions of its exercises |

## For the authors

The book does not copy these programs: it reads them with
`\lstinputlisting{examples/...}`, so a file and its listing cannot drift apart.
`make check-listings` compiles every file, whether the book shows it or not, and
`make examples` builds the archive.
