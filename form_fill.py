inputs = ['EM_PERM_WATER', 'EM_TEMP', 'EM_PUMP_INLET', 'EM_QA_PUMPINLET', 'EM_UF_RETURN',
          'EM_DENSITY_RETN', 'EM_WATER', 'VLV_UF_INLET', 'CTRL_UF_FLOW', 'MTR_UF_PUMP']
target = """IF
     (('^/FAIL_MONITOR/ACQ_REL/_{0}/ACQUIRE.CV' != "") AND
     (COUNT < MAX_COUNT))
THEN
    IF
        (COUNT > 0)
    THEN
        '^/P_MSG2.CV' := '^/P_MSG2.CV' + ", ";
    ENDIF;
    '^/P_MSG2.CV' := '^/P_MSG2.CV' + '//#THISUNIT#/{0}';
    COUNT := COUNT + 1;
ENDIF;"""

for a in inputs:
    print(target.format(a))
