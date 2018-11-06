select p.PERMITNUMBER, 
p.APDTTM,
p.PERMITISSUEDATE,
p.PERMITTYPE,
p.TYPEOFWORK,
nvl(b.parentkey, u.parentkey)
from imsv7.li_allpermits p, imsv7.apbldg b, imsv7.apuse u
where p.apkey = b.apkey (+)
and p.apkey = u.apkey (+)
and (b.parentkey = 1 or b.apkey is null)
and(u.parentkey = 1 or u.apkey is null)
and TO_DATE(p.APDTTM, 'YYYY-MM-DD') = TO_DATE(p.PERMITISSUEDATE, 'YYYY-MM-DD')
and p.APDTTM >= '01-JAN-2016'