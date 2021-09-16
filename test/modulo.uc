{
    int x;
    int y;
    int q;
    int r;

    if ((x>=0) & (y>0))
    {
        q:=0;
        r:=x;
        while (r>=y)
        {
            r:=r-y;
            q:=q+1;        
        }
        write r;
    }
}
