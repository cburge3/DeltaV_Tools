""" For creating some of the more repetitive format files"""

format_type = 0
max_interlocks = 16
m = list()
m.append('AT1/T_DESC{0}.CV,AT1/T_DELAY_ON{0}.CV,AT1/T_DELAY_OFF{0}.CV,AT1/T_EXP{0}.EXPRESSION,AT1/T_VAL{0}.CV,')
m.append('DCC1$I_DESC_{0}.CV,DCC1$I_DELAY_ON{0}.CV,DCC1$I_DELAY_OFF{0}.CV,DCC1$I_EXP{0}.EXPRESSION,')
m.append('INTERLOCK/CND{0}/DESC.CV,INTERLOCK/CND{0}/T_EXPRESSION.EXPRESSION,INTERLOCK/CND{0}/TIME_DURATION.CV,')
# common header
r = 'module_name,area,node_name,description,'
# common string parameter start
n = 'is_a_string_parameter F,F,F,F,'
st = list()
st.append('T,F,F,T,F,')  # for AT modules
st.append('T,F,F,T,')  # for DCC modules
st.append('T,T,F,')
for z in range(1, max_interlocks + 1):
    r += m[format_type].format(str(z))
    n += st[format_type]

line1 = "header " + r[:-1]
line2 = r[:-1]
line3 = n[:-1]
print('\n'.join([line1, line2, line3]))
# checks
print(len(line2.split(',')), len(line3.split(',')))

