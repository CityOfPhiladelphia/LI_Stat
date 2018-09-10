--Query no. of monthly on-line, L&I Concourse, and mail transactions per license type.
--For trades: March 2017 -present 
--runtime 147.227 seconds
SELECT
    applicationyear,
    applicationmonth,
    createdbytype,
    licensetype,
    COUNT(licensenumber) countlicensesapplied
FROM
    (
        SELECT DISTINCT
            tlic.licensetype,
            tlic.licensenumber,
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
            EXTRACT(YEAR FROM tlic.initialissuedate) applicationyear,
            EXTRACT(MONTH FROM tlic.initialissuedate) applicationmonth
        FROM
            query.o_tl_license tlic,
            query.r_tl_amendrenew_license lra,
            query.j_tl_amendrenew tar
        WHERE
            tlic.objectid = lra.licenseid
            AND lra.amendrenewid = tar.objectid
            AND tlic.initialissuedate >= '01-MAR-17'
            AND tlic.initialissuedate <= SYSDATE
        UNION
        SELECT DISTINCT
            tlic.licensetype,
            tlic.licensenumber licensenumber,
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
            EXTRACT(YEAR FROM tar.completeddate) jobissueyear,
            EXTRACT(MONTH FROM tar.completeddate) jobissuemonth
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
GROUP BY
    applicationyear,
    applicationmonth,
    createdbytype,
    licensetype
ORDER BY
    applicationyear,
    applicationmonth,
    createdbytype,
    licensetype;