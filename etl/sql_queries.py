class SqlQuery():
    def __init__(self, extract_query_file, source_db, target_table):
        self.extract_query_file = 'queries/' + extract_query_file
        self.source_db = source_db
        self.target_table = target_table

    @property
    def columns(self):
        '''Returns the column names from the target_table in GISLICLD.'''
        from li_dbs import GISLICLD

        with GISLICLD.GISLICLD() as con:
            with con.cursor() as cursor:
                sql = f"""SELECT 
                              column_name
                          FROM 
                              all_tab_cols
                          WHERE 
                              table_name = '{self.target_table.upper()}'"""
                cursor.execute(sql)
                cols = cursor.fetchall()
                cols = [col[0] for col in cols]
        return cols

    @property
    def insert_query(self):
        '''Generates the insert query based on the target_table and columns.'''
        insert_q = f'''INSERT INTO {self.target_table} (
                            {", ".join(column for column in self.columns)})
                       VALUES ({", ".join(":" + str(num + 1) for num in range(len(self.columns)))})'''
        return insert_q

LicenseVolumesBL = SqlQuery(
    extract_query_file = 'licenses/slide1_license_volumes_BL.sql',
    source_db = 'ECLIPSE_PROD',
    target_table = 'li_stat_licensevolumes_bl'
)

LicenseVolumesTL = SqlQuery(
    extract_query_file = 'licenses/slide1_license_volumes_TL.sql',
    source_db = 'ECLIPSE_PROD',
    target_table = 'li_stat_licensevolumes_tl'
)

LicenseRevenueBL = SqlQuery(
    extract_query_file = 'licenses/slide2_PaymentsbyMonth_BL.sql',
    source_db = 'ECLIPSE_PROD',
    target_table = 'li_stat_licenserevenue_bl'
)

LicenseRevenueTL = SqlQuery(
    extract_query_file = 'licenses/slide2_PaymentsbyMonth_TL.sql',
    source_db = 'ECLIPSE_PROD',
    target_table = 'li_stat_licenserevenue_tl'
)

LicenseTrendsBL = SqlQuery(
    extract_query_file = 'licenses/slide3_license_trends_BL.sql',
    source_db = 'ECLIPSE_PROD',
    target_table = 'li_stat_licensetrends_bl'
)

SubmittalVolumesBL = SqlQuery(
    extract_query_file = 'licenses/slide4_submittal_volumes_BL.sql',
    source_db = 'ECLIPSE_PROD',
    target_table = 'li_stat_submittalvolumes_bl'
)

SubmittalVolumesTL = SqlQuery(
    extract_query_file = 'licenses/slide4_submittal_volumes_TL.sql',
    source_db = 'ECLIPSE_PROD',
    target_table = 'li_stat_submittalvolumes_tl'
)

PermitsFees = SqlQuery(
    extract_query_file = 'permits/Slide1_MonthlyPermitsSubmittedwithPaidFees.sql',
    source_db='LIDB',
    target_table = 'li_stat_permitsfees'
)

PermitsOTCvsReview = SqlQuery(
    extract_query_file = 'permits/Slide3_all_count_monthly_permits.sql',
    source_db = 'LIDB',
    target_table = 'li_stat_permits_otcvsreview'
)

PermitsAccelReview = SqlQuery(
    extract_query_file = 'permits/Slide5_accelerated_reviews.sql',
    source_db = 'LIDB',
    target_table = 'li_stat_permits_accelreview'
)

ImmDang = SqlQuery(
    extract_query_file = 'ImmDang.sql',
    source_db = 'GISLNI',
    target_table = 'li_stat_immdang'
)

Unsafes = SqlQuery(
    extract_query_file = 'Unsafes.sql',
   source_db = 'GISLNI',
    target_table = 'li_stat_unsafes'
)

PublicDemos = SqlQuery(
    extract_query_file = 'PublicDemos.sql',
    source_db = 'DataBridge',
    target_table = 'li_stat_publicdemos'
)

UninspectedServiceRequests = SqlQuery(
    extract_query_file = 'UninspectedServiceRequests.sql',
    source_db = 'GISLNI',
    target_table = 'li_stat_uninspectedservreq'
)

queries = [
    LicenseVolumesBL,
    LicenseVolumesTL,
    LicenseRevenueBL,
    LicenseRevenueTL,
    LicenseTrendsBL,
    SubmittalVolumesBL,
    SubmittalVolumesTL,
    PermitsFees,
    PermitsOTCvsReview,
    PermitsAccelReview,
    ImmDang,
    Unsafes,
    PublicDemos,
    UninspectedServiceRequests
]