--Query no. of monthly on-line, L&I Concourse, and mail transactions per license type.
--For business: April 2016- present
--runtime 562.093 seconds
SELECT DISTINCT licensenumber, createddate, LicenseIssueDate, createdbytype, jobtype, jobnumber, createdby, licensetype--, licenselink
FROM((SELECT DISTINCT 
       (CASE WHEN ap.createdby LIKE '%2%' THEN 'Online'
             WHEN ap.createdby LIKE '%3%' THEN 'Online'
             WHEN ap.createdby LIKE '%4%' THEN 'Online'
             WHEN ap.createdby LIKE '%5%' THEN 'Online'
             WHEN ap.createdby LIKE '%6%' THEN 'Online'
             WHEN ap.createdby LIKE '%7%' THEN 'Online'
             WHEN ap.createdby LIKE '%7%' THEN 'Online'
             WHEN ap.createdby LIKE '%9%' THEN 'Online'
             WHEN ap.createdby = 'PPG User'                THEN 'Online'
             WHEN ap.createdby = 'POSSE system power user' THEN 'Revenue'
             ELSE 'Staff' END) AS createdbytype,
        (CASE WHEN ap.applicationtype LIKE 'Application' THEN 'Application'END) jobtype, 
        lt.name licensetype, lic.licensenumber licensenumber, ap.ExternalFileNum jobnumber, ap.createdby createdby,
        extract(month from ap.CreatedDate) || '/'||extract(day from ap.CreatedDate)|| '/'|| extract(year from ap.CreatedDate) createddate, ap.CreatedDate JobCreatedDateField,
        extract(month from ap.CompletedDate) || '/'||extract(day from ap.CompletedDate)|| '/'|| extract(year from ap.CompletedDate) JobCompletedDate,
        extract(month from lic.MostRecentIssueDate) || '/'||extract(day from lic.MostRecentIssueDate)|| '/'|| extract(year from lic.MostRecentIssueDate) LicenseIssueDate,
        (CASE WHEN ap.applicationtype LIKE 'Application' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1244067&objectHandle='
                                                                    || lic.objectid
                                                                    || '&processHandle=&paneId=1244067_3' END AS licenselink
      FROM lmscorral.bl_license lic, lmscorral.bl_licensetype lt, query.j_bl_application ap, query.r_bl_application_license apl, query.o_jobtypes jt
      WHERE lt.objectid = lic.licensetypeobjectid (+)
        AND lic.objectid = apl.licenseobjectid (+)
        AND apl.applicationobjectid = ap.objectid (+)
        AND ap.JobTypeId = jt.JobTypeId (+)
        AND ap.StatusId like '1036493'
        AND lic.initialissuedate > '01-APR-16'
        AND lic.initialissuedate < SYSDATE
        AND ap.applicationtype = 'Application')
UNION
(SELECT DISTINCT  
  (CASE WHEN ar.CreatedBy like '%2%' THEN 'Online' 
        WHEN ar.CreatedBy like '%3%' THEN 'Online' 
        WHEN ar.CreatedBy like '%4%' THEN 'Online'
        WHEN ar.CreatedBy like '%5%' THEN 'Online' 
        WHEN ar.CreatedBy like '%6%' THEN 'Online' 
        WHEN ar.CreatedBy like '%7%' THEN 'Online' 
        WHEN ar.CreatedBy like '%7%' THEN 'Online'
        WHEN ar.CreatedBy like '%9%' THEN 'Online' 
        WHEN ar.CreatedBy = 'PPG User' THEN 'Online' 
        WHEN ar.CreatedBy = 'POSSE system power user' THEN 'Revenue' 
        ELSE 'Staff' END) AS createdbytype, 
    (CASE WHEN ar.applicationtype LIKE 'Renewal' THEN 'Renewal' END) jobtype,
    lt.Name licensetype, lic.LicenseNumber licensenumber, ar.ExternalFileNum jobnumber, ar.CreatedBy createdby, 
    extract(month from ar.CreatedDate) || '/'||extract(day from ar.CreatedDate)|| '/'|| extract(year from ar.CreatedDate) createddate, ar.CreatedDate JobCreatedDateField,
    extract(month from ar.CompletedDate) || '/'||extract(day from ar.CompletedDate)|| '/'|| extract(year from ar.CompletedDate) JobCompletedDate, 
    extract(month from lic.MostRecentIssueDate) || '/'||extract(day from lic.MostRecentIssueDate)|| '/'|| extract(year from lic.MostRecentIssueDate) LicenseIssueDate, 
   (
                CASE
                    WHEN ar.applicationtype LIKE 'Renewal' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1244067&objectHandle='
                                                                || lic.objectid
                                                                || '&processHandle=&paneId=1244067_3'
                END
            ) AS licenselink
      FROM lmscorral.bl_licensetype lt, lmscorral.bl_license lic, query.r_bl_amendrenew_license arl, query.j_bl_amendrenew ar, query.o_jobtypes jt
      WHERE lt.ObjectId = lic.LicenseTypeObjectId (+)
        AND lic.ObjectId = arl.LicenseId (+)
        AND arl.AmendRenewId = ar.ObjectId (+)
        AND ar.JobTypeId = jt.JobTypeId (+)
        AND ar.StatusId like '1036493'
        AND ar.issuedate > '01-APR-16'
        AND ar.issuedate < SYSDATE
        AND ar.applicationtype LIKE 'Renewal'))
ORDER BY
    LicenseIssueDate,
    createdbytype,
    jobtype,
    licensetype,
    licensenumber;
