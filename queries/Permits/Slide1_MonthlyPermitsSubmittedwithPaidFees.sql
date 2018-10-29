select PermitType, PermitDescription, ( CASE 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '1' THEN 'Jan' 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '2' THEN 'Feb' 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '3' THEN 'Mar' 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '4' THEN 'Apr' 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '5' THEN 'May' 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '6' THEN 'Jun' 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '7' THEN 'Jul' 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '8' THEN 'Aug' 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '9' THEN 'Sept' 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '10' THEN 'Oct' 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '11' THEN 'Nov' 
                             WHEN Extract(month FROM PermitIssueDate) LIKE '12' THEN 'Dec' 
                           END ) 
                         || ' ' 
                         || Extract(year FROM PermitIssueDate) IssuanceMonthYear, 
count(PermitNumber) TotalPermitsIssued, sum(PaidFees) TotalFeesPaid
from (select p.AddressKey, p.Unit, p.zip, p.CensusTract, p.ownername, p.Organization OwnOrg, p.PermitNumber, p.PermitType, p.PermitDescription, p.TypeOfWork, p.PERMIT_TYPE_NAME, p.loc, p.DescriptionOfWork, p.PermitIssueDate, p.CertificateOfOccupancy, p.FinalledDate, 
p.PermitStatus, p.apname, p.Status, p.DeclaredValue, p.ApplicantCapacity, p.bldgarea, p.apdttm, p.MODDTTM, p.INSPAGENCY, p.PrimaryContact, p.ContractorName, p.ContractorType, p.ContractorAddress1, p.ContractorAddress2, p.ContractorCity, p.ContractorState, p.ContractorZip, p.MostRecentInsp, fee1.amt as PaidFees
from imsv7.li_allpermits p, imsv7.apbldg b, imsv7.apfee fee1
where p.apkey = fee1.apkey  (+) 
and p.PermitIssueDate > '01-JAN-16'
and fee1.paiddttm is not null)
group by PermitType, PermitDescription, IssuanceMonthYear
     
