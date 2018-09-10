SELECT licensetype                   "LicenseType", 
       RenewalYear                   "RenewalYear", 
       RenewalMonth                  "RenewalMonth", 
       Count(DISTINCT licensenumber) "CountLicensesRenewed" 
FROM   (SELECT DISTINCT tlic.licensetype, 
                        tlic.licensenumber                LicenseNumber, 
                        Extract(year FROM tar.issuedate)  RenewalYear,
                        Extract(month FROM tar.issuedate) RenewalMonth 
        FROM   query.o_tl_license tlic, 
               query.r_tl_amendrenew_license rta, 
               query.j_tl_amendrenew tar 
        WHERE  tlic.objectid = rta.licenseid 
               AND rta.amendrenewid = tar.objectid 
               AND tar.issuedate > '01-JAN-16') 
GROUP  BY licensetype, 
          renewalyear,
          renewalmonth
ORDER  BY licensetype, 
          renewalyear, 
          renewalmonth