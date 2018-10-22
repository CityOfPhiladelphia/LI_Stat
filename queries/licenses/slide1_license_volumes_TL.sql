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
             SELECT DISTINCT
                tap.applicationtype   JobType, 
                tlic.licensetype                            LicenseType, 
                tlic.externalfilenum                        LicenseNumber,
                tlic.initialissuedate                       IssueDate,
                Extract(year FROM tlic.initialissuedate)    JOBISSUEYEAR, 
                Extract(month FROM tlic.initialissuedate)   JOBISSUEMONTH
        FROM query.o_tl_license tlic,
             query.j_tl_application tap,
             query.o_fn_fee fee,
             api.jobs job
        WHERE tlic.objectid = tap.tradelicenseobjectid (+)
             AND tap.jobid = job.jobid (+) 
             AND job.jobid = fee.referencedobjectid (+)
             AND tlic.initialissuedate >= '01-oct-18'
             AND tlic.initialissuedate <= SYSDATE
         UNION
         SELECT DISTINCT
                tar.applicationtype                     JobType, 
                tlic.licensetype                        LicenseType, 
                tlic.externalfilenum                    LicenseNumber,
                tlic.initialissuedate                   IssueDate,
             EXTRACT(YEAR FROM tar.completeddate) jobissueyear,
             EXTRACT(MONTH FROM tar.completeddate) jobissuemonth
        FROM   query.o_tl_license tlic, 
             query.r_tl_amendrenew_license lra, 
             query.j_tl_amendrenew tar 
        WHERE  tlic.objectid = lra.licenseid 
             AND lra.amendrenewid = tar.objectid 
             AND tar.completeddate >= '01-oct-18' 
             AND tar.completeddate <= SYSDATE 
             AND tar.statusdescription LIKE 'Approved' 
             AND tar.applicationtype LIKE 'Renewal'
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
--runtime 86 sec 
