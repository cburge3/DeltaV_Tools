subdir = 'inputs'
inputs = subdir + '\\' + 'PH_423_ADD_MONOMER.fhx'
alias_file = subdir + '\\' + 'UPs.txt'
input_file = open(inputs, mode='r', encoding='utf-16')
out = input_file.read()
with open(alias_file, encoding='utf-8') as file:
    for a in file:
        a = a.split('\t')
        if a[0][0] != "#":
            print("{} instances of {} were found and replaced".format(out.count(a[0]), a[0]))
            out = out.replace('//#THISUNIT#/' + a[0] + '_VALUE.CV', '^/' + a[1].strip() + '.CV')
            out = out.replace('//#THISUNIT#/' + a[0] + '_VALUE', '^/' + a[1].strip() + '.CV')
            out = out.replace(a[0], a[1].strip())

with open('outputs\\UP_subs.fhx', mode='w') as output_file:
    output_file.write(out)
