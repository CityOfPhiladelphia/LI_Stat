SELECT DISTINCT ( CASE 
                    WHEN ap.applicationtype LIKE 'Application' THEN 
                    'BL_Application' 
                  END )                            JobType,
                lt.name                            LicenseType, 
                lic.externalfilenum                LicenseNumber, 
                ap.issuedate                       IssueDate, 
                ( CASE 
                    WHEN Extract(month FROM ap.issuedate) LIKE '1' THEN 
                    'January' 
                    WHEN Extract(month FROM ap.issuedate) LIKE '2' THEN 
                    'February' 
                    WHEN Extract(month FROM ap.issuedate) LIKE '3' THEN 'March' 
                    WHEN Extract(month FROM ap.issuedate) LIKE '4' THEN 'April' 
                    WHEN Extract(month FROM ap.issuedate) LIKE '5' THEN 'May' 
                    WHEN Extract(month FROM ap.issuedate) LIKE '6' THEN 'June' 
                    WHEN Extract(month FROM ap.issuedate) LIKE '7' THEN 'July' 
                    WHEN Extract(month FROM ap.issuedate) LIKE '8' THEN 'August' 
                    WHEN Extract(month FROM ap.issuedate) LIKE '9' THEN 
                    'September' 
                    WHEN Extract(month FROM ap.issuedate) LIKE '10' THEN 
                    'October' 
                    WHEN Extract(month FROM ap.issuedate) LIKE '11' THEN 
                    'November' 
                    WHEN Extract(month FROM ap.issuedate) LIKE '12' THEN 
                    'December' 
                  END ) 
                || ' ' 
                || Extract(year FROM ap.issuedate) JobIssueMonthYear, 
                Extract(year FROM ap.issuedate)    JobIssueYear, 
                Extract(month FROM ap.issuedate)   JobIssueMonth,
                ( CASE
                WHEN ap.applicationtype LIKE 'Application' THEN
                'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1239699&objectHandle='
                ||rla.applicationobjectid
                ||'&processHandle='
                END )                              JobLink
FROM   query.j_bl_application ap, 
       query.r_bl_application_license rla, 
       query.o_bl_license lic, 
       lmscorral.bl_licensetype lt 
WHERE  lic.licensetypeid = lt.objectid 
       AND lic.objectid = rla.licenseobjectid 
       AND rla.applicationobjectid = ap.jobid 
       AND lt.name NOT LIKE 'Activity' 
       AND ap.statusdescription LIKE 'Approved' 
       AND ap.issuedate > '01-JAN-16' 
       AND ap.issuedate <= SYSDATE 
UNION 
SELECT DISTINCT ( CASE 
                    WHEN ar.applicationtype LIKE 'Renewal' THEN 'BL_Renewal' 
                  END )                            JobType,
                lt.name                            LicenseType, 
                lic.externalfilenum                LicenseNumber, 
                ar.issuedate                       IssueDate, 
                ( CASE 
                    WHEN Extract(month FROM ar.issuedate) LIKE '1' THEN 
                    'January' 
                    WHEN Extract(month FROM ar.issuedate) LIKE '2' THEN 
                    'February' 
                    WHEN Extract(month FROM ar.issuedate) LIKE '3' THEN 'March' 
                    WHEN Extract(month FROM ar.issuedate) LIKE '4' THEN 'April' 
                    WHEN Extract(month FROM ar.issuedate) LIKE '5' THEN 'May' 
                    WHEN Extract(month FROM ar.issuedate) LIKE '6' THEN 'June' 
                    WHEN Extract(month FROM ar.issuedate) LIKE '7' THEN 'July' 
                    WHEN Extract(month FROM ar.issuedate) LIKE '8' THEN 'August' 
                    WHEN Extract(month FROM ar.issuedate) LIKE '9' THEN 
                    'September' 
                    WHEN Extract(month FROM ar.issuedate) LIKE '10' THEN 
                    'October' 
                    WHEN Extract(month FROM ar.issuedate) LIKE '11' THEN 
                    'November' 
                    WHEN Extract(month FROM ar.issuedate) LIKE '12' THEN 
                    'December' 
                  END ) 
                || ' ' 
                || Extract(year FROM ar.issuedate) JobIssueMonthYear, 
                Extract(year FROM ar.issuedate)    JobIssueYear, 
                Extract(month FROM ar.issuedate)   JobIssueMonth,
                ( CASE
                WHEN ar.applicationtype LIKE 'Renewal' THEN
                'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1243107&objectHandle='
                ||rla.amendrenewid
                ||'&processHandle='
                END )                              JobLink 
FROM   query.j_bl_amendrenew ar, 
       query.r_bl_amendrenew_license rla, 
       query.o_bl_license lic, 
       lmscorral.bl_licensetype lt 
WHERE  lic.licensetypeid = lt.objectid 
       AND lic.objectid = rla.licenseid 
       AND rla.amendrenewid = ar.jobid 
       AND lt.name NOT LIKE 'Activity' 
       AND ar.statusdescription LIKE 'Approved' 
       AND ar.applicationtype LIKE 'Renewal' 
       AND ar.issuedate > '01-JAN-16' 
       AND ar.issuedate <= SYSDATE
--runtime 7-8 min