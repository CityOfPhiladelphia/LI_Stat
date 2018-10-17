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
WHERE b.apdefnkey                    = defn.apdefnkey
AND TO_DATE(b.APDTTM, 'YYYY-MM-DD') != TO_DATE(b.ISSDTTM, 'YYYY-MM-DD')
AND b.APKEY                          = act.APKEY (+)
AND b.APDTTM                        >= '01-JAN-2016'
AND b.parentkey                      = '1'
UNION
SELECT u.apno,
  u.APDTTM,
  u.issdttm PermitIssueDate,
  defn.aptype PermitType,
  u.worktype,
  act.ISSDTTM ReviewIssueDate,
  u.parentkey
FROM imsv7.apuse u,
  imsv7.apact act,
  imsv7.apdefn defn
WHERE u.apdefnkey                    = defn.apdefnkey
AND TO_DATE(u.APDTTM, 'YYYY-MM-DD') != TO_DATE(u.ISSDTTM, 'YYYY-MM-DD')
AND u.APKEY                          = act.APKEY (+)
AND u.APDTTM                        >= '01-JAN-2016'
AND u.parentkey                      = '1'