""" For creating some of the more repetitive format files"""

format_type = 0
num_digits = 3
max_interlocks = 60
m = list()
# parameter paths

m.append('RP{}_DESC.CV,')
# m.append('AT1/T_DESC{0}.CV,AT1/T_DELAY_ON{0}.CV,AT1/T_DELAY_OFF{0}.CV,AT1/T_EXP{0}.EXPRESSION,AT1/T_VAL{0}.CV,')
# m.append('DCC1$I_DESC_{0}.CV,DCC1$I_DELAY_ON{0}.CV,DCC1$I_DELAY_OFF{0}.CV,DCC1$I_EXP{0}.EXPRESSION,')
# m.append('INTERLOCK/CND{0}/DESC.CV,INTERLOCK/CND{0}/T_EXPRESSION.EXPRESSION,INTERLOCK/CND{0}/TIME_DURATION.CV,')
# m.append('CND{0}/DESC.CV,CND{0}/T_EXPRESSION.EXPRESSION,CND{0}/TIME_DURATION.CV,')
# m.append('DEV{0}_ID.CV,DEV{0}_TT.CV,')
# common header
r = 'module_name,area,node_name,description,'
# common string parameter start
n = 'is_a_string_parameter F,F,F,F,'
# string parameter flags
st = list()
st.append('T,')
# st.append('T,F,F,T,F,')  # for AT modules
# st.append('T,F,F,T,')  # for DCC modules
# st.append('T,T,F,')
# st.append('T,T,F,')
# st.append('T,T,')
for z in range(1, max_interlocks + 1):
    str_digit = ''
    for d in range(0, num_digits):
        if z < 10**d:
            str_digit += '0'
    str_digit += str(z)
    r += m[format_type].format(str_digit)
    n += st[format_type]

# truncate trailing commas
line1 = "header " + r[:-1]
line2 = r[:-1]
line3 = n[:-1]
print('\n'.join([line1, line2, line3]))
# checks
print(len(line2.split(',')), len(line3.split(',')))

