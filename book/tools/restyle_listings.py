#!/usr/bin/env python3
"""Apply the chapter-1 §1.2.2 layout convention to every Ymir listing in the book.

    foo (a, b, c)  ->  foo(a, b, c)
    a [0]          ->  a[0]
    x : i32        ->  x: i32

Only `colored*` listings (Ymir source) and prose \token{} are touched.
YIL dumps (myilVerb / lyilVerb) and shell listings (bashVerb) are compiler /
terminal output and are left verbatim.
"""
import re, sys, pathlib

# Keywords whose parenthesis/bracket is NOT a parameter list:
#   if (cond)      - control flow condition
#   let (a, b)     - destructuring pattern
#   mut (i32, f32) - tuple type
NO_ATTACH_PAREN = {'if', 'let', 'mut'}
#   copy [1,2]  dcopy [..]  dmut [i32]  mut [i32]  let [i,j,k]  in [1,2,3]
NO_ATTACH_BRACK = {'copy', 'dcopy', 'dmut', 'mut', 'let', 'in'}

STR = re.compile(r'"(?:[^"\\]|\\.)*"')
CHR = re.compile(r"'(?:[^'\\]|\\.)*'")


def transform_code(s):
    """Apply the three rules to a fragment known to be code (no comments)."""
    # protect literals
    keep = []
    def stash(m):
        keep.append(m.group(0))
        return f'\x00{len(keep)-1}\x00'
    s = STR.sub(stash, s)
    s = CHR.sub(stash, s)

    # rule 1: call / parameter list
    s = re.sub(r'([A-Za-z_][A-Za-z_0-9]*)\s+\(',
               lambda m: m.group(0) if m.group(1) in NO_ATTACH_PAREN else m.group(1) + '(', s)
    # rule 2: template instantiation, e.g.  to!{u32} ()  ->  to!{u32}()
    s = re.sub(r'\}\s+\(', '}(', s)
    # rule 3: indexing
    s = re.sub(r'([A-Za-z_][A-Za-z_0-9]*)\s+\[',
               lambda m: m.group(0) if m.group(1) in NO_ATTACH_BRACK else m.group(1) + '[', s)
    # rule 4: type annotation colon
    s = re.sub(r'(\S)[ \t]+:[ \t]', r'\1: ', s)

    for i, lit in enumerate(keep):
        s = s.replace(f'\x00{i}\x00', lit)
    return s


def transform_line(ln, in_block):
    """Transform one listing line, honouring // and /* */ comments.

    Returns (new_line, in_block_after).
    """
    out, i, n = [], 0, len(ln)
    code_start = 0
    while i < n:
        if in_block:
            j = ln.find('*/', i)
            if j < 0:
                out.append(ln[code_start:]); return ''.join(out), True
            out.append(ln[i:j+2]); i = j + 2; code_start = i; in_block = False
            continue
        # scan forward through code looking for a comment opener, skipping literals
        m = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|//|/\*').search(ln, i)
        if not m:
            out.append(transform_code(ln[code_start:])); return ''.join(out), False
        if m.group(0) == '//':
            out.append(transform_code(ln[code_start:m.start()]))
            out.append(ln[m.start():]); return ''.join(out), False
        if m.group(0) == '/*':
            out.append(transform_code(ln[code_start:m.start()]))
            i = m.start(); code_start = i; in_block = True
            out.append('/*'); i += 2; code_start = i
            continue
        i = m.end()          # a literal: skip over it, stay in code
    out.append(transform_code(ln[code_start:]))
    return ''.join(out), in_block


TOKEN = re.compile(r'\\token\{((?:[^{}]|\{[^{}]*\})*)\}')

def process(path, apply):
    src = path.read_text()
    lines = src.split('\n')
    out, inl, style, in_block, hits = [], False, None, False, 0
    for ln in lines:
        s = ln.strip()
        if s.startswith('\\begin{lstlisting}'):
            inl = True; in_block = False
            m = re.search(r'style=(\w+)', s); style = m.group(1) if m else '?'
            # a `%% restyle: skip` marker on a preceding line opts the listing out
            back = [x.strip() for x in out[-3:] if x.strip()]
            if any(x.startswith('%% restyle: skip') for x in back): style = 'SKIP'
            out.append(ln); continue
        if s.startswith('\\end{lstlisting}'):
            inl = False; out.append(ln); continue
        if inl and style and style.startswith('colored'):
            new, in_block = transform_line(ln, in_block)
        elif not inl:
            # prose: inline \token{...} only
            new = TOKEN.sub(lambda m: '\\token{' + transform_code(m.group(1)) + '}', ln)
        else:
            new = ln
        if new != ln: hits += 1
        out.append(new)
    res = '\n'.join(out)
    if apply and res != src: path.write_text(res)
    return hits, src, res


def main():
    apply = '--apply' in sys.argv
    total, files = 0, 0
    diffs = []
    for p in sorted(pathlib.Path('chapters').rglob('*.tex')):
        hits, before, after = process(p, apply)
        if hits:
            total += hits; files += 1
            if not apply:
                import difflib
                d = list(difflib.unified_diff(before.split('\n'), after.split('\n'),
                                              str(p), str(p), n=0, lineterm=''))
                diffs.append('\n'.join(d))
    if not apply:
        print('\n'.join(diffs))
    print(f'\n{"APPLIED" if apply else "DRY RUN"}: {total} lines changed in {files} files')

main()
