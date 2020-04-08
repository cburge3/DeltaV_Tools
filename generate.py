b = "'//U_423_A01/BV0{}_DESC.CV' := '^/DESC_BV{}.CV';"
c = "'//U_423_A01/BV0{}_VALUE.CV' := '^/VAL_BV{}.CV';"
d = "'//U_423_A01/UP0{}_DESC.CV' := '^/DESC_UP{}.CV';"
e = "'//U_423_A01/UP0{}_VALUE.CV' := '^/VAL_UP{}.CV';"

r = [b,c,d,e]

for z in r:
    for a in range(1,41):
        i = str(a)
        if a < 10:
            print(z.format("0" + i, i))
        else:
            print(z.format(i, i))