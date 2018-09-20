SELECT jobtype, 
       licensetype, 
       jobissuemonthyear, 
       jobissueyear, 
       jobissuemonth, 
       Count(DISTINCT licensenumber) CountJobs 
FROM   ((SELECT DISTINCT lt.name                            LicenseType, 
                         lic.externalfilenum                LicenseNumber, 
                         ( CASE 
                             WHEN ap.applicationtype LIKE 'Application' THEN 'BL_Application' 
                           END )                            JobType, 
                         ( CASE 
                             WHEN Extract(month FROM ap.issuedate) LIKE '1' THEN 'January' 
                             WHEN Extract(month FROM ap.issuedate) LIKE '2' THEN 'February' 
                             WHEN Extract(month FROM ap.issuedate) LIKE '3' THEN 'March' 
                             WHEN Extract(month FROM ap.issuedate) LIKE '4' THEN 'April' 
                             WHEN Extract(month FROM ap.issuedate) LIKE '5' THEN 'May' 
                             WHEN Extract(month FROM ap.issuedate) LIKE '6' THEN 'June' 
                             WHEN Extract(month FROM ap.issuedate) LIKE '7' THEN 'July' 
                             WHEN Extract(month FROM ap.issuedate) LIKE '8' THEN 'August' 
                             WHEN Extract(month FROM ap.issuedate) LIKE '9' THEN 'September' 
                             WHEN Extract(month FROM ap.issuedate) LIKE '10' THEN 'October' 
                             WHEN Extract(month FROM ap.issuedate) LIKE '11' THEN 'November' 
                             WHEN Extract(month FROM ap.issuedate) LIKE '12' THEN 'December' 
                           END ) 
                         || ' ' 
                         || Extract(year FROM ap.issuedate) JobIssueMonthYear, 
                         Extract(year FROM ap.issuedate)    JobIssueYear, 
                         Extract(month FROM ap.issuedate)   JobIssueMonth 
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
                AND ap.issuedate <= SYSDATE) 
        UNION 
        SELECT DISTINCT lt.name                            LicenseType, 
                        lic.externalfilenum                LicenseNumber, 
                        ( CASE 
                            WHEN ar.applicationtype LIKE 'Renewal' THEN 'BL_Renewal' 
                          END )                            JobType, 
                        ( CASE 
                            WHEN Extract(month FROM ar.issuedate) LIKE '1' THEN 'January' 
                            WHEN Extract(month FROM ar.issuedate) LIKE '2' THEN 'February' 
                            WHEN Extract(month FROM ar.issuedate) LIKE '3' THEN 'March' 
                            WHEN Extract(month FROM ar.issuedate) LIKE '4' THEN 'April' 
                            WHEN Extract(month FROM ar.issuedate) LIKE '5' THEN 'May' 
                            WHEN Extract(month FROM ar.issuedate) LIKE '6' THEN 'June' 
                            WHEN Extract(month FROM ar.issuedate) LIKE '7' THEN 'July' 
                            WHEN Extract(month FROM ar.issuedate) LIKE '8' THEN 'August' 
                            WHEN Extract(month FROM ar.issuedate) LIKE '9' THEN 'September' 
                            WHEN Extract(month FROM ar.issuedate) LIKE '10' THEN 'October' 
                            WHEN Extract(month FROM ar.issuedate) LIKE '11' THEN 'November' 
                            WHEN Extract(month FROM ar.issuedate) LIKE '12' THEN 'December' 
                          END ) 
                        || ' ' 
                        || Extract(year FROM ar.issuedate) JobIssueMonthYear, 
                        Extract(year FROM ar.issuedate)    JobIssueYear, 
                        Extract(month FROM ar.issuedate)   JobIssueMonth 
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
               AND ar.issuedate <= SYSDATE) 
GROUP  BY jobissuemonthyear, 
          jobissueyear, 
          jobissuemonth, 
          jobtype, 
          licensetype 
ORDER  BY jobissueyear, 
          jobissuemonth, 
          jobtype, 
          licensetype 