{
    int i;
    int j;
    int m;
    int n;
    int t;
    int u;
    int[10] A;
    int[10] B;

    i := 0;
    while (i < n)
    {
        j := 0;
        while (j < m)
        {
            u := (i*m)+j;
            t := (j*n)+i;
            B[t] := A[u];
            j := j+1;
        }
        i := i+1;
    }
}

