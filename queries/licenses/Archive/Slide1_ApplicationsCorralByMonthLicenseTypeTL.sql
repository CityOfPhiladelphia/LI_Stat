SELECT jobtype, 
       jobissuemonthyear, 
       jobissueyear, 
       jobissuemonth, 
       Count(DISTINCT licensenumber) COUNTJOBS 
FROM   (SELECT DISTINCT tlic.licensetype                            LicenseType, 
                        tlic.licensenumber 
                        LicenseNumber, 
                        ( CASE 
                            WHEN tlic.initialissuedate >= '01-JAN-16' THEN 
                            'TL_Application' 
                          END )                                     JobType, 
                        ( CASE 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '1' 
                          THEN 
                            'January' 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '2' 
                          THEN 
                            'February' 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '3' 
                          THEN 
                            'March' 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '4' 
                          THEN 
                            'April' 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '5' 
                          THEN 
                            'May' 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '6' 
                          THEN 
                            'June' 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '7' 
                          THEN 
                            'July' 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '8' 
                          THEN 
                            'August' 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '9' 
                          THEN 
                            'September' 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '10' 
                          THEN 'October' 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '11' 
                          THEN 'November' 
                            WHEN Extract(month FROM tlic.initialissuedate) LIKE 
                                 '12' 
                          THEN 'December' 
                          END ) 
                        || ', ' 
                        || Extract(year FROM tlic.initialissuedate) 
                        JobIssueMonthYear, 
                        Extract(year FROM tlic.initialissuedate)    JOBISSUEYEAR 
                        , 
                        Extract( 
        month FROM tlic.initialissuedate)   JOBISSUEMONTH 
        FROM   query.o_tl_license tlic 
        WHERE  tlic.initialissuedate >= '01-JAN-16' 
               AND tlic.initialissuedate <= SYSDATE 
        UNION 
        SELECT DISTINCT tlic.licensetype, 
                        tlic.licensenumber                      LicenseNumber, 
                        tar.applicationtype                     JobType, 
                        ( CASE 
                            WHEN Extract(month FROM tar.completeddate) LIKE '1' 
                          THEN 
                            'January' 
                            WHEN Extract(month FROM tar.completeddate) LIKE '2' 
                          THEN 
                            'February' 
                            WHEN Extract(month FROM tar.completeddate) LIKE '3' 
                          THEN 
                            'March' 
                            WHEN Extract(month FROM tar.completeddate) LIKE '4' 
                          THEN 
                            'April' 
                            WHEN Extract(month FROM tar.completeddate) LIKE '5' 
                          THEN 
                            'May' 
                            WHEN Extract(month FROM tar.completeddate) LIKE '6' 
                          THEN 
                            'June' 
                            WHEN Extract(month FROM tar.completeddate) LIKE '7' 
                          THEN 
                            'July' 
                            WHEN Extract(month FROM tar.completeddate) LIKE '8' 
                          THEN 
                            'August' 
                            WHEN Extract(month FROM tar.completeddate) LIKE '9' 
                          THEN 
                            'September' 
                            WHEN Extract(month FROM tar.completeddate) LIKE '10' 
                          THEN 
                            'October' 
                            WHEN Extract(month FROM tar.completeddate) LIKE '11' 
                          THEN 
                            'November' 
                            WHEN Extract(month FROM tar.completeddate) LIKE '12' 
                          THEN 
                            'December' 
                          END ) 
                        || ', ' 
                        || Extract(year FROM tar.completeddate) 
                        JobIssueMonthYear, 
                        Extract(year FROM tar.completeddate)    JOBISSUEYEAR, 
                        Extract(month FROM tar.completeddate)   JOBISSUEMONTH 
        FROM   query.o_tl_license tlic, 
               query.r_tl_amendrenew_license lra, 
               query.j_tl_amendrenew tar 
        WHERE  tlic.objectid = lra.licenseid 
               AND lra.amendrenewid = tar.objectid 
               AND tar.completeddate >= '01-JAN-16' 
               AND tar.completeddate <= SYSDATE 
               AND tar.statusdescription LIKE 'Approved' 
               AND tar.applicationtype LIKE 'Renewal') 
GROUP  BY jobissuemonthyear, 
          jobissueyear, 
          jobissuemonth, 
          jobtype 
ORDER  BY jobissueyear, 
          jobissuemonth 
--runtime 0:03 