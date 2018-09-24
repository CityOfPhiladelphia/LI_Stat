SELECT DISTINCT
    jobtype,
    paymentmonth,
    paymentyear,
    (paymentmonth || '-1-' || paymentyear) AS paymentdaymonthyear,
    SUM(amount) totalamount
FROM
    (
        SELECT DISTINCT
            jt.description jobtype,
            job.externalfilenum,
            EXTRACT(MONTH FROM fee.latestpayment) paymentmonth,
            EXTRACT(YEAR FROM fee.latestpayment) paymentyear,
            fee.paymenttotal AS amount
        FROM
            query.o_fn_fee fee,
            api.jobs job,
            api.jobtypes jt
        WHERE
            fee.latestpayment >= '01-JAN-16'
            AND fee.referencedobjectid = job.jobid
            AND job.jobtypeid = jt.jobtypeid
    )
GROUP BY
    jobtype,
    paymentyear,
    paymentmonth
ORDER BY
    jobtype,
    paymentyear,
    paymentmonth

--0:32 runtime