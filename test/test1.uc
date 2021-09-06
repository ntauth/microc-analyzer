{
    int i;
    {int fst; int snd} R;
    int[10] A;
    
    while (i < 10) {
        read A[i];
        i := i + 1;
    }

    i := 0;
    
    while (i < 10) {
        if (A[i] >= 0) {
            R.fst := R.fst + A[i];
        }
        else {
            i := i + 1;
            // break;
        }

        R.snd := R.snd + 1;
    }

    write R.fst / R.snd;
}
