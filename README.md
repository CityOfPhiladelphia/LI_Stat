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
    
## Overview
- Data is ETL'd from Hansen / Eclipse into AWS RDS nightly for each dashboard
- Data is cached in Redis
- Dashboards are served by Dash / Flask

## Requirements
- Python 3.6+
- Pip
- [Redis](https://github.com/rgl/redis/downloads)
    
## Usage
1. Install dependencies `pip install -r requirements.txt`
2. Get the config.py file from one of us containing usernames and password logins and put it in your LI_dashboards base directory.
3. [Install Redis](https://github.com/rgl/redis/downloads)
4. Launch Redis `C:\Program Files\Redis\redis-server`
5. Launch the web server `python index.py`
6. Run the etl process for all queries `python etl/etl.py`
7. Run the etl process for one dashboard `python etl/etl_cli.py -n dashboard_table_name` 
8. Run the etl process for multiple specified dashboards `python etl/etl_cli.py -n dashboard_table_name1 -n dashboard_table_name2` 

