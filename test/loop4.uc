{
    int i;
    int j;
    int m;
    int n;
    int u;
    i := 0;
    n:=10;
    m:=5;
    while (i < n)
    {
        j := 0;
        while (j < m)
        {
            u := i+j;
            j := j+1;
        }
        i := i+1;
    }
}