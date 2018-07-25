"""
Created by Gotham on 25-07-2018.
"""
from sfps import SeleniumFbPostScheduler
sfps = SeleniumFbPostScheduler(page_name='YOUR-PAGE-NAME', chromedriver_path=r'PATH-TO-CHROME-DRIVER')
sfps.authenticate(email_or_mob="FB-ID", password="PASSWORD")
sfps.scheduler(starting_date='dd/mm/yyyy', post_time="24:00")
