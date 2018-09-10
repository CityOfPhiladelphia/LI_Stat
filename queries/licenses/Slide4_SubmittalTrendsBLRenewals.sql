--Query no. of monthly on-line, L&I Concourse, and mail transactions per license type.
--For business: April 2016- present
--runtime 628.072 seconds
SELECT
    renewalyear,
    renewalmonth,
    createdbytype,
    licensetype,
    COUNT(licensenumber) countlicensesrenewed
FROM
    (
        SELECT
            (
                CASE
                    WHEN ap.createdby LIKE '%2%' THEN 'Online'
                    WHEN ap.createdby LIKE '%3%' THEN 'Online'
                    WHEN ap.createdby LIKE '%4%' THEN 'Online'
                    WHEN ap.createdby LIKE '%5%' THEN 'Online'
                    WHEN ap.createdby LIKE '%6%' THEN 'Online'
                    WHEN ap.createdby LIKE '%7%' THEN 'Online'
                    WHEN ap.createdby LIKE '%7%' THEN 'Online'
                    WHEN ap.createdby LIKE '%9%' THEN 'Online'
                    WHEN ap.createdby = 'PPG User'                THEN 'Online'
                    WHEN ap.createdby = 'POSSE system power user' THEN 'Revenue'
                    ELSE 'Staff'
                END
            ) AS createdbytype,
            lt.name licensetype,
            lic.licensenumber licensenumber,
            EXTRACT(MONTH FROM ar.issuedate) renewalmonth,
            EXTRACT(YEAR FROM ar.issuedate) renewalyear
        FROM
            lmscorral.bl_amendmentrenewal ar,
            query.r_bl_amendrenew_license rla,
            lmscorral.bl_license lic,
            lmscorral.bl_licensetype lt,
            query.j_bl_application ap,
            query.r_bl_application_license apl
        WHERE
            lic.licensetypeobjectid = lt.objectid
            AND lic.objectid = apl.licenseobjectid
            AND apl.applicationobjectid = ap.objectid
            AND lic.objectid = rla.licenseid
            AND rla.amendrenewid = ar.jobid
            AND lt.name NOT LIKE 'Activity'
            AND ar.statusdescription LIKE 'Approved'
            AND ar.applicationtype LIKE 'Renewal'
            AND ar.issuedate > '01-APR-16'
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
    licensetype