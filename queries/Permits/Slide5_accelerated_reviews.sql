SELECT distinct b.apno,
  b.APDTTM PermitApplicationDate,
  b.issdttm PermitIssueDate,
  (CASE
      WHEN b.issdttm - b.APDTTM <= 10
      THEN 'Within SLA'
      WHEN b.issdttm - b.APDTTM > 10
      THEN 'Outside SLA'
   END) SLACompliance,
  defn.aptype PermitType,
  b.worktype,
  act.ISSDTTM ReviewIssueDate,
  f.feedesc,
  rec.hours
FROM imsv7.apbldg b,
  imsv7.apact act,
  imsv7.apdefn defn,
  imsv7.apfee f,
  imsv7.aprec rec
WHERE b.apdefnkey = defn.apdefnkey
AND b.APKEY       = act.APKEY (+)
AND b.apkey       = f.apkey (+)
AND b.apkey       = rec.apkey (+)
AND b.APDTTM     >= '01-JAN-2016'
AND f.stat        = 'P'
AND (f.feedesc LIKE '%ACCELERATED%' OR f.FEEDESC LIKE '%ACCELARATED%')