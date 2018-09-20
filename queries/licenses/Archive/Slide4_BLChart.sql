--Query no. of monthly on-line, L&I Concourse, and mail transactions per license type.
--For business: April 2016- present
--runtime 562.093 seconds
SELECT DISTINCT
    licensenumber,
    issuedate,
    createdbytype,
    jobtype,
    licensetype,
    licenselink
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
            lic.initialissuedate issuedate,
            lt.name licensetype,
            lic.licensenumber licensenumber,
            (
                CASE
                    WHEN ap.applicationtype LIKE 'Application' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1244067&objectHandle='
                                                                    || lic.objectid
                                                                    || '&processHandle=&paneId=1244067_3'
                END
            ) AS licenselink
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
            AND lic.initialissuedate < SYSDATE
            AND ap.applicationtype = 'Application'
        )
        UNION
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
                    WHEN ar.applicationtype LIKE 'Renewal' THEN 'Renewal'
                END
            ) jobtype,
            ar.issuedate issuedate,
            lt.name licensetype,
            lic.licensenumber licensenumber,
            (
                CASE
                    WHEN ar.applicationtype LIKE 'Renewal' THEN 'https://eclipseprod.phila.gov/phillylmsprod/int/lms/Default.aspx#presentationId=1244067&objectHandle='
                                                                || lic.objectid
                                                                || '&processHandle=&paneId=1244067_3'
                END
            ) AS licenselink
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
            AND ar.issuedate < SYSDATE
        )
    )
ORDER BY
    issuedate,
    createdbytype,
    jobtype,
    licensetype,
    licensenumber;