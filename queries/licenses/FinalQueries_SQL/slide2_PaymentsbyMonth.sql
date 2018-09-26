SELECT
     jobtype,
     paymentdate,
     SUM(amount) totalamount
 FROM
     (
         SELECT
             ( CASE
                 WHEN jobtype LIKE 'Amendment/Renewal' THEN 'Business License Amend/Renew'
                 WHEN jobtype LIKE 'Business License Application' THEN 'Business License Application'
                 WHEN jobtype LIKE 'Trade License Amend/Renew' THEN ' Trade License Amend/Renew'
                 WHEN jobtype LIKE 'Trade License Application' THEN 'Trade License Application'
             END ) AS jobtype,
             TO_DATE(paymentyear
                       || '/'
                       || paymentmonth
                       || '/'
                       || '01','yyyy/mm/dd') AS paymentdate,
             amount
         FROM
             (
                 SELECT DISTINCT
                     jt.description     jobtype,
                     job.externalfilenum,
                     EXTRACT(MONTH FROM fee.latestpayment) paymentmonth,
                     EXTRACT(YEAR FROM fee.latestpayment) paymentyear,
                     fee.paymenttotal   AS amount
                 FROM
                     query.o_fn_fee fee,
                     api.jobs job,
                     api.jobtypes jt
                 WHERE
                     fee.latestpayment >= '01-JAN-16'
                     AND fee.referencedobjectid = job.jobid
                     AND job.jobtypeid = jt.jobtypeid
             )
     )
 GROUP BY
     jobtype,
     paymentdate
 ORDER BY
     jobtype,
     paymentdate
    
--0:32 runtime