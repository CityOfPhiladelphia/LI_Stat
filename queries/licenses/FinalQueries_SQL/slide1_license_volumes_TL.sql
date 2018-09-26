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
                     tlic.licensetype     licensetype,
                     tlic.licensenumber   licensenumber,
                     ( CASE
                         WHEN tlic.initialissuedate >= '01-JAN-16' THEN 'Application'
                     END ) jobtype,
                     EXTRACT(YEAR FROM tlic.initialissuedate) jobissueyear,
                     EXTRACT(MONTH FROM tlic.initialissuedate) jobissuemonth
                 FROM
                     query.o_tl_license tlic
                 WHERE
                     tlic.initialissuedate >= '01-JAN-16'
                     AND tlic.initialissuedate <= SYSDATE
                 UNION
                 SELECT DISTINCT
                     tlic.licensetype      licensetype,
                     tlic.licensenumber    licensenumber,
                     tar.applicationtype   jobtype,
                     EXTRACT(YEAR FROM tar.completeddate) jobissueyear,
                     EXTRACT(MONTH FROM tar.completeddate) jobissuemonth
                 FROM
                     query.o_tl_license tlic,
                     query.r_tl_amendrenew_license lra,
                     query.j_tl_amendrenew tar
                 WHERE
                     tlic.objectid = lra.licenseid
                     AND lra.amendrenewid = tar.objectid
                     AND tar.completeddate >= '01-JAN-16'
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