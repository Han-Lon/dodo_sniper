from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import argparse
import getpass
import os
from datetime import datetime, timedelta
from time import sleep

# Need to know if the auction is in tickets or bells to set the ceiling and find quick bid button
while True:
    xpath_bid_btn = str(input("Tickets or Bells?: "))
    if xpath_bid_btn.lower() == 'tickets':
        # Don't go higher than 10 Nook mile tickets
        ceiling = 1
        css_selector_bidbtn = '#btn-quick-bid-1'
        break
    elif xpath_bid_btn.lower() == 'bells':
        # Don't go higher than 150000 bells
        ceiling = 10
        css_selector_bidbtn = '#btn-quick-bid-1000'
        break
    else:
        print('Error. The input needs to be either bells or ticets. Was {}'.format(xpath_bid_btn))

# Snipe when there's this many seconds left
seconds = 2


def login(driver):
    """Login to dodocodes using username+password. Requires minimal user interaction"""
    print('Logging in')
    driver.find_element_by_xpath('/html/body/header/nav/div/ul[2]/li/a').click()
    username_field = driver.find_element_by_xpath('//*[@id="input-email"]')
    passw_field = driver.find_element_by_xpath('//*[@id="input-password"]')
    username_field.send_keys(os.environ['username'])
    passw_field.send_keys(os.environ['password'])
    passw_field.send_keys(Keys.RETURN)
    print('Done logging in')


def discord_login(driver):
    """Login to dodocodes using Discord. Requires user interaction"""
    print('Logging in')
    driver.find_element_by_xpath('/html/body/header/nav/div/ul[2]/li/a').click()
    driver.find_element_by_xpath('//*[@id="at-discord"]').click()
    input('Enter anything here and press return when you\'ve successfully logged in to Discord: ')
    print('Done logging in')


def snipe(driver):
    """Find time left in auction, wait until 2 seconds before auction ends (while checking ceiling), check
       ceiling one more time, and then snipe"""
    time = driver.find_element_by_css_selector('h3.mb-0').text.split()[-1]
    if time.upper() in ['AM', 'PM']:
        print('AM/PM format detected-- handling datetime formatting appropriately')
        time = driver.find_element_by_css_selector('h3.mb-0').text.split()[-2:]
        time = ' '.join(time)
    time = datetime.strptime(time, "%I:%M:%S %p").time()
    tnow = timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)
    tsnipe = timedelta(hours=0, minutes=0, seconds=seconds)
    twait = tnow - tsnipe
    # TODO make this a separate function call
    try:
        current_bid = int(driver.find_element_by_css_selector('div.col-6:nth-child(2) > h4:nth-child(3)').text.replace(',', ''))
    except ValueError as e:
        if 'No bids' in str(e):
            print(f'Received error when checking current_bid, assuming "No Bids". Check this for accuracy {str(e)}')
            current_bid = 0
        else:
            raise
    # Debugging things - make sure the bid button is present and at the expected CSS selector path
    print('Finding bid button...')
    driver.find_element_by_css_selector(css_selector_bidbtn)
    print('Bid button found!')
    print(f'Current bid is {current_bid} and ceiling is {ceiling}')
    try:
        # Don't bid if the current bid is higher than the ceiling (upper limit)
        if current_bid < ceiling:
            pass
        else:
            print('Current bid is {}. Too high, not bidding'.format(str(current_bid)))
            exit(1)
    except TypeError as e:
        print('No bids expected: {}'.format(current_bid))
        print(e)
    # Sleep for a few seconds
    print('Waiting for... {}'.format(str(twait)))
    sleep(twait.total_seconds())
    print('Wait is over')
    # TODO make this a separate function call
    try:
        current_bid = int(driver.find_element_by_css_selector('div.col-6:nth-child(2) > h4:nth-child(3)').text.replace(',', ''))
    except ValueError as e:
        if 'No bids' in str(e):
            print(f'Received error when checking current_bid, assuming "No Bids". Check this for accuracy {str(e)}')
            current_bid = 0
        else:
            raise
    try:
        # If the current bid is lower than the ceiling, place a bid. Otherwise, exit the program
        if current_bid < ceiling:
            driver.find_element_by_css_selector(css_selector_bidbtn).click()
        else:
            print('Current bid is {}. Too high, not bidding'.format(str(current_bid)))
            exit(1)
    except TypeError as e:
        print('No bids expected: {}'.format(current_bid))
        print(e)
        driver.find_element_by_css_selector(css_selector_bidbtn).click()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args()
    driver = webdriver.Firefox()
    driver.get(args.url)
    driver.implicitly_wait(10)
    discord_login(driver)
    snipe(driver)

    