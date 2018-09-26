--Query no. of monthly on-line, L&I Concourse, and mail transactions per license type.
--For trades: March 2017 -present 
--runtime _____ seconds
SELECT
     licensetype,
     createdbytype,
     jobtype,
     issuedate,
     COUNT(licensenumber) licensenumbercount
 FROM
     (
         SELECT DISTINCT
             licensenumber,
             licensetype,
             createdbytype,
             jobtype,
             TO_DATE(issueyear
                       || '/'
                       || issuemonth
                       || '/'
                       || '01','yyyy/mm/dd') AS issuedate
         FROM
             (
                 SELECT DISTINCT
                     tlic.licensenumber,
                     tlic.licensetype,
                     ( CASE
                         WHEN tap.createdby LIKE '%2%' THEN 'Online'
                         WHEN tap.createdby LIKE '%3%' THEN 'Online'
                         WHEN tap.createdby LIKE '%4%' THEN 'Online'
                         WHEN tap.createdby LIKE '%5%' THEN 'Online'
                         WHEN tap.createdby LIKE '%6%' THEN 'Online'
                         WHEN tap.createdby LIKE '%7%' THEN 'Online'
                         WHEN tap.createdby LIKE '%7%' THEN 'Online'
                         WHEN tap.createdby LIKE '%9%' THEN 'Online'
                         WHEN tap.createdby = 'PPG User'                THEN 'Online'
                         WHEN tap.createdby = 'POSSE system power user' THEN 'Revenue'
                         ELSE 'Staff'
                     END ) AS createdbytype,
                     ( CASE
                         WHEN tap.applicationtype LIKE 'Application' THEN 'Application'
                     END ) jobtype,
                     EXTRACT(MONTH FROM tlic.initialissuedate) issuemonth,
                     EXTRACT(YEAR FROM tlic.initialissuedate) issueyear
                 FROM
                     query.o_tl_license tlic,
                     query.j_tl_application tap,
                     query.r_tradelicensetlapplication tlap
                 WHERE
                     tlic.objectid = tlap.relationshipid
                     AND tap.objectid = tlap.tlapplicationid
                     AND tlic.initialissuedate >= '01-MAR-17'
                     AND tlic.initialissuedate <= SYSDATE
                     AND tap.applicationtype LIKE 'Application'
                 UNION
                 SELECT DISTINCT
                     tlic.licensenumber,
                     tlic.licensetype,
                     ( CASE
                         WHEN tar.createdby LIKE '%2%' THEN 'Online'
                         WHEN tar.createdby LIKE '%3%' THEN 'Online'
                         WHEN tar.createdby LIKE '%4%' THEN 'Online'
                         WHEN tar.createdby LIKE '%5%' THEN 'Online'
                         WHEN tar.createdby LIKE '%6%' THEN 'Online'
                         WHEN tar.createdby LIKE '%7%' THEN 'Online'
                         WHEN tar.createdby LIKE '%7%' THEN 'Online'
                         WHEN tar.createdby LIKE '%9%' THEN 'Online'
                         WHEN tar.createdby = 'PPG User'                THEN 'Online'
                         WHEN tar.createdby = 'POSSE system power user' THEN 'Revenue'
                         ELSE 'Staff'
                     END ) AS createdbytype,
                     ( CASE
                         WHEN tar.applicationtype LIKE 'Renewal' THEN 'Renewal'
                     END ) jobtype,
                     EXTRACT(MONTH FROM tar.completeddate) issuemonth,
                     EXTRACT(YEAR FROM tar.completeddate) issueyear
                 FROM
                     query.o_tl_license tlic,
                     query.r_tl_amendrenew_license lra,
                     query.j_tl_amendrenew tar
                 WHERE
                     tlic.objectid = lra.licenseid
                     AND lra.amendrenewid = tar.objectid
                     AND tar.completeddate >= '01-MAR-17'
                     AND tar.completeddate <= SYSDATE
                     AND tar.statusdescription LIKE 'Approved'
                     AND tar.applicationtype LIKE 'Renewal'
             )
     )
 GROUP BY
     issuedate,
     createdbytype,
     jobtype,
     licensetype
 ORDER BY
     issuedate,
     createdbytype,
     jobtype,
     licensetype