--Query no. of monthly on-line, L&I Concourse, and mail transactions per license type.
--For business: April 2016- present
--runtime 562.093 seconds
SELECT DISTINCT
    licenseissuedate,
    createdbytype,
    jobtype,
    licensetype,
    COUNT(licensenumber) licensenumbercount
FROM
    (
        ( SELECT DISTINCT
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
            (
                CASE
                    WHEN ap.applicationtype LIKE 'Application' THEN 'Application'
                END
            ) jobtype,
            lt.name licensetype,
            lic.licensenumber licensenumber,
            EXTRACT(MONTH FROM lic.mostrecentissuedate)
            || '-'
            || '1'
            || '-'
            || EXTRACT(YEAR FROM lic.mostrecentissuedate) licenseissuedate
          FROM
            lmscorral.bl_license lic,
            lmscorral.bl_licensetype lt,
            query.j_bl_application ap,
            query.r_bl_application_license apl,
            query.o_jobtypes jt
          WHERE
            lt.objectid = lic.licensetypeobjectid (+)
            AND lic.objectid = apl.licenseobjectid (+)
            AND apl.applicationobjectid = ap.objectid (+)
            AND ap.jobtypeid = jt.jobtypeid (+)
            AND ap.statusid LIKE '1036493'
            AND lic.initialissuedate > '01-APR-16'
            AND lic.initialissuedate < SYSDATE
            AND ap.applicationtype = 'Application'
        )
        UNION
        ( SELECT DISTINCT
            (
                CASE
                    WHEN ar.createdby LIKE '%2%' THEN 'Online'
                    WHEN ar.createdby LIKE '%3%' THEN 'Online'
                    WHEN ar.createdby LIKE '%4%' THEN 'Online'
                    WHEN ar.createdby LIKE '%5%' THEN 'Online'
                    WHEN ar.createdby LIKE '%6%' THEN 'Online'
                    WHEN ar.createdby LIKE '%7%' THEN 'Online'
                    WHEN ar.createdby LIKE '%7%' THEN 'Online'
                    WHEN ar.createdby LIKE '%9%' THEN 'Online'
                    WHEN ar.createdby = 'PPG User'                THEN 'Online'
                    WHEN ar.createdby = 'POSSE system power user' THEN 'Revenue'
                    ELSE 'Staff'
                END
            ) AS createdbytype,
            (
                CASE
                    WHEN ar.applicationtype LIKE 'Renewal' THEN 'Renewal'
                END
            ) jobtype,
            lt.name licensetype,
            lic.licensenumber licensenumber,
            EXTRACT(MONTH FROM lic.mostrecentissuedate)
            || '-'
            || '1'
            || '-'
            || EXTRACT(YEAR FROM lic.mostrecentissuedate) licenseissuedate
          FROM
            lmscorral.bl_licensetype lt,
            lmscorral.bl_license lic,
            query.r_bl_amendrenew_license arl,
            query.j_bl_amendrenew ar,
            query.o_jobtypes jt
          WHERE
            lt.objectid = lic.licensetypeobjectid (+)
            AND lic.objectid = arl.licenseid (+)
            AND arl.amendrenewid = ar.objectid (+)
            AND ar.jobtypeid = jt.jobtypeid (+)
            AND ar.statusid LIKE '1036493'
            AND ar.issuedate > '01-APR-16'
            AND ar.issuedate < SYSDATE
            AND ar.applicationtype LIKE 'Renewal'
        )
    )
GROUP BY
    licenseissuedate,
    createdbytype,
    jobtype,
    licensetype
ORDER BY
    licenseissuedate,
    createdbytype,
    jobtype,
    licensetype