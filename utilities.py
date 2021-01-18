def populatenamedset(named_set_root):
    d = dict()
    entries = named_set_root.findall('.//entry')
    for e in entries:
        d[int(e.attrib['value'])] = e.attrib['name']
    return d

def format_number(num_digits, number):
    str_digit = ''
    for d in range(0, num_digits):
        if number < 10**d:
            str_digit += '0'
    str_digit += str(number)
    return str_digit

def camel_case(input_string):
    out = []
    input_string = input_string.split(' ')
    for word in range(0, len(input_string)):
        if input_string[word] != "":
            temp = input_string[word][0].upper() + input_string[word][1:]
            out.append(temp)
    out = ' '.join(out)
    return out

if __name__ == "__main__":
    print(format_number(4, 37))