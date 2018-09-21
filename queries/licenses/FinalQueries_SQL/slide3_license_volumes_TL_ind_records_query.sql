SELECT DISTINCT ( CASE 
                   WHEN tlic.initialissuedate >= '01-JAN-16' THEN 'Application' 
                 END )                                      JobType, 
                tlic.licensetype                            LicenseType, 
                tlic.externalfilenum                        LicenseNumber,
                tlic.initialissuedate                       IssueDate,
                ( CASE 
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '1' THEN 'January'
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '2' THEN 'February'
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '3' THEN 'March'
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '4' THEN 'April'
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '5' THEN 'May' 
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '6' THEN 'June' 
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '7' THEN 'July' 
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '8' THEN 'August'
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '9' THEN 'September'
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '10' THEN 'October'
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '11' THEN 'November'
                    WHEN Extract(month FROM tlic.initialissuedate) LIKE '12' THEN 'December'
                  END ) 
                || ' ' 
                || Extract(year FROM tlic.initialissuedate) JobIssueMonthYear, 
                Extract(year FROM tlic.initialissuedate)    JOBISSUEYEAR, 
                Extract(month FROM tlic.initialissuedate)   JOBISSUEMONTH,
                ( CASE 
                WHEN tlic.initialissuedate >= '01-JAN-16' THEN 
                'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=2855291&objectHandle='
                ||tlic.objectid
                ||'&processHandle='  
                END )                                   JobLink
FROM   query.o_tl_license tlic 
WHERE  tlic.initialissuedate >= '01-JAN-16' 
       AND tlic.initialissuedate <= SYSDATE 
UNION 
SELECT DISTINCT tar.applicationtype                     JobType, 
                tlic.licensetype                        LicenseType, 
                tlic.externalfilenum                    LicenseNumber,
                tlic.initialissuedate                   IssueDate,
                ( CASE 
                    WHEN Extract(month FROM tar.completeddate) LIKE '1' THEN 'January' 
                    WHEN Extract(month FROM tar.completeddate) LIKE '2' THEN 'February' 
                    WHEN Extract(month FROM tar.completeddate) LIKE '3' THEN 'March' 
                    WHEN Extract(month FROM tar.completeddate) LIKE '4' THEN 'April' 
                    WHEN Extract(month FROM tar.completeddate) LIKE '5' THEN 'May' 
                    WHEN Extract(month FROM tar.completeddate) LIKE '6' THEN 'June' 
                    WHEN Extract(month FROM tar.completeddate) LIKE '7' THEN 'July' 
                    WHEN Extract(month FROM tar.completeddate) LIKE '8' THEN 'August' 
                    WHEN Extract(month FROM tar.completeddate) LIKE '9' THEN 'September'
                    WHEN Extract(month FROM tar.completeddate) LIKE '10' THEN 'October' 
                    WHEN Extract(month FROM tar.completeddate) LIKE '11' THEN 'November'
                    WHEN Extract(month FROM tar.completeddate) LIKE '12' THEN 'December'
                  END ) 
                || ' ' 
                || Extract(year FROM tar.completeddate) JobIssueMonthYear, 
                Extract(year FROM tar.completeddate)    JOBISSUEYEAR, 
                Extract(month FROM tar.completeddate)   JOBISSUEMONTH,
                ( CASE 
                WHEN tar.applicationtype LIKE 'Renewal' THEN 
                'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=2855291&objectHandle='
                ||tlic.objectid 
                ||'&processHandle=' 
                END )                                       JobLink  
FROM   query.o_tl_license tlic, 
       query.r_tl_amendrenew_license lra, 
       query.j_tl_amendrenew tar 
WHERE  tlic.objectid = lra.licenseid 
       AND lra.amendrenewid = tar.objectid 
       AND tar.completeddate >= '01-JAN-16' 
       AND tar.completeddate <= SYSDATE 
       AND tar.statusdescription LIKE 'Approved' 
       AND tar.applicationtype LIKE 'Renewal'
--runtime 69 sec   
