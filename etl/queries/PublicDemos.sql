SELECT demodate,
  COUNT(DISTINCT objectid) countdemos
FROM
  (SELECT objectid,
    TO_DATE(democompletionyear
    || '/'
    || democompletionmonth
    || '/'
    || '01','yyyy/mm/dd') AS demodate
  FROM
    (SELECT objectid,
      EXTRACT(YEAR FROM completed_date) democompletionyear,
      EXTRACT(MONTH FROM completed_date) democompletionmonth
    FROM GIS_LNI.LI_DEMOLITIONS
    WHERE CITY_DEMO = 'YES'
    AND completed_date IS NOT NULL
    )
  )
GROUP BY demodate
ORDER BY demodate