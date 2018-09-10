--Query no. of monthly on-line, L&I Concourse, and mail transactions per license type.
--For trades: March 2017 -present 
--runtime _____ seconds
SET DEFINE OFF

SELECT DISTINCT
    tlic.externalfilenum licensenumber,
    tlic.licensetype,
    
    (
        CASE
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
        END
    ) AS createdbytype,
    (
        CASE
            WHEN tar.applicationtype LIKE 'Application' THEN 'Application'
        END
    ) jobtype,
    tlic.lastissuedate mostrecentissuedate,
    (
        CASE
            WHEN tar.applicationtype LIKE 'Application' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=2855291&objectHandle='
                                                             || tlic.objectid
                                                             || '&processHandle='
        END
    ) joblink
FROM
    query.o_tl_license tlic,
    query.r_tl_amendrenew_license lra,
    query.j_tl_amendrenew tar
WHERE
    tlic.objectid = lra.licenseid
    AND lra.amendrenewid = tar.objectid
    AND tlic.initialissuedate >= '01-MAR-17'
    AND tlic.initialissuedate <= SYSDATE
    AND tar.applicationtype LIKE 'Application'
UNION
SELECT DISTINCT
    tlic.externalfilenum licensenumber,
    tlic.licensetype,
    
    (
        CASE
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
        END
    ) AS createdbytype,
    (
        CASE
            WHEN tar.applicationtype LIKE 'Renewal' THEN 'Renewal'
        END
    ) jobtype,
    tlic.lastissuedate mostrecentissuedate,
    (
        CASE
            WHEN tar.applicationtype LIKE 'Renewal' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=2855291&objectHandle='
                                                             || tlic.objectid
                                                             || '&processHandle='
        END
    ) joblink
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
    AND tar.applicationtype LIKE 'Renewal';

SET DEFINE ON