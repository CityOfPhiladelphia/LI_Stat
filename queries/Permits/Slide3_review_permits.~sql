SELECT trim(b.apno) PermitNumber,
  b.APDTTM ProcessingDate,
  nvl(nvl(aprec.stopdttm, aprec.startdttm), b.issdttm) PermitIssueDate,
  defn.aptype PermitType,
  b.worktype
FROM imsv7.apbldg b,
  imsv7.apact act,
  imsv7.aprec aprec,
  imsv7.apdefn defn
WHERE b.apdefnkey                    = defn.apdefnkey
AND TO_DATE(b.APDTTM, 'YYYY-MM-DD') != TO_DATE(b.ISSDTTM, 'YYYY-MM-DD')
AND b.APKEY                          = act.APKEY (+)
AND b.APKEY                          = aprec.APKEY (+)
AND b.APDTTM                        >= '01-JAN-2016'
AND b.parentkey                      = '1'
--and upper(a.comments) like '%ISSUE%'
and aprec.logtype like 'RPTPER%'

UNION
SELECT trim(u.apno) PermitNumber,
  u.APDTTM ProcessingDate,
  nvl(nvl(aprec.stopdttm, aprec.startdttm), u.issdttm) PermitIssueDate,
  defn.aptype PermitType,
  u.worktype
FROM imsv7.apuse u,
  imsv7.apact act,
  imsv7.aprec aprec,
  imsv7.apdefn defn
WHERE u.apdefnkey                    = defn.apdefnkey
AND TO_DATE(u.APDTTM, 'YYYY-MM-DD') != TO_DATE(u.ISSDTTM, 'YYYY-MM-DD')
AND u.APKEY                          = act.APKEY (+)
AND u.Apkey                          = aprec.apkey (+)
AND u.APDTTM                        >= '01-JAN-2016'
AND u.parentkey                      = '1'
