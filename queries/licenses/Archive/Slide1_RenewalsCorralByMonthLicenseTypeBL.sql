SELECT licensetype                   "LicenseType", 
       jobtype, 
       applicationtype, 
       renewalmonth                  "RenewalMonth", 
       renewalyear                   "RenewalYear", 
       Count(DISTINCT licensenumber) "CountLicensesRenewed" 
FROM   (SELECT DISTINCT lt.name                          LicenseType, 
                        lic.licensenumber                LicenseNumber, 
                        ( CASE 
                            WHEN ar.issuedate > '01-JAN-16' THEN 'BL_Renewal' 
                          END )                          JobType, 
                        ar.applicationtype, 
                        Extract(month FROM ar.issuedate) RenewalMonth, 
                        Extract(year FROM ar.issuedate)  RenewalYear 
        FROM   lmscorral.bl_amendmentrenewal ar, 
               query.r_bl_amendrenew_license rla, 
               lmscorral.bl_license lic, 
               lmscorral.bl_licensetype lt 
        WHERE  lic.licensetypeobjectid = lt.objectid 
               AND lic.objectid = rla.licenseid 
               AND rla.amendrenewid = ar.jobid 
               AND lt.name NOT LIKE 'Activity' 
               AND ar.statusdescription LIKE 'Approved' 
               AND ar.applicationtype LIKE 'Renewal' 
               AND ar.issuedate > '01-JAN-16') 
GROUP  BY licensetype, 
          jobtype, 
          applicationtype, 
          renewalmonth, 
          renewalyear 
ORDER  BY licensetype, 
          jobtype, 
          applicationtype, 
          renewalyear, 
          renewalmonth 
--runtime 2:34 