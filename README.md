# LI_Stat
Dashboards for quarterly reports and statistics

The dashboards are as follows (Needs to be Updated):
- Licenses
    - Slide 1: License Volumes
    - Slide 2: License Revenue
    - Slide 3: License Trends
    - Slide 4: Mode of Submittal (Online, In-person, Mail)
- Permits
    - Slide 1: Permit Volumes and Revenues
    - Slide 2: Permit Trends
    - Slide 4: Review Performance
    - Slide 5: Accelerated Reviews
    - Slide 7: Application Completeness
    
## Usage
- Install dependencies and grab phila_mail and li_dbs from G:/PythonModules and paste into the  ..\Lib\site-packages folder of your Python installation.
- Get the config.py file from one of us containing usernames and password logins and put it in your LI_dashboards folder.
- `python index.py` to launch the application
- `python etl/etl.py` to run the etl process for all queries
- `python etl/etl.py -n dashboard_table_name` to run the etl process for one dashboard
    - Ex: `python etl/etl_cli.py -n li_dash_indworkloads_bl`
- `python etl/etl.py -n dashboard_table_name1 -n dashboard_table_name2` to run the etl process for multiple specified dashboards
    - Ex: `python etl/etl_cli.py -n li_dash_indworkloads_bl -n li_dash_activejobs_bl_counts`
