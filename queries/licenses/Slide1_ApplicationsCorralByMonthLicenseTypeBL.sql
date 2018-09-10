SELECT licensetype                   "LicenseType", 
       jobtype, 
       applicationmonth              "ApplicationMonth", 
       applicationyear               "ApplicationYear", 
       Count(DISTINCT licensenumber) "CountLicensesApplied" 
FROM   (SELECT DISTINCT lt.name                                  LicenseType, 
                        lic.licensenumber                        LicenseNumber, 
                        ( CASE 
                            WHEN lic.initialissuedate > '01-JAN-16' THEN 
                            'BL_Application' 
                          END )                                  JobType, 
                        Extract(month FROM lic.initialissuedate) 
                        ApplicationMonth, 
                        Extract(year FROM lic.initialissuedate)  ApplicationYear 
        FROM   lmscorral.bl_license lic, 
               lmscorral.bl_licensetype lt 
        WHERE  lic.licensetypeobjectid = lt.objectid 
               AND lic.initialissuedate > '01-JAN-16') 
GROUP  BY licensetype, 
          jobtype, 
          applicationmonth, 
          applicationyear 
ORDER  BY licensetype, 
          jobtype, 
          applicationyear, 
          applicationmonth 
--runtime 0:03 