subdir = 'inputs'
inputs = subdir + '\\' + 'PH_423_COMPLETE.fhx'
alias_file = subdir + '\\' + '419_aliases.txt'
input_file = open(inputs, mode='r', encoding='utf-16')
out = input_file.read()
with open(alias_file, encoding='utf-16') as file:
    for a in file:
        a = a.split('\t')
        count = out.count(a[5])
        if a[6] != 'T\n' and count > 0:
            out = out.replace(a[5], '#' + a[0] + '#')
            count += 1
            print("{} replaced with {} {} times".format(a[5], a[0], count))

with open('outputs\\alias_subs.fhx', mode='w') as output_file:
    output_file.write(out)
