SELECT DISTINCT sub.SERVNO "Service Request No.",
  sub.address "Address",
  sub.sr_problemdesc "Problem Description",
  sub.sr_calldate "Call Date",
  sub.unit "Unit",
  (
  CASE
    WHEN sub.unit = 'Ops'
    THEN addr.ops_district
    WHEN sub.unit = 'Building'
    THEN addr.building_district
    WHEN sub.unit = 'CSU'
    THEN addr.ops_district
  END) "District",
  s.sla "SLA"
FROM
  (SELECT sr.SERVNO,
    sr.addresskey,
    sr.address,
    sr.sr_problemcode,
    sr.sr_problemdesc,
    sr.sr_calldate,
    sr.sr_inspectiondate,
    sr.sr_resolutiondate,
    (
    CASE
      WHEN sr.SR_PROBLEMCODE IN ('BRH', 'DCC', 'DCR', 'DRGMR', 'FC', 'FR', 'HM', 'IR', 'LB', 'LR', 'LVCIP', 'MC', 'MR', 'NH', 'NPU', 'SMR', 'VC', 'VH', 'VRS', 'ZB', 'ZR')
      THEN 'Ops'
      WHEN sr.SR_PROBLEMCODE IN ('BC', 'BLK', 'COMP', 'EC', 'LC', 'PC', 'SPC', 'SR311', 'X', 'ZC', 'ZM')
      THEN 'Building'
      WHEN sr.SR_PROBLEMCODE IN ('BD', 'BDH', 'BDO')
      THEN 'CSU'
      ELSE 'Other'
    END) unit
  FROM IMSV7.LI_ALLSERVICEREQUESTS@lidb_link sr
  ) sub,
  LNI_ADDR addr,
  sla_dictionary s
WHERE sub.sr_inspectiondate IS NULL
AND sub.sr_resolutiondate   IS NULL
AND sub.addresskey           = addr.addrkey
AND sub.unit                != 'Other'
AND sub.sr_calldate         >= '01-JAN-2016'
AND sub.sr_problemcode       = s.prob (+)
ORDER BY sub.sr_calldate
