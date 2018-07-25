'''
Created by Gotham on 13-06-2018.
'''
from selenium import webdriver
import time
from datetime import date, timedelta
import json
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions

EMAIL_XPATH = '//*[@id="email"]'
PASS_XPATH = '//*[@id="pass"]'
LOGIN_BTN_XPATH = '//input[starts-with(@id,"u_0_")]'
CREATE_BTN_XPATH = '//div[starts-with(@id,"u_0_")]/span/div/div[2]/div[2]/div/div[4]/div[1]/span[2]/button'
POST_TEXT_AREA_XPATH = '//div[starts-with(@id,"js_")]/div[1]/div/div[1]/div[2]/div/div[1]/div/div/div/div[2]/div'
SCHEDULE_BTN_XPATH = '//div[starts-with(@id,"js_")]/div[2]/div[3]/div/div[2]/div/span[2]/div/span/button'


class SeleniumFbPostScheduler:
    def __init__(self, page_name, chromedriver_path=None):
        chrome_options = Options()
        chrome_options.add_argument("--disable-notifications")
        self.browser = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
        self.scheduling_url = 'https://www.facebook.com/'+page_name+'/publishing_tools' \
                              '/?section=SCHEDULED_POSTS&sort[0]=scheduled_publish_time_ascending'
        self.browser.get('https://www.facebook.com')
        self.date_to_post = None

    def authenticate(self, email_or_mob, password):
        self.browser.find_element_by_xpath(EMAIL_XPATH).send_keys(email_or_mob)
        self.browser.find_element_by_xpath(PASS_XPATH).send_keys(password)
        self.browser.find_element_by_xpath(LOGIN_BTN_XPATH).click()

    def date_putter(self, date_to_post):
        date_to_post_str = date_to_post.strftime('%d/%m/%Y')
        date_elem = self.browser.switch_to.active_element
        date_elem.send_keys(date_to_post_str)
        self.press_tabs(1)

    def press_tabs(self, no_of_tabs):
        action_chains = webdriver.ActionChains(self.browser)
        for i in range(no_of_tabs):
            action_chains = action_chains.send_keys(Keys.TAB)
        action_chains.perform()

    def time_putter(self, time_to_post):
        time_split = time_to_post.split(':')
        hour_elem = self.browser.switch_to.active_element
        current_hour = hour_elem.get_attribute("aria-valuetext")
        target_hour = time_split[0]
        if current_hour in ["01", "02"]:
            hour_elem.send_keys("00")
        hour_elem.send_keys(target_hour[0])
        hour_elem.send_keys(target_hour[1])
        self.press_tabs(1)
        minute_elem = self.browser.switch_to.active_element
        current_min = int(minute_elem.get_attribute("aria-valuetext"))
        if 0 < current_min < 9:
            minute_elem.send_keys("00")
        minute_elem.send_keys(time_split[1])
        self.press_tabs(3)

    def scheduler(self, starting_date, post_time="10:00"):
        try:
            self.browser.get(self.scheduling_url)
            try:
                alert = self.browser.switch_to.alert
                alert.accept()
            except exceptions.NoAlertPresentException:
                pass
            try:
                self.browser.find_element_by_xpath(CREATE_BTN_XPATH).click()
            except exceptions.NoSuchElementException or exceptions.ElementNotVisibleException:
                time.sleep(6)
                self.browser.find_element_by_xpath(CREATE_BTN_XPATH).click()
            time.sleep(6)
            date_to_post_obj = time.strptime(starting_date, '%d/%m/%Y')
            self.date_to_post = date(date_to_post_obj.tm_year, date_to_post_obj.tm_mon, date_to_post_obj.tm_mday)
            with open('db.json', 'r') as db_read:
                data_list = json.load(db_read)
            while len(data_list) > 0:
                oldest_data = data_list.pop()
                t_a = self.browser.find_element_by_css_selector('div[role="textbox"]')
                t_a.send_keys(oldest_data["message"])
                t_a.send_keys(Keys.ENTER)
                time.sleep(5)
                s_b = self.browser.find_element_by_css_selector(
                    'button[data-testid="react-composer-post-button"][type="submit"]')
                s_b.click()
                time.sleep(2)
                self.press_tabs(2)
                self.browser.switch_to.active_element.clear()
                self.date_putter(self.date_to_post)
                self.time_putter(post_time)
                self.browser.switch_to.active_element.click()
                with open('db.json', 'w') as db_write:
                    json.dump(data_list, db_write)
                self.date_to_post = self.date_to_post + timedelta(1)
        except exceptions.NoSuchElementException or exceptions.ElementNotVisibleException:
            self.scheduler(starting_date=self.date_to_post.strftime('%d/%m/%Y'), post_time=post_time)
