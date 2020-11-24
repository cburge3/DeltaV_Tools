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

if __name__ == "__main__":
    print(format_number(4, 37))