# IMPORTS
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By
from collections import Counter
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import re
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import requests


# GLOBAL VARIABLE OPTIONS FOR CHROMEDRIVER
options = Options()
options.add_argument("--headless") # Runs Chrome in headless mode.
options.add_argument('--start-maximized') # Start Chrome maximized
options.add_argument('--disable-dev-shm-usage') # Overcome limited resource problems      
options.add_argument('--no-sandbox') # Bypass OS security model


# -------------------------------------------
# IMPROVEMENT PROTOCOL
# -------------------------------------------
def ada_improvement_protocol():
    """Return a list of the number of ADA improvement proposals per author."""

    driver = webdriver.Chrome(options=options)
    driver.get('https://github.com/cardano-foundation/CIPs')
    time.sleep(10)

    # Find the relevant table and extract the links to the CIPs
    relevant_table = driver.find_element(By.CSS_SELECTOR, '#repo-content-pjax-container > div > div > div.Layout.Layout--flowRow-until-md.react-repos-overview-margin.Layout--sidebarPosition-end.Layout--sidebarPosition-flowRow-end > div.Layout-main > react-partial > div > div > div.Box-sc-g0xbh4-0.yfPnm > div:nth-child(1) > table')
    cip_links = []
    authors_list = []

    for elements in relevant_table.find_elements(By.CSS_SELECTOR, 'td.react-directory-row-name-cell-large-screen'):

        if 'CIP' in elements.find_element(By.CSS_SELECTOR, 'a').text: # Skip the elements that are not CIPs
            cip_links.append(elements.find_element(By.CSS_SELECTOR, 'a').get_attribute('href'))

    # Go through all the CIPs and extract the authors
    for link in cip_links:

        driver.get(link)
        time.sleep(5)

        try:
            # Find the relevant section where author names are stored
            relevant_section = driver.find_element(By.CSS_SELECTOR, '#readme > div.Box-sc-g0xbh4-0.bJMeLZ.js-snippet-clipboard-copy-unpositioned > article > table:nth-child(1)')
            author_table = relevant_section.find_element(By.CSS_SELECTOR, 'table')

            # Extract the author names and exclude their email addresses
            for authors in author_table.find_elements(By.CSS_SELECTOR, 'td'):
                authors_list.append(authors.text.split('<', 1)[0].strip())

        except NoSuchElementException:
            continue

    ada_ip_list = list(Counter(authors_list).values())

    driver.quit()

    return ada_ip_list


# -------------------------------------------
# REFERENCE-CLIENT CONTRIBUTION
# -------------------------------------------
def ada_reference_client_concentration():
    """Return a list of the number of ADA reference client commits per author."""

    ada_commits_list = []

    while not ada_commits_list:  # Keep retrying until the list is not empty, as the website might not load properly
        try:

            driver = webdriver.Chrome(options=options)
            driver.get('https://github.com/cardano-foundation/developer-portal/graphs/contributors')
            time.sleep(15)

            # Find all the contributors to the Cardano Foundation's developer portal
            contributors = driver.find_elements(By.CSS_SELECTOR, 'a.Link--secondary.text-normal')
            for contributor in contributors: 
                ada_commits_list.append(int(contributor.text.replace(",","").replace(" commits", "").replace(" commit", "")))

            driver.quit()

            if ada_commits_list == []:
                print("Error: Cardano's Commit Page did not load properly. Retrying...")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    return ada_commits_list


# -------------------------------------------
# OWNER CONTROL
# -------------------------------------------
def ada_owner_control():
    """Return a list of the premined amount of ADA and the current supply."""

    ada_owner_list = [5185414108] #pre-mined ADA by the founders -> Source: https://cardano.org/genesis/

    response = requests.get('https://beta.explorer.cardano.org/en/') # Check if the first source is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://beta.explorer.cardano.org/en/')
        time.sleep(10)

        # Extract the current supply of ADA
        market_cap_element = driver.find_element(By.CSS_SELECTOR, 'span[data-testid="circulating-supply-value"]')

        ada_owner_list.append(float(market_cap_element.text.replace('B', '')) * 1000000000)

        driver.quit()

        return ada_owner_list
    
    else: # If the first source is not available, use the second source

        driver = webdriver.Chrome()
        driver.get("https://coinmarketcap.com/currencies/cardano/")
        time.sleep(10)

        supply_element = driver.find_element(By.XPATH, '//*[@id="section-coin-stats"]/div/dl/div[4]/div[1]/dd')

        # Scenario planning as sometimes the website displays the supply in millions and sometimes in full numbers
        if "M" in supply_element.text:
            ada_owner_list.append(float(supply_element.text.replace(",", "").replace(" ADA", "").replace("B", ""))*1000000000)
        else:
            ada_owner_list.append(float(supply_element.text.replace(",", "").replace(" ADA", "")))

        driver.quit()

        return ada_owner_list


# -------------------------------------------
# EXCHANGE CONCENTRATION
# -------------------------------------------
def ada_exchange_concentration():
    """Return a list of the trading volume of ADA on different exchanges."""

    ada_exchange_list = []

    response = requests.get('https://coinranking.com/coin/cardano-ada/exchanges') # Check if the first source is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://coinranking.com/coin/cardano-ada/exchanges')
        time.sleep(10)

        # Click the cookies button
        cookies_button = driver.find_element(By.CSS_SELECTOR, 'button.fc-button.fc-cta-consent.fc-primary-button')
        cookies_button.click()
        time.sleep(1)

        # Store the trading volume per exchange in a list
        while True:

            ada_exchange_elements = driver.find_elements(By.CSS_SELECTOR, 'td:nth-child(3)')
            # Clean the data
            for e in ada_exchange_elements:

                if " billion" in e.text:
                    ada_exchange_list.append(float(e.text.replace(" billion", "").replace("$ ", "").replace(",", "")) * 1000000000)
                elif " million" in e.text:
                    ada_exchange_list.append(float(e.text.replace(" million", "").replace("$ ", "").replace(",", "")) * 1000000)
                else: 
                    ada_exchange_list.append(float(e.text.replace("$ ", "").replace(",", "")))

            # Attempt to click the next page button
            try:
                next_page_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[3]/section/section/div[3]/a/img')
                driver.execute_script("arguments[0].scrollIntoView();", next_page_button)

                # Exit the loop if the next page button is disabled -> last page
                if next_page_button.find_element(By.XPATH, '..').get_attribute('class') == 'active-link pagination__button pagination__button--disabled':
                    break

                next_page_button.click()
                time.sleep(2)

            except NoSuchElementException:
                break  # Exit the loop if there is no next page button (last page)

        driver.quit()

        return ada_exchange_list
    
    else: # If the first source is not available, use the second source

        driver = webdriver.Chrome()
        driver.get('https://cryptorank.io/price/cardano/exchanges')
        time.sleep(10)

        while True:
            
            # Find the relevant section
            relevant_table = driver.find_element(By.CSS_SELECTOR, '#root-container > section > div.sc-be4b7d84-0.sc-e739bd4e-0.lfEaaA.bxDZvl > div > div.sc-7145b3a-0.kcNxkD > table')
            time.sleep(1)
            exchange_elements = relevant_table.find_elements(By.CSS_SELECTOR, 'td:nth-child(8)')

            # Clean the data
            for e in exchange_elements:
                if "N/A" in e.text:
                    pass
                elif "B" in e.text.split()[1]:
                    ada_exchange_list.append(float(e.text.split()[1].replace("B", "").replace("$ ", "").replace(",", "")) * 1000000000)
                elif "M" in e.text.split()[1]:
                    ada_exchange_list.append(float(e.text.split()[1].replace("M", "").replace("$ ", "").replace(",", "")) * 1000000)
                elif "K" in e.text.split()[1]:
                    ada_exchange_list.append(float(e.text.split()[1].replace("K", "").replace("$ ", "").replace(",", "")) * 1000)
                else: 
                    ada_exchange_list.append(float(e.text.split()[1].replace("$ ", "").replace(",", "")))
            
            # Attempt to click the next page button
            next_page = relevant_table.find_element(By.XPATH, '//*[@id="root-container"]/section/div[1]/div/div[3]/div[1]/button[9]')
            time.sleep(1)

            # Exit the loop if the next page button is disabled -> last page
            if next_page.get_attribute('disabled'):
                break

            else:
                try:
                    next_page.click()
                    time.sleep(3)

                except NoSuchElementException:
                    break

        driver.quit()

        return ada_exchange_list


# -------------------------------------------
# GEOGRAPHICAL DIVERSITY & HOSTING CONCENTRATION -> This function combines both parameters to save runtime. This is feasible as for both parameters no backup data source could be identified anyways. 
# -------------------------------------------
def ada_geo_hosting():
    """Return a list of the number of ADA pools per country and a list of the number of ADA pools per hosting provider."""

    driver = webdriver.Chrome(options=options)
    driver.get('https://adastat.net/de/pools')
    time.sleep(15)

    # Set the right filter options to show all relevant pools (except retired ones) on the website
    option_button = driver.find_element(By.CSS_SELECTOR, 'a.uk-margin-small-left.uk-link-muted')
    time.sleep(1)
    option_button.click()
    time.sleep(1)

    # Set the range slider to show all pools, regardless of how many blocks they have validated
    range_slider = driver.find_element(By.CSS_SELECTOR, '#main > div.uk-box-shadow-small.uk-background-default.uk-padding.uk-margin-small.uk-animation-slide-top-small > div.uk-grid.uk-child-width-1-2\@s.uk-child-width-1-3\@l > div:nth-child(3) > div > div.range-wrapper > div.range-track-wrapper > input')
    target_position = driver.find_element(By.CSS_SELECTOR, '#main > div.uk-box-shadow-small.uk-background-default.uk-padding.uk-margin-small.uk-animation-slide-top-small > div.uk-grid.uk-child-width-1-2\@s.uk-child-width-1-3\@l > div:nth-child(3) > div > div.range-wrapper > div.range-track-wrapper > div.range-track > div.range-step-wrapper.uk-flex.uk-flex-between.uk-text-small > div:nth-child(1)')
    action = ActionChains(driver)
    action.drag_and_drop(range_slider, target_position).perform()
    time.sleep(2)

    # Show all cluster pools, pools with a broken pledge, oversaturated pools and pools with a low ticker
    switches = driver.find_elements(By.CSS_SELECTOR, 'span.switch')
    time.sleep(1)
    for switch in switches[3:-1]:
        switch.click()
        time.sleep(1)
    
    # Save the options
    options_area = driver.find_element(By.CSS_SELECTOR, '#main > div.uk-box-shadow-small.uk-background-default.uk-padding.uk-margin-small.uk-animation-slide-top-small')
    save_options_button = driver.find_element(By.CSS_SELECTOR, 'a.uk-button.uk-button-small.uk-button-primary.uk-margin-small-bottom.margin-5-right')
    time.sleep(1)
    driver.execute_script("arguments[0].scrollIntoView();", options_area)
    time.sleep(1)
    save_options_button.click()


    # Making all elements visible by scrolling down and clicking the 'show more' button
    while True:

        try:
            time.sleep(2)
            # Set the number of elements per page to 96 to show all pools faster
            more_elements_per_page = driver.find_element(By.CSS_SELECTOR, 'select.select-css.uk-margin-small-left')
            select = Select(more_elements_per_page)
            select.select_by_value("96")

            # Scroll down to the bottom of the page
            more_elements_button = driver.find_element(By.CSS_SELECTOR, '#main > div.margin-30-top.uk-margin > div.uk-text-center.uk-light.show-more-wrapper > div')
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)  
            more_elements_button.click()
            time.sleep(2) 

        except NoSuchElementException:
            break

    time.sleep(2)

    # Extract the links to the pool pages    
    pool_links = [p.get_attribute('href') for p in driver.find_elements(By.CSS_SELECTOR,'a.uk-flex')]

    # Go through all the pool pages and extract the hosting provider and country
    host_list = []
    country_list = []

    for link in pool_links:
        try:

            driver.get(link+'#info')
            time.sleep(7)

            # Find the relevant table that stores the hosting provider and country
            relevant_table = driver.find_elements(By.CSS_SELECTOR, 'table')[2]
            host_elements = relevant_table.find_elements(By.CSS_SELECTOR, 'td:nth-child(3)')
            country_elements = relevant_table.find_elements(By.CSS_SELECTOR, 'td:nth-child(2)')

            # Extract the hosting providers but exclude unknown ones
            for host in host_elements:
                if host.text == 'Unknown': # Skip the pools with unknown hosting providers
                    continue
                else:
                    host_list.append(host.text)
            
            # Extract the countries but exclude unknown ones
            for country in country_elements:
                if country.text == 'Unknown': # Skip the pools with unknown countries
                    continue
                else:
                    country_list.append(country.text.strip())
                    
        except WebDriverException: 
            driver = webdriver.Chrome(options=options) # Restart the driver if it crashes, as it might happen due to the long runtime
            continue

        except: # Skip the pool if the tale that stores the hosting provider and country does not exist
            continue

    host_counts = Counter(host_list) # Count the number of times each hosting provider appears
    ada_hosting_list = list(host_counts.values())  

    country_counts = Counter(country_list) # Count the number of times each country appears
    ada_geo_list = list(country_counts.values())

    driver.quit()

    return ada_geo_list, ada_hosting_list


# -------------------------------------------
# DECISSION MAKING
# -------------------------------------------
def ada_decision_making():
    """Return a list of the amount of staked ADA per pool."""
    ada_stake_list = []

    response = requests.get('https://adastat.net/de/pools') # Check if the first source is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://adastat.net/de/pools')
        time.sleep(15)

        # Set the right filter options to show all relevant pools (except retired ones) on the website
        option_button = driver.find_element(By.CSS_SELECTOR, 'a.uk-margin-small-left.uk-link-muted')
        time.sleep(1)
        option_button.click()
        time.sleep(1)

        # Set the range slider to show all pools, regardless of how many blocks they have validated
        range_slider = driver.find_element(By.CSS_SELECTOR, '#main > div.uk-box-shadow-small.uk-background-default.uk-padding.uk-margin-small.uk-animation-slide-top-small > div.uk-grid.uk-child-width-1-2\@s.uk-child-width-1-3\@l > div:nth-child(3) > div > div.range-wrapper > div.range-track-wrapper > input')
        target_position = driver.find_element(By.CSS_SELECTOR, '#main > div.uk-box-shadow-small.uk-background-default.uk-padding.uk-margin-small.uk-animation-slide-top-small > div.uk-grid.uk-child-width-1-2\@s.uk-child-width-1-3\@l > div:nth-child(3) > div > div.range-wrapper > div.range-track-wrapper > div.range-track > div.range-step-wrapper.uk-flex.uk-flex-between.uk-text-small > div:nth-child(1)')
        action = ActionChains(driver)
        action.drag_and_drop(range_slider, target_position).perform()
        time.sleep(2)

        # Show all cluster pools, pools with a broken pledge, oversaturated pools and pools with a low ticker
        switches = driver.find_elements(By.CSS_SELECTOR, 'span.switch')
        time.sleep(1)
        for switch in switches[3:-1]:
            switch.click()
            time.sleep(1)

        # Save the options
        options_area = driver.find_element(By.CSS_SELECTOR, '#main > div.uk-box-shadow-small.uk-background-default.uk-padding.uk-margin-small.uk-animation-slide-top-small')
        save_options_button = driver.find_element(By.CSS_SELECTOR, 'a.uk-button.uk-button-small.uk-button-primary.uk-margin-small-bottom.margin-5-right')
        time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView();", options_area)
        time.sleep(1)
        save_options_button.click()

        # Making all elements visible by scrolling down and clicking the 'show more' button
        while True:
            try:
                # Set the number of elements per page to 96 to show all pools faster
                time.sleep(2)
                more_elements_per_page = driver.find_element(By.CSS_SELECTOR, 'select.select-css.uk-margin-small-left')
                select = Select(more_elements_per_page)
                select.select_by_value("96")

                # Scroll down to the bottom of the page
                more_elements_button = driver.find_element(By.CSS_SELECTOR, '#main > div.margin-30-top.uk-margin > div.uk-text-center.uk-light.show-more-wrapper > div')
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(2)  
                more_elements_button.click()
                time.sleep(2) 

            except NoSuchElementException:
                break

        time.sleep(2)

        # Extract the staked ADA per pool
        stake_elements = driver.find_elements(By.CSS_SELECTOR, 'td:nth-child(13)')

        for stakes in stake_elements:
            try:
                cleaned_stake = stakes.text.replace("₳", "").replace(",", "").replace("&nbsp;", "").replace("\u00a0", "").strip().lower()

                # For some data points on the website, normal data cleaning does not work -> thus, a regular expression is used

                match = re.match(r'([\d.,]+)\s*([kKmM]?)', cleaned_stake) # Pattern identifies numbers with a suffix (k, m for thousands and millions)

                if match:
                    value, suffix = match.groups()
                    value = float(value.replace(",", "")) # delete commas
                    
                    # Convert 'k' to thousands and 'm' to millions
                    if suffix.lower() == 'k':
                        value *= 1000

                    elif suffix.lower() == 'm':
                        value *= 1000000
                    
                    ada_stake_list.append(value)

            except ValueError as e:
                print(f"Error converting string to float: {e}")


        driver.quit()

        return ada_stake_list
    
    else: # If the first source is not available, use the second source

        driver = webdriver.Chrome(options=options)
        i = 1 # Set an index for looping through the several pages -> this is a more robust approach than trying to click buttons on a page, hence it is used if possible

        while True:
            driver.get('https://beta.explorer.cardano.org/en/pools?page='+str(i)+'&size=50&sort=&retired=false')   
            time.sleep(7)

            # Extract the staked ADA per pool
            stake_elements = driver.find_elements(By.CSS_SELECTOR, 'td:nth-child(3)')

            for e in stake_elements:
                if e.text == "N/A": # Skip the pools with unknown staked ADA
                    continue

                ada_stake_list.append(float(e.text.replace(",", ""))) # Clean the data

            i += 1 # Increase the index to go to the next page

            # Exit the loop if the next page button is disabled -> last page
            if driver.find_element(By.XPATH, '/html/body/div/div/div[2]/div/div[3]/main/div/div[4]/div[3]/nav/ul/li[10]/button').get_attribute('disabled'):
                break

        driver.quit()
        
        return ada_stake_list
