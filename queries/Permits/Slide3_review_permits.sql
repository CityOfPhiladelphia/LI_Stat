SELECT b.apno,
  b.APDTTM,
  b.issdttm PermitIssueDate,
  defn.aptype PermitType,
  b.worktype,
  act.ISSDTTM ReviewIssueDate,
  b.parentkey
FROM imsv7.apbldg b,
  imsv7.apact act,
  imsv7.apdefn defn
WHERE b.apkey                        = act.apkey
AND b.apdefnkey                      = defn.apdefnkey
AND TO_DATE(b.APDTTM, 'YYYY-MM-DD') != TO_DATE(b.ISSDTTM, 'YYYY-MM-DD')
AND b.APDTTM                        >= '01-JAN-2016'
AND b.APKEY                          = act.APKEY (+)
AND b.parentkey = '1'