{
    // Declarations
    int x;
    int[3] y;
    {int fst; int snd} z;
    int fst; // fst can still be used outside of the record scope

    // Statements
    x := 5;
    x := y[2];
    y[2] := 5;
    y[1] := x;
    z.fst := 2;
    z.snd := 5;
    z := (x, y[1]);
    x := x + y[2];

    if (x > 0)
    {
        read y[2];
        write 666;

        while (x < 100)
        {
            x := x + 1;
            if (x == 99) {

            } else {

            }
        }
    }
}