"""
cn_complex.py

Generates the simplicial complex C(m) on vertices {0, 1, ..., m-1}, defined
by the same forbidden-pair rules as X(m) but with indices taken modulo m
(i.e., on a cycle rather than a path).

A subset S is a simplex iff it contains no forbidden pair:
  C1+C2: no {i, (i+1) mod m} for any i      (cyclically adjacent vertices)
  C3:    no {j, (j+3) mod m} for odd j       (cyclic distance-3, odd vertex)

The complex C(2n) corresponds to the n-cycle: it has 2n vertices, one for each
directed edge of the cycle, with the same orientation convention as the path
complex in path_complex.py. C(m) is defined for all m >= 2.

Comparison with X(m): X(m) uses the same rules but on a path (no wrap-around).
C(m) adds the cyclic forbidden pairs {m-1, 0} (from C1+C2) and, for odd j,
{j, (j+3) mod m} whenever j+3 >= m.

Performance note: the facet enumeration uses Bron-Kerbosch and is fast up to
m ~ 30. For larger m (say m >= 36) the number of facets grows exponentially
and computation may be slow.

Usage:
    python3 cn_complex.py <m>

Output:
    cn_m<m>.txt            ? all non-empty simplices
    cn_m<m>_facets.txt     ? maximal simplices (facets)
    cn_m<m>_nonpure_max.txt ? maximal simplices of dimension < max dimension
"""

import sys
import os
import time


def build_forbidden(m):
    """
    Return adjacency list of forbidden neighbors for C(m).
    Forbidden: {i, (i+1)%m} for all i, and {j, (j+3)%m} for odd j.
    """
    forb = [set() for _ in range(m)]
    for i in range(m):
        j = (i + 1) % m
        forb[i].add(j)
        forb[j].add(i)
    for i in range(m):
        if i % 2 == 1:
            j = (i + 3) % m
            forb[i].add(j)
            forb[j].add(i)
    return forb


def write_all_simplices(m, forb, filepath):
    """Write all non-empty simplices of C(m). Returns count."""
    count = 0
    first = True
    with open(filepath, 'w') as f:
        def rec(start, current, forbidden_so_far):
            nonlocal count, first
            if current:
                if not first:
                    f.write(',')
                f.write(str(list(current)))
                first = False
                count += 1
            for v in range(start, m):
                if v not in forbidden_so_far:
                    current.append(v)
                    rec(v + 1, current, forbidden_so_far | forb[v])
                    current.pop()
        rec(0, [], set())
        f.write('\n')
    return count


def get_all_facets(m, forb):
    """All maximal independent sets via Bron-Kerbosch."""
    results = []
    def bk(R, P, X):
        if not P and not X:
            results.append(tuple(sorted(R)))
            return
        if not P:
            return
        for v in list(P):
            bk(R | {v},
               {u for u in P if u != v and u not in forb[v]},
               {u for u in X if u not in forb[v]})
            P = P - {v}
            X = X | {v}
    bk(set(), set(range(m)), set())
    return sorted(results)


def write_facets(facets, filepath):
    with open(filepath, 'w') as f:
        f.write(','.join(str(list(r)) for r in facets))
        f.write('\n')
    return len(facets)


def write_nonpure_max(facets, filepath):
    """Write maximal simplices of dimension < max dimension."""
    if not facets:
        with open(filepath, 'w') as f:
            f.write('\n')
        return 0
    max_dim = max(len(f) - 1 for f in facets)
    npm = [f for f in facets if len(f) - 1 < max_dim]
    with open(filepath, 'w') as f:
        f.write(','.join(str(list(r)) for r in npm))
        f.write('\n')
    return len(npm)


def main():
    if len(sys.argv) > 1:
        try:
            m = int(sys.argv[1])
        except ValueError:
            print(f"Error: argument must be an integer, got '{sys.argv[1]}'")
            sys.exit(1)
    else:
        m = 12
        print(f"No m supplied; using default m=12.")
        print("Usage: python3 cn_complex.py <m>\n")

    if m < 2:
        print("Error: m must be >= 2")
        sys.exit(1)

    if m >= 36:
        print(f"Warning: m={m} may be slow (facet count grows exponentially).")

    all_path = f"cn_m{m}.txt"
    fac_path = f"cn_m{m}_facets.txt"
    npm_path = f"cn_m{m}_nonpure_max.txt"

    print(f"Computing C({m})...")
    t0 = time.time()

    forb   = build_forbidden(m)
    facets = get_all_facets(m, forb)

    all_count = write_all_simplices(m, forb, all_path)
    fac_count = write_facets(facets, fac_path)
    npm_count = write_nonpure_max(facets, npm_path)

    elapsed = time.time() - t0

    def kb(p): return os.path.getsize(p) / 1024

    print(f"  All simplices:   {all_count:8,}  ->  '{all_path}'  ({kb(all_path):.1f} KB)")
    print(f"  Facets:          {fac_count:8,}  ->  '{fac_path}'  ({kb(fac_path):.1f} KB)")
    print(f"  Nonpure-max:     {npm_count:8,}  ->  '{npm_path}'  ({kb(npm_path):.1f} KB)")
    print(f"  Time: {elapsed:.3f}s")

    if m % 2 == 0:
        print(f"\n  Note: C({m}) corresponds to the {m//2}-cycle.")


if __name__ == "__main__":
    main()