Select distinct PaymentMonth, PaymentYear, sum(Amount) TotalAmount
from (select distinct extract(MONTH from pay.CompletedDate) PaymentMonth, extract(YEAR from pay.CompletedDate) PaymentYear, pay.Amount as Amount
from QUERY.O_FN_PAYMENT pay
where pay.CompletedDate >= '01-JAN-16')
group by PaymentYear, PaymentMonth
order by PaymentYear, PaymentMonth

--0:32 runtime
