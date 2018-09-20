--Query no. of monthly on-line, L&I Concourse, and mail transactions per license type.
--For business: April 2016- present
--runtime 494.446 seconds
SELECT
    applicationyear,
    applicationmonth,
    createdbytype,
    licensetype,
    COUNT(licensenumber) countlicensesapplied
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
            EXTRACT(MONTH FROM lic.initialissuedate) applicationmonth,
            EXTRACT(YEAR FROM lic.initialissuedate) applicationyear
        FROM
            lmscorral.bl_license lic,
            lmscorral.bl_licensetype lt,
            query.j_bl_application ap,
            query.r_bl_application_license apl
        WHERE
            lt.objectid = lic.licensetypeobjectid (+)
            AND lic.objectid = apl.licenseobjectid (+)
            AND apl.applicationobjectid = ap.objectid (+)
            AND lic.initialissuedate > '01-APR-16'
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