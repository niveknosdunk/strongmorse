"""
ym_complex.py

Generates the "Option B" simplicial complex Y(m) on vertices {0, 1, ..., m-1}.

A subset S is a simplex iff it contains no forbidden pair:
  C1+C2: no {i, i+1} for any i       (adjacent vertices)
  C3':   no {i, i+3} for ANY i        (all vertices, not just odd ones)

Compare with xm_complex.py (Option A) where C3 only forbids {i, i+3} for odd i.
Y(m) is a subcomplex of X(m): every simplex of Y(m) is a simplex of X(m),
but not vice versa.

The forbidden graph is the path graph plus all edges {i, i+3},
making it vertex-transitive (the rule is the same at every vertex).

Usage:
    python3 ym_complex.py <m>

Output:
    ym_m<m>.txt            — all simplices (non-empty faces)
    ym_m<m>_facets.txt     — maximal simplices (facets)
    ym_m<m>_nonpure_max.txt — maximal simplices of dimension < max dimension
"""

import sys
import os
import time


def build_forbidden(m):
    """Forbidden neighbors for Y(m): {i,i+1} and {i,i+3} for all i."""
    forb = [set() for _ in range(m)]
    for i in range(m - 1):
        forb[i].add(i + 1)
        forb[i + 1].add(i)
    for i in range(m):
        if i + 3 < m:
            forb[i].add(i + 3)
            forb[i + 3].add(i)
    return forb


def write_all_simplices(m, forb, filepath):
    """Write all non-empty simplices of Y(m). Returns count."""
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
    """Return all maximal simplices via Bron-Kerbosch for maximal independent sets."""
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


def write_facets(m, forb, filepath):
    """Write all maximal simplices. Returns count."""
    facets = get_all_facets(m, forb)
    with open(filepath, 'w') as f:
        f.write(','.join(str(list(r)) for r in facets))
        f.write('\n')
    return len(facets)


def write_nonpure_max(m, forb, filepath):
    """Write maximal simplices of dimension < max dimension. Returns count."""
    facets = get_all_facets(m, forb)
    if not facets:
        with open(filepath, 'w') as f:
            f.write('\n')
        return 0
    max_dim = max(len(f) - 1 for f in facets)
    npm = sorted(f for f in facets if len(f) - 1 < max_dim)
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
        m = 8
        print(f"No n supplied; using default m=8.")
        print("Usage: python3 ym_complex.py <m>\n")

    if m < 2:
        print("Error: m must be >= 2")
        sys.exit(1)

    all_path = f"ym_m{m}.txt"
    fac_path = f"ym_m{m}_facets.txt"
    npm_path = f"ym_m{m}_nonpure_max.txt"

    print(f"Computing Y({m})...")
    t0 = time.time()

    forb = build_forbidden(m)

    all_count = write_all_simplices(m, forb, all_path)
    fac_count = write_facets(m, forb, fac_path)
    npm_count = write_nonpure_max(m, forb, npm_path)

    elapsed = time.time() - t0

    def kb(p): return os.path.getsize(p) / 1024

    print(f"  All simplices:   {all_count:8,}  ->  '{all_path}'  ({kb(all_path):.1f} KB)")
    print(f"  Facets:          {fac_count:8,}  ->  '{fac_path}'  ({kb(fac_path):.1f} KB)")
    print(f"  Nonpure-max:     {npm_count:8,}  ->  '{npm_path}'  ({kb(npm_path):.1f} KB)")
    print(f"  Time: {elapsed:.3f}s")


if __name__ == "__main__":
    main()
