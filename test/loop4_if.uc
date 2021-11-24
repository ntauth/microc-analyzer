{
    int i;
    int j;
    int m;
    int n;
    int u;
    i := 0;
    m:=5;

    if (m > 2)
    {
        n := 10;
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
            u := i+j;
            j := j+1;
        }
        i := i+1;
    }
}