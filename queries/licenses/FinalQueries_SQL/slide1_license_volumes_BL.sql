SELECT
     jobtype,
     licensetype,
     issuedate,
     COUNT(DISTINCT licensenumber) countjobs
 FROM
     (
         SELECT
             licensetype,
             licensenumber,
             jobtype,
             TO_DATE(jobissueyear
                       || '/'
                       || jobissuemonth
                       || '/'
                       || '01','yyyy/mm/dd') AS issuedate
         FROM
             (
                 ( SELECT DISTINCT
                     lt.name               licensetype,
                     lic.externalfilenum   licensenumber,
                     ( CASE
                         WHEN ap.applicationtype LIKE 'Application' THEN 'BL_Application'
                     END ) jobtype,
                     EXTRACT(YEAR FROM ap.issuedate) jobissueyear,
                     EXTRACT(MONTH FROM ap.issuedate) jobissuemonth
                 FROM
                     query.j_bl_application ap,
                     query.r_bl_application_license rla,
                     query.o_bl_license lic,
                     lmscorral.bl_licensetype lt
                 WHERE
                     lic.licensetypeid = lt.objectid
                     AND lic.objectid = rla.licenseobjectid
                     AND rla.applicationobjectid = ap.jobid
                     AND ap.statusdescription LIKE 'Approved'
                     AND ap.issuedate > '01-JAN-16'
                     AND ap.issuedate <= SYSDATE
                 )
                 UNION
                 SELECT DISTINCT
                     lt.name               licensetype,
                     lic.externalfilenum   licensenumber,
                     ( CASE
                         WHEN ar.applicationtype LIKE 'Renewal' THEN 'BL_Renewal'
                     END ) jobtype,
                     EXTRACT(YEAR FROM ar.issuedate) jobissueyear,
                     EXTRACT(MONTH FROM ar.issuedate) jobissuemonth
                 FROM
                     query.j_bl_amendrenew ar,
                     query.r_bl_amendrenew_license rla,
                     query.o_bl_license lic,
                     lmscorral.bl_licensetype lt
                 WHERE
                     lic.licensetypeid = lt.objectid
                     AND lic.objectid = rla.licenseid
                     AND rla.amendrenewid = ar.jobid
                     AND ar.statusdescription LIKE 'Approved'
                     AND ar.applicationtype LIKE 'Renewal'
                     AND ar.issuedate > '01-JAN-16'
                     AND ar.issuedate <= SYSDATE
             )
     )
 GROUP BY
     issuedate,
     jobtype,
     licensetype
 ORDER BY
     issuedate,
     jobtype,
     licensetype