select AddressKey, Unit, zip, CensusTract, ownername, OwnOrg, PermitNumber, PermitType, PermitDescription, TypeOfWork, PERMIT_TYPE_NAME, loc, DescriptionOfWork, PermitIssueDate, CertificateOfOccupancy, FinalledDate, PermitStatus, apname, Status, 
DeclaredValue, ApplicantCapacity, bldgarea, apdttm, MODDTTM, INSPAGENCY, PrimaryContact, ContractorName, ContractorType, ContractorAddress1, ContractorAddress2, ContractorCity, ContractorState, ContractorZip, MostRecentInsp, sum(PaidFees) TotalFeesPaid
from (select p.AddressKey, p.Unit, p.zip, p.CensusTract, p.ownername, p.Organization OwnOrg, p.PermitNumber, p.PermitType, p.PermitDescription, p.TypeOfWork, p.PERMIT_TYPE_NAME, p.loc, p.DescriptionOfWork, p.PermitIssueDate, p.CertificateOfOccupancy, p.FinalledDate, 
p.PermitStatus, p.apname, p.Status, p.DeclaredValue, p.ApplicantCapacity, p.bldgarea, p.apdttm, p.MODDTTM, p.INSPAGENCY, p.PrimaryContact, p.ContractorName, p.ContractorType, p.ContractorAddress1, p.ContractorAddress2, p.ContractorCity, p.ContractorState, p.ContractorZip, p.MostRecentInsp, fee1.amt as PaidFees
from imsv7.li_allpermits p, imsv7.apbldg b, imsv7.apfee fee1
where trim(p.PermitNumber) = trim(b.apno)
and b.apkey = fee1.apkey  (+) 
and p.PermitIssueDate > '01-JAN-16'
and fee1.paiddttm is not null 
union 
select p.AddressKey, p.Unit, p.zip, p.CensusTract, p.ownername, p.Organization OwnOrg, p.PermitNumber, p.PermitType, p.PermitDescription, p.TypeOfWork, p.PERMIT_TYPE_NAME, p.loc, p.DescriptionOfWork, p.PermitIssueDate, p.CertificateOfOccupancy, p.FinalledDate, 
p.PermitStatus, p.apname, p.Status, p.DeclaredValue, p.ApplicantCapacity, p.bldgarea, p.apdttm, p.MODDTTM, p.INSPAGENCY, p.PrimaryContact, p.ContractorName, p.ContractorType, p.ContractorAddress1, p.ContractorAddress2, p.ContractorCity, p.ContractorState, p.ContractorZip, p.MostRecentInsp, fee2.amt as PaidFees
from imsv7.li_allpermits p, imsv7.apuse u, imsv7.apfee fee2
where trim(p.PermitNumber) = trim(u.apno)
and u.apkey = fee2.apkey (+)
and p.PermitIssueDate > '01-JAN-16'
and fee2.paiddttm is not null)
group by AddressKey, Unit, zip, CensusTract, ownername, OwnOrg, PermitNumber, PermitType, PermitDescription, TypeOfWork, PERMIT_TYPE_NAME, loc, DescriptionOfWork, PermitIssueDate, CertificateOfOccupancy, FinalledDate, PermitStatus, apname, Status, 
DeclaredValue, ApplicantCapacity, bldgarea, apdttm, MODDTTM, INSPAGENCY, PrimaryContact, ContractorName, ContractorType, ContractorAddress1, ContractorAddress2, ContractorCity, ContractorState, ContractorZip, MostRecentInsp
       
     
