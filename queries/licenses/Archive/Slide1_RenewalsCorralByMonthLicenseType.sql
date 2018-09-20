Select LicenseType "LicenseType", RenewalMonth "RenewalMonth", RenewalYear "RenewalYear", 
count(distinct LicenseNumber) "CountLicensesRenewed"
from (select DISTINCT  lt.name LicenseType, lic.LicenseNumber LicenseNumber, 
extract(MONTH from ar.IssueDate) RenewalMonth, extract(YEAR from ar.IssueDate) RenewalYear
from lmscorral.bl_amendmentrenewal ar, query.r_bl_amendrenew_license rla, lmscorral.bl_license lic, lmscorral.bl_licensetype lt
where lic.LicenseTypeObjectId = lt.ObjectId 
and lic.ObjectId = rla.LicenseId 
and rla.AmendRenewId = ar.JOBID
and lt.Name not like 'Activity'
and ar.StatusDescription like 'Approved' 
and ar.IssueDate >'01-JAN-16'
)
group by LicenseType, RenewalMonth, RenewalYear
order by LicenseType, RenewalYear, RenewalMonth
--runtime 2:34

