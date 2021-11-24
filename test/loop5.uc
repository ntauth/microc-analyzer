{
    int i;
    int j;
    int k;
    int m;
    int n;
    int r;
    int u;
    m:=10;
    r:=5;
    i := 0;
    if (m > 2)
    {
        n := 15;
    }
    else
    {
        n := 20;
    }
    while (i < n)
    {
        j := 0;
        while (j < m)
        {
            k := 0;
            while (k < r)
            {
                u := i+j+k;
                k := k+1;
            }
            j := j+1;
        }
        i := i+1;
    }
}