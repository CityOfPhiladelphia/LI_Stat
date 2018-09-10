--Report: Identify percent change in volume for new/ renewal total activity (per license type) 
--between January-June 2016 and January-June 2017. 
--Include CALs.
select DISTINCT lt.name LicenseType, 
extract(MONTH from ap.IssueDate) ApplicationMonth, extract(YEAR from ap.IssueDate) ApplicationYear, 
count(distinct ap.JobId) CountApprovedJobs
from lmscorral.bl_application ap, query.r_bl_application_license rla, lmscorral.bl_license lic, lmscorral.bl_licensetype lt
where lic.LicenseTypeObjectId = lt.ObjectId 
and lic.ObjectId = rla.LicenseObjectId 
and rla.ApplicationObjectId = ap.JOBID 
and ap.StatusDescription like 'Approved' 
and ap.IssueDate >'01-JAN-16'
group by lt.Name, ap.IssueDate
--runtime 0:03
