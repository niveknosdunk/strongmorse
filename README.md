# strongmorse
scripts used in the paper "Complexes of strong Morse matchings"

There are six python3 files in this repository:

1. path_complex.py generates the maximal simplices of the strong Morse complex on the path P_n with n edges. This complex has dimension n-1 and is not pure for n at least 4, so these maximal simplices do not all have the same dimension. The output generates a combined file, a file of the facets, and a file of the maximal simplices of smaller dimension.
2. simplex_tuples.py generates the complexes to which the strong Morse complexes on the n-simplex and its boundary collapse.
3. cn_complex.py generates the maximal simplices of the strong Morse complex on the cycle C_n with n edges.
4. xm_complex.py generates the maximal simplices of the complex X(m) defined in the paper. We have X(2m) = SM(P_m).
5. ym_complex.py generates the maximal simplices of the complex Y(m) defined in the paper.
6. en_complex3.py generates the maximal simplices of the subcomplex E(n) in SM(C_n), where C_n is the cycle with n edges, consisting of simplices having only even numbered vertices.

Full disclosure: these scripts were written by Claude Sonnet 4.6.
