SELECT AddressKey,
  Unit,
  zip,
  CensusTract,
  ownername,
  OwnOrg,
  PermitNumber,
  PermitType,
  PermitDescription,
  TypeOfWork,
  PERMIT_TYPE_NAME,
  loc,
  DescriptionOfWork,
  PermitIssueDate,
  CertificateOfOccupancy,
  FinalledDate,
  PermitStatus,
  apname,
  Status,
  DeclaredValue,
  ApplicantCapacity,
  bldgarea,
  apdttm,
  MODDTTM,
  INSPAGENCY,
  PrimaryContact,
  ContractorName,
  ContractorType,
  ContractorAddress1,
  ContractorAddress2,
  ContractorCity,
  ContractorState,
  ContractorZip,
  MostRecentInsp,
  SUM(PaidFees) TotalFeesPaid
FROM
  (SELECT p.AddressKey,
    p.Unit,
    p.zip,
    p.CensusTract,
    p.ownername,
    p.Organization OwnOrg,
    p.PermitNumber,
    p.PermitType,
    p.PermitDescription,
    p.TypeOfWork,
    p.PERMIT_TYPE_NAME,
    p.loc,
    p.DescriptionOfWork,
    p.PermitIssueDate,
    p.CertificateOfOccupancy,
    p.FinalledDate,
    p.PermitStatus,
    p.apname,
    p.Status,
    p.DeclaredValue,
    p.ApplicantCapacity,
    p.bldgarea,
    p.apdttm,
    p.MODDTTM,
    p.INSPAGENCY,
    p.PrimaryContact,
    p.ContractorName,
    p.ContractorType,
    p.ContractorAddress1,
    p.ContractorAddress2,
    p.ContractorCity,
    p.ContractorState,
    p.ContractorZip,
    p.MostRecentInsp,
    fee1.amt AS PaidFees
  FROM imsv7.li_allpermits p,
    imsv7.apfee fee1
  WHERE p.apkey                = fee1.apkey (+)
  AND p.PermitIssueDate      >= '01-JAN-16'
  AND fee1.paiddttm         IS NOT NULL)
GROUP BY AddressKey,
  Unit,
  zip,
  CensusTract,
  ownername,
  OwnOrg,
  PermitNumber,
  PermitType,
  PermitDescription,
  TypeOfWork,
  PERMIT_TYPE_NAME,
  loc,
  DescriptionOfWork,
  PermitIssueDate,
  CertificateOfOccupancy,
  FinalledDate,
  PermitStatus,
  apname,
  Status,
  DeclaredValue,
  ApplicantCapacity,
  bldgarea,
  apdttm,
  MODDTTM,
  INSPAGENCY,
  PrimaryContact,
  ContractorName,
  ContractorType,
  ContractorAddress1,
  ContractorAddress2,
  ContractorCity,
  ContractorState,
  ContractorZip,
  MostRecentInsp
