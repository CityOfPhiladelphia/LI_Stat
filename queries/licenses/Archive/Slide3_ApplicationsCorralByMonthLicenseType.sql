Select LicenseType, ApplicationMonth, ApplicationYear, count(distinct LicenseNumber) CountLicensesApplied
from (select DISTINCT lt.name LicenseType, lic.LicenseNumber LicenseNumber,  
extract(MONTH from ap.IssueDate) ApplicationMonth, extract(YEAR from ap.IssueDate) ApplicationYear
from lmscorral.bl_application ap, query.r_bl_application_license rla, lmscorral.bl_license lic, lmscorral.bl_licensetype lt
where lic.LicenseTypeObjectId = lt.ObjectId 
and lic.ObjectId = rla.LicenseObjectId 
and rla.ApplicationObjectId = ap.JOBID 
and lt.Name not like 'Activity'
and ap.StatusDescription like 'Approved' 
and ap.IssueDate >'01-JAN-16')
group by LicenseType, ApplicationMonth, ApplicationYear
order by LicenseType, ApplicationYear, ApplicationMonth

--runtime 0:03
