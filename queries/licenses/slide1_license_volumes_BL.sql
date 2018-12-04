SELECT
     jobtype,
     licensetype,
     issuedate,
     COUNT(DISTINCT jobnumber) countjobs
 FROM
     (
         SELECT
             licensetype,
             jobnumber,
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
                     ap.ExternalFileNum    jobnumber, 
                     ( CASE
                         WHEN ap.applicationtype LIKE 'Application' THEN 'BL_Application'
                     END ) jobtype,
                     EXTRACT(YEAR FROM ap.issuedate) jobissueyear,
                     EXTRACT(MONTH FROM ap.issuedate) jobissuemonth
                 FROM
                     query.j_bl_application ap,
                     query.r_bl_application_license apl,
                     query.o_bl_license lic,
                     lmscorral.bl_licensetype lt
                 WHERE
                     lic.licensetypeid = lt.objectid
                     AND lic.objectid = apl.licenseobjectid
                     AND apl.applicationobjectid = ap.jobid
                     AND ap.statusdescription LIKE 'Approved'
                     AND ap.issuedate >= '01-JAN-16'
                     and ap.IssueDate <= sysdate
                     AND ap.applicationtype = 'Application'
                     --and lt.Name not like 'Activity'
                 )
                 UNION
                 SELECT DISTINCT
                     lt.name               licensetype,
                     lic.externalfilenum   licensenumber,
                     ar.ExternalFileNum    jobnumber,
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
                      AND ar.issuedate >= '01-JAN-16'
                      --and ar.IssueDate < '01-DEC-18'
                      AND ar.issuedate <= SYSDATE
                      AND ar.applicationtype LIKE 'Renewal'
                      --and lt.Name not like 'Activity'
                  UNION
                  SELECT DISTINCT
                     lt.name               licensetype,
                     lic.externalfilenum   licensenumber,
                     ap.ExternalFileNum    jobnumber,
                     'Activity' jobtype,
                     EXTRACT(YEAR FROM ap.IssueDate) jobissueyear,
                     EXTRACT(MONTH FROM ap.IssueDate) jobissuemonth
                 FROM
                     query.o_bl_license lic,
                     lmscorral.bl_licensetype lt, 
                     query.j_bl_application ap
                 WHERE
                     lic.licensetypeid = lt.objectid
                     AND lic.InitialIssueDate >= '01-JAN-16'
                     and lic.InitialIssueDate <= sysdate
                     and lt.Name like 'Activity'
                     and ap.ActivityLicenseId = lic.ObjectId
                     AND ap.statusdescription LIKE 'Approved'
            ))
 GROUP BY
     issuedate,
     jobtype,
     licensetype
 ORDER BY
     issuedate,
     jobtype,
     licensetype
