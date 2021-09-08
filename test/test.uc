{
    // Declarations
    int x;
    int[3] y;
    {int fst; int snd} z;
    int fst; // fst can still be used outside of the record scope

    // Statements
    x := (5);
    x := y[2];
    y[2] := 5;
    y[1] := x;
    z.fst := 2;
    z.snd := 5;
    z := (x, y[1]);
    x := x + y[2];

    if (x > 0)
    {
        x := 1;
        y := 2;
        // read y[2];
        // write 666;

        // while (x < 100)
        // {
        //     x := x + 1;
        //     if (x == 99) {

        //     } else {

        //     }
        // }
    }

    x := 3;

    if (x > 2)
    {
        x := 9;
        y := 9;
    }
    else
    {
        x := 8;
    }

    x := 1;

    // if (y[1] > 5) {
    //     y[1] := 6;
    // } else {
    //     y[1] := 4;
    //     y[2] := 2;
    // }

    while (!x > 0 & y[0] < 4 | y[1] < 4) {
        x := x - 1;
        y := y - 1;

        if (x == 1) {
            z.fst := 0;
        }

        z.fst := z.fst + 1;
    }

    // y[1] := y[2] * x + z.fst;
}