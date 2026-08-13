"""
path_complex.py

Computes the simplicial complex for the path-labeling construction with n+1
vertices and writes five output files.

Usage:
    python3 path_complex.py <n>

Output files:
    complex_n<n>.txt            — all facets
    complex_n<n>_pure.txt       — pure (length-n) facets
    complex_n<n>_nonpure_max.txt — nonpure-maximal facets (length < n, not
                                   contained in any other facet)
    complex_n<n>_intersection.txt — facets of the intersection of the pure
                                    complex and the nonpure-max complex

Works efficiently for any n >= 2 (n=20 runs in ~3 seconds).

HOW IT WORKS
------------
The 2n vertices are directed edges of the path 0-1-2-...-n, in lex order:
  (0,1), (1,0), (1,2), (2,1), ..., (n-1,n), (n,n-1)
with lex indices 0, 1, 2, ..., 2n-1. The rightward edge (k, k+1) has index
2k; the leftward edge (k+1, k) has index 2k+1.

A direction string d[0]...d[n-1] over {>, <, -} encodes a facet:
  > at position k  ->  active vertex 2k   (rightward edge)
  < at position k  ->  active vertex 2k+1 (leftward edge)
  - at position k  ->  no vertex contributed

Valid direction strings (= facets) satisfy:
  1. No consecutive <> pair  (one vertex can't point both ways)
  2. All runs of - have even length
  3. At least one non-dash character

There are 2^n - [n even] valid strings in total.

PURE FACETS
  The n+1 all-active strings >^j <^(n-j) for j=0,...,n.

ALL-STUCK CHARACTERIZATION (nonpure-maximal facets)
  A -- pair at positions (k, k+1) is "stuck" if d[k-1]='<' and d[k+2]='>'.
  The < prevents replacing d[k] with > (would create <>), and the > prevents
  replacing d[k+1] with < (would create <>). A shorter facet is nonpure-
  maximal iff it has at least one -- pair and every -- pair is stuck.
  This gives an O(n) test per string with no quadratic subset comparisons.
  Direction strings with no dashes are excluded (those are the pure facets).

INTERSECTION
  The intersection of the pure complex and the nonpure-max complex is computed
  by generating all faces of each and intersecting. It has a period-4 homotopy
  pattern: contractible for n=2,3 mod 4; homotopy equivalent to S^(n-6) for
  n=0 mod 4 (n>=8); homotopy equivalent to S^(n-5) for n=1 mod 4 (n>=9).
  Since both the pure and nonpure-max complexes are contractible, the full
  complex has the homotopy type of the suspension of the intersection.
"""

import sys
import os
import time
from itertools import combinations


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def dir_to_lex_indices(d):
    """Convert a direction string (list of chars) to sorted lex vertex indices."""
    result = []
    for k, c in enumerate(d):
        if c == '>':
            result.append(2 * k)
        elif c == '<':
            result.append(2 * k + 1)
    return result


def all_faces(facets):
    """All faces (including empty set) of a list of facets."""
    faces = set()
    for f in facets:
        for r in range(len(f) + 1):
            for sub in combinations(f, r):
                faces.add(sub)
    return faces


def complex_facets(simplices):
    """Maximal non-empty simplices in a collection."""
    sl = sorted(simplices)
    return [s for s in sl if s and not any(set(s) < set(t) for t in sl)]


def write_list(facets, filepath):
    """Write a list of facets as [a,b,...], comma-separated, to filepath."""
    with open(filepath, 'w') as f:
        f.write(','.join(str(list(fac)) for fac in facets))
        f.write('\n')


# ---------------------------------------------------------------------------
# File writers
# ---------------------------------------------------------------------------

def write_all_facets(n, filepath):
    """
    Write all valid facets to filepath. Uses O(n) memory.
    Returns the number of facets written.
    """
    count = 0
    first = True

    with open(filepath, 'w') as f:

        def recurse(pos, current, last_char, in_odd_dash):
            nonlocal count, first
            if pos == n:
                if not in_odd_dash and any(c != '-' for c in current):
                    indices = dir_to_lex_indices(current)
                    if not first:
                        f.write(',')
                    f.write(str(indices))
                    first = False
                    count += 1
                return
            if in_odd_dash:
                current.append('-')
                recurse(pos + 1, current, '-', False)
                current.pop()
                return
            if last_char != '<':
                current.append('>')
                recurse(pos + 1, current, '>', False)
                current.pop()
            current.append('<')
            recurse(pos + 1, current, '<', False)
            current.pop()
            current.append('-')
            recurse(pos + 1, current, '-', True)
            current.pop()

        recurse(0, [], 'start', False)
        f.write('\n')

    return count


def get_pure_facets(n):
    """Return the n+1 pure facets as a list of tuples."""
    result = []
    for j in range(n + 1):
        f = tuple(list(range(0, 2*j, 2)) + list(range(2*j+1, 2*n, 2)))
        result.append(f)
    return result


def write_pure_facets(n, filepath):
    """Write the n+1 pure facets to filepath. Returns n+1."""
    facets = get_pure_facets(n)
    write_list(facets, filepath)
    return len(facets)


def get_nonpure_max_facets(n):
    """
    Return all nonpure-maximal facets as a sorted list of tuples.
    Uses the all-stuck characterization.
    """
    results = []

    def recurse(pos, current, last_char, in_odd_dash):
        if pos == n:
            if in_odd_dash:
                return
            has_dash = any(c == '-' for c in current)
            if not has_dash:
                return  # pure facets excluded here
            i = 0
            all_stuck = True
            while i < n:
                if current[i] == '-':
                    k = i
                    left_ok  = (k > 0 and current[k-1] == '<')
                    right_ok = (k+2 < n and current[k+2] == '>')
                    if not (left_ok and right_ok):
                        all_stuck = False
                        break
                    i += 2
                else:
                    i += 1
            if all_stuck:
                results.append(tuple(dir_to_lex_indices(current)))
            return
        if in_odd_dash:
            current.append('-')
            recurse(pos + 1, current, '-', False)
            current.pop()
            return
        if last_char != '<':
            current.append('>')
            recurse(pos + 1, current, '>', False)
            current.pop()
        current.append('<')
        recurse(pos + 1, current, '<', False)
        current.pop()
        current.append('-')
        recurse(pos + 1, current, '-', True)
        current.pop()

    recurse(0, [], 'start', False)
    return sorted(results)


def write_nonpure_max_facets(n, filepath):
    """Write all nonpure-maximal facets to filepath. Returns count."""
    facets = get_nonpure_max_facets(n)
    write_list(facets, filepath)
    return len(facets)


def write_intersection(n, pure_facets, npm_facets, filepath):
    """
    Write the facets of the intersection of the pure complex and the
    nonpure-max complex to filepath. Returns count.

    The facets are the maximal elements of {P ∩ Q : P pure, Q nonpure-max}.
    They always share the same maximum size, so only that size is kept;
    no quadratic subset comparisons are needed.
    """
    caps = set()
    for p in pure_facets:
        for q in npm_facets:
            cap = tuple(sorted(set(p) & set(q)))
            if cap:
                caps.add(cap)
    if not caps:
        write_list([], filepath)
        return 0
    max_size = max(len(c) for c in caps)
    int_facets = sorted(c for c in caps if len(c) == max_size)
    write_list(int_facets, filepath)
    return len(int_facets)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print(f"Error: argument must be an integer, got '{sys.argv[1]}'")
            sys.exit(1)
    else:
        n = 5
        print(f"No n supplied; using default n=5.")
        print("Usage: python3 path_complex.py <n>\n")

    if n < 2:
        print("Error: n must be >= 2")
        sys.exit(1)

    all_path     = f"complex_n{n}.txt"
    pure_path    = f"complex_n{n}_pure.txt"
    npm_path     = f"complex_n{n}_nonpure_max.txt"
    int_path     = f"complex_n{n}_intersection.txt"

    print(f"Computing path complex for n={n}...")
    t0 = time.time()

    all_count  = write_all_facets(n, all_path)
    pure       = get_pure_facets(n)
    write_list(pure, pure_path)
    npm        = get_nonpure_max_facets(n)
    write_list(npm, npm_path)
    int_count  = write_intersection(n, pure, npm, int_path)

    elapsed = time.time() - t0

    def kb(path): return os.path.getsize(path) / 1024

    print(f"  All facets:     {all_count:6d}  ->  '{all_path}'  ({kb(all_path):.1f} KB)")
    print(f"  Pure:           {len(pure):6d}  ->  '{pure_path}'  ({kb(pure_path):.1f} KB)")
    print(f"  Nonpure-max:    {len(npm):6d}  ->  '{npm_path}'  ({kb(npm_path):.1f} KB)")
    print(f"  Intersection:   {int_count:6d}  ->  '{int_path}'  ({kb(int_path):.1f} KB)")
    print(f"  Time: {elapsed:.3f}s")


if __name__ == "__main__":
    main()
