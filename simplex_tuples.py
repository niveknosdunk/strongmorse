import itertools
import sys

def generate_files(n):
    # --- Step 1: Build ordered list of pairs (i,j), i != j, 0 <= i,j <= n ---
    # Lex order: (0,1),(0,2),...,(0,n),(1,0),(1,2),...,(n,n-1)
    pairs = []
    for i in range(n + 1):
        for j in range(n + 1):
            if i != j:
                pairs.append((i, j))
    # pairs is already in lex order due to nested loop structure
    pair_to_index = {p: idx for idx, p in enumerate(pairs)}
    # Verify count: n(n+1) pairs
    assert len(pairs) == n * (n + 1), f"Expected {n*(n+1)} pairs, got {len(pairs)}"

    # --- Step 2: Generate all permutations of 0..n in lex order ---
    all_perms = list(itertools.permutations(range(n + 1)))
    # itertools.permutations returns in lex order when input is sorted

    simplex_tuples = []   # all n-tuples
    sphere_tuples  = []   # all (n-1)-tuples  (skip last step)

    for perm in all_perms:
        # perm[vertex] = label assigned to that vertex
        # Build inverse: label -> vertex
        label_to_vertex = [0] * (n + 1)
        for vertex, label in enumerate(perm):
            label_to_vertex[label] = vertex

        # At step m (1-indexed, m goes from 1 to n):
        #   The vertex with label m is v_m = label_to_vertex[m]
        #   We generate m pairs: (v_m, label_to_vertex[k]) for k = 0, 1, ..., m-1
        #   Each such pair maps to a pair index.
        #
        # The full n-tuple is formed by choosing ONE pair-index from each step m=1..n.
        # That is the Cartesian product of the choices at each step.

        # Collect choices at each step
        step_choices = []  # step_choices[m-1] = list of pair indices for step m

        for m in range(1, n + 1):
            v_high = label_to_vertex[m]
            choices_this_step = []
            for k in range(m):          # k = 0, 1, ..., m-1
                v_low = label_to_vertex[k]
                pair_idx = pair_to_index[(v_high, v_low)]
                choices_this_step.append(pair_idx)
            step_choices.append(choices_this_step)

        # Cartesian product over steps 1..n  →  n-tuples (simplex)
        for combo in itertools.product(*step_choices):
            simplex_tuples.append(list(combo))

        # Cartesian product over steps 1..n-1  →  (n-1)-tuples (sphere)
        for combo in itertools.product(*step_choices[:-1]):
            sphere_tuples.append(list(combo))

    # --- Step 3: Sort each tuple's entries, then deduplicate ---
    def sort_and_dedup(tuple_list):
        sorted_tuples = [sorted(t) for t in tuple_list]
        # Deduplicate while preserving first-occurrence order
        seen = set()
        unique = []
        for t in sorted_tuples:
            key = tuple(t)
            if key not in seen:
                seen.add(key)
                unique.append(t)
        return unique

    unique_simplex = sort_and_dedup(simplex_tuples)
    unique_sphere  = sort_and_dedup(sphere_tuples)

    # --- Step 4: Write output files ---
    def tuples_to_str(tuple_list):
        return ",".join("[" + ",".join(str(x) for x in t) + "]" for t in tuple_list)

    simplex_filename = f"{n}-simplex.txt"
    sphere_filename  = f"{n-1}-sphere.txt"

    with open(simplex_filename, "w") as f:
        f.write(tuples_to_str(unique_simplex))

    with open(sphere_filename, "w") as f:
        f.write(tuples_to_str(unique_sphere))

    print(f"n = {n}")
    print(f"Pairs (vertices): {len(pairs)}")
    print(f"Permutations: {len(all_perms)}")
    print(f"Total n-tuples before dedup:     {len(simplex_tuples)}")
    print(f"Unique n-tuples (simplex):        {len(unique_simplex)}  → {simplex_filename}")
    print(f"Total (n-1)-tuples before dedup: {len(sphere_tuples)}")
    print(f"Unique (n-1)-tuples (sphere):     {len(unique_sphere)}   → {sphere_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python simplex_tuples.py <n>")
        sys.exit(1)
    n = int(sys.argv[1])
    if n < 1:
        print("n must be a positive integer")
        sys.exit(1)
    generate_files(n)