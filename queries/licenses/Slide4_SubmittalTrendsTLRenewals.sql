--Query no. of monthly on-line, L&I Concourse, and mail transactions per license type.
--For trades: March 2017 -present 
--runtime 54.024 seconds
SELECT
    renewalyear,
    renewalmonth,
    createdbytype,
    licensetype,
    COUNT(DISTINCT licensenumber) countlicensesrenewed
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
            EXTRACT(YEAR FROM tlic.initialissuedate) renewalyear,
            EXTRACT(MONTH FROM tlic.initialissuedate) renewalmonth
        FROM
            query.o_tl_license tlic,
            query.r_tl_amendrenew_license lra,
            query.j_tl_amendrenew tar
        WHERE
            tlic.objectid = lra.licenseid
            AND lra.amendrenewid = tar.objectid
            AND tlic.initialissuedate >= '01-MAR-17'
            AND tlic.initialissuedate <= SYSDATE
            AND tar.statusdescription LIKE 'Approved'
            AND tar.applicationtype LIKE 'Renewal'
    )
GROUP BY
    renewalyear,
    renewalmonth,
    createdbytype,
    licensetype
ORDER BY
    renewalyear,
    renewalmonth,
    createdbytype,
    licensetype;