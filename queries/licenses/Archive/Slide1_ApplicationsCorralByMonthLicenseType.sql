Select LicenseType "LicenseType", ApplicationMonth "ApplicationMonth", ApplicationYear "ApplicationYear", count(distinct LicenseNumber) "CountLicensesApplied"
from (select DISTINCT lt.name LicenseType, lic.LicenseNumber LicenseNumber,  
extract(MONTH from lic.InitialIssueDate) ApplicationMonth, extract(YEAR from lic.InitialIssueDate) ApplicationYear
from lmscorral.bl_license lic, lmscorral.bl_licensetype lt
where lic.LicenseTypeObjectId = lt.ObjectId 
and lic.InitialIssueDate >'01-JAN-16')
group by LicenseType, ApplicationMonth, ApplicationYear
order by LicenseType, ApplicationYear, ApplicationMonth
--runtime 0:03
