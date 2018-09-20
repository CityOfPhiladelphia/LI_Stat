Select distinct JobType, PaymentMonth, PaymentYear, sum(Amount) TotalAmount
from (select distinct jt.Description JobType, job.ExternalFileNum, extract(MONTH from fee.LatestPayment) PaymentMonth, 
extract(YEAR from fee.LatestPayment) PaymentYear, fee.PaymentTotal as Amount
from query.o_fn_fee fee, api.jobs job, api.jobtypes jt
where fee.LatestPayment >= '01-JAN-16'
and fee.ReferencedObjectId = job.JobId 
and job.JobTypeId = jt.JobTypeId )
group by JobType, PaymentYear, PaymentMonth
order by JobType, PaymentYear, PaymentMonth

--0:32 runtime
