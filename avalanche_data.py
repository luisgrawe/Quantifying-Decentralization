# IMPORTS
from bs4 import BeautifulSoup
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By
from collections import Counter
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import requests

# GLOBAL VARIABLE OPTIONS FOR CHROMEDRIVER
options = Options()
options.add_argument("--headless")
options.add_argument('--disable-dev-shm-usage')        
options.add_argument('--no-sandbox')


# ----------------------------------------------------------------------------------------
# IMPROVEMENT PROTOCOL
# ----------------------------------------------------------------------------------------
def ava_improvement_protocol():
    """Return a list of the number of AVA imrpovement proposals per author."""

    ava_ip_list = []
    author_ip_list = []

    driver = webdriver.Chrome(options=options)
    driver.get('https://github.com/avalanche-foundation/ACPs/pulls?page=1&q=')
    time.sleep(10)

    # Find all the authors of the AIPs 
    while True:

        authors = driver.find_elements(By.CSS_SELECTOR, 'a.Link--muted[data-hovercard-type="user"]') 

        for a in authors:
            author_ip_list.append(a.text)

        # Attempt to click the next page button
        try:
            next_page_button = driver.find_element(By.CSS_SELECTOR, 'a.next_page')
            next_page_button.click()
            time.sleep(2)

        except NoSuchElementException:
            break  # Exit the loop if there is no next page button (last page)
    
    # Count the number of AIPs per author
    name_counts = Counter(author_ip_list)
    ava_ip_list = list(name_counts.values())

    driver.quit()

    print(f"Avalanche's distribution of AIPs: {ava_ip_list}")

    return ava_ip_list


# ----------------------------------------------------------------------------------------
# REFERENCE-CLIENT CONTRIBUTION
# ----------------------------------------------------------------------------------------
def ava_reference_client_concentration():
    """Return a list of the number of commits per contributor to the AvalancheGo repository."""

    ava_commits_list = []

    while not ava_commits_list:  # Keep retrying until the list is not empty, as sometimes the data is not loaded properly
        try:
            driver = webdriver.Chrome(options=options)
            driver.get('https://github.com/ava-labs/avalanchego/graphs/contributors')
            time.sleep(15)

            # Find all the contributors to the Cardano Foundation's developer portal
            contributors = driver.find_elements(By.CSS_SELECTOR, 'a.Link--secondary.text-normal')

            for contributor in contributors: 
                # Clean the data
                ava_commits_list.append(int(contributor.text.replace(",","").replace(" commits", "").replace(" commit", "")))

            driver.quit()

            if ava_commits_list == []:
                print("Error: Avalanche's Commit Page did not load properly. Retrying...")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    print(f"Avalanche's distribution of commits to the reference client: {ava_commits_list}")

    return ava_commits_list


# ----------------------------------------------------------------------------------------
# GEOGRAPHICAL DIVERSITY & HOSTING CONCENTRATION -> This function combines both parameters to save runtime. This is feasible as for both parameters no backup data source could be identified anyways.
# ----------------------------------------------------------------------------------------
def ava_geo_diversity_hosting_concentration():
    """Return a list of the number of nodes per country and the number of nodes per hosting provider."""

    country_list = []
    host_list = []

    driver = webdriver.Chrome(options=options)
    driver.get('https://avascan.info/staking/validators')
    time.sleep(10)

    # Click the cookies button
    cookies_button = driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-boxed.btn-primary') # Click the cookies button
    cookies_button.click()

    counter = 0 # Counter to keep track of how many times the next page button must be clicked in order to show new data
    home_url = driver.current_url # Get the current URL and store it as the home URL to go back to after each iteration, this is necessary to avoid the "stale element reference" error

    # Loop through all the validator links and extract the location and hosting provider
    while True:    
        #Exctract the links of all validators
        staker_links = [s.get_attribute('href') for s in driver.find_elements(By.CSS_SELECTOR, 'a.node-link')]

        for link in staker_links:
            try:
                driver.get(link)
                time.sleep(2)

                try: 
                    # Locate where the elements are displayed
                    row_elements = driver.find_elements(By.CSS_SELECTOR, 'div.row')

                    # Go through all rows and extract the data stored in the Location and ISP rows
                    for e in row_elements:

                        # Geo data
                        if 'Location' in e.text:
                            if "," in e.find_element(By.CSS_SELECTOR, 'div.col-content').text: # clean data
                                country_list.append(e.find_element(By.CSS_SELECTOR, 'div.col-content').text.split(',')[1]) # sometimes city and country are provided -> only extract the country data
                            else:
                                country_list.append(e.find_element(By.CSS_SELECTOR, 'div.col-content').text)

                        # Hosting provider data
                        elif 'ISP' in e.text:
                            host_list.append(e.find_element(By.CSS_SELECTOR, 'div.col-content').text)

                        # If the data is not available, continue
                        else:
                            continue

                except NoSuchElementException:
                        pass
                
            except WebDriverException:
                driver = webdriver.Chrome(options=options) # restart the driver in case it crashes due to the long runtime
                continue

        counter += 1 # Increment the counter to keep track of how many times the next page button must be clicked
        driver.get(home_url) # Go back to the home URL
        time.sleep(3)

        # Attempt to click the next page button as many times as the counter
        try:
            next_page_button = driver.find_element(By.XPATH, '//*[@id="staking"]/div[2]/div[2]/div[1]/div/div[2]/div[2]/div/button[3]')
            for i in range(counter):
                next_page_button.click()
                time.sleep(1)
            time.sleep(3)

            if next_page_button.get_attribute('disabled'):
                break # Exit the loop if the next page button is disabled -> last page

        except NoSuchElementException:
            break # Exit the loop if there is no next page button 

    country_counts = Counter(country_list) # Count the number of nodes per country
    ava_geo_list = list(country_counts.values())

    host_counts = Counter(host_list) # Count the number of nodes per hosting provider
    ava_hosting_list = list(host_counts.values())

    driver.quit()

    print(f"Avalanche's distribution of nodes per country: {ava_geo_list}")
    print(f"Avalanche's distribution of nodes per hosting provider: {ava_hosting_list}")

    return ava_geo_list, ava_hosting_list


# ----------------------------------------------------------------------------------------
# DECISION MAKING
# ----------------------------------------------------------------------------------------
def ava_decision_making():
    """Return a list of the amount of staked AVAX per validator."""

    ava_stake_list = []

    response = requests.get('https://avascan.info/staking/validators') # Check if the website is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://avascan.info/staking/validators')
        time.sleep(10)

        # Click the cookies button
        cookies_button = driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-boxed.btn-primary') # Click the cookies button
        cookies_button.click()

        # Loop through all the pages and extract the amount of staked AVA
        while True:
            stake_elements = driver.find_elements(By.CSS_SELECTOR, 'td.pvm-td-total-stake')

            # Extract the amount of staked AVA and clean the data
            for e in stake_elements:
                ava_stake_list.append(float(e.text.replace(",", "").replace("AVAX", "")))

            # Attempt to click the next page button    
            try:
                next_page_button = driver.find_element(By.XPATH, '//*[@id="staking"]/div[2]/div[2]/div[1]/div/div[2]/div[2]/div/button[3]')
                next_page_button.click()
                time.sleep(3)

                # Exit the loop if the next page button is disabled -> last page
                if next_page_button.get_attribute('disabled'):
                    break 

            except NoSuchElementException:
                break 

        driver.quit()

        print(f"Avalanche's distribution of staked AVAX per validator: {ava_stake_list}")

        return ava_stake_list
    
    else: # If the website is not available, use the backup data source

        driver = webdriver.Chrome()
        driver.get('https://subnets.avax.network/validators/')
        time.sleep(10)

        # Loop through all the pages and extract the amount of staked AVA
        while True:
            stake_elements = driver.find_elements(By.CSS_SELECTOR, 'td:nth-child(7)')

            # Extract the amount of staked AVA and clean the data
            for e in stake_elements:
                ava_stake_list.append(int(e.text.replace(' AVAX', '').replace(',', '')))
            
            # Attempt to click the next page button
            next_page = driver.find_element(By.CSS_SELECTOR, '#root > div.MuiStack-root.css-irwvew > div:nth-child(2) > div.MuiContainer-root.MuiContainer-maxWidthXl.css-m6s6bk > div > div.MuiPaper-root.MuiPaper-elevation.MuiPaper-rounded.MuiPaper-elevation0.MuiCard-root.css-1530to5 > div.MuiStack-root.css-9vr6n > div > div:nth-child(2) > div > button.MuiButtonBase-root.MuiButton-root.MuiButton-contained.MuiButton-containedSecondary.MuiButton-sizeMedium.MuiButton-containedSizeMedium.MuiButton-disableElevation.MuiButtonGroup-grouped.MuiButtonGroup-groupedHorizontal.MuiButtonGroup-groupedContained.MuiButtonGroup-groupedContainedHorizontal.MuiButtonGroup-groupedContainedSecondary.MuiButton-root.MuiButton-contained.MuiButton-containedSecondary.MuiButton-sizeMedium.MuiButton-containedSizeMedium.MuiButton-disableElevation.MuiButtonGroup-grouped.MuiButtonGroup-groupedHorizontal.MuiButtonGroup-groupedContained.MuiButtonGroup-groupedContainedHorizontal.MuiButtonGroup-groupedContainedSecondary.MuiButtonGroup-lastButton.css-1kt3rdy')
            
            # Exit the loop if the next page button is disabled -> last page
            if next_page.get_attribute('disabled'):
                break

            else:
                next_page.click()
                time.sleep(5)

        driver.quit()

        print(f"Avalanche's distribution of staked AVAX per validator: {ava_stake_list}")

        return ava_stake_list


# ----------------------------------------------------------------------------------------
# EXCHANGE CONCENTRATION
# ----------------------------------------------------------------------------------------
def ava_exchange_concentration():
    """Return a list of the daily trading volume of AVA on different exchanges."""

    ava_exchange_list = []

    response = requests.get('https://coinranking.com/coin/avalanche-avax/exchanges') # Check if the website is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://coinranking.com/coin/avalanche-avax/exchanges')
        time.sleep(10)

        # Click the cookies button
        cookies_button = driver.find_element(By.CSS_SELECTOR, 'button.fc-button.fc-cta-consent.fc-primary-button')
        cookies_button.click()
        time.sleep(1)

        # Loop through all the pages and extract the daily trading volumes of AVA
        while True:
            ava_exchange_elements = driver.find_elements(By.CSS_SELECTOR, 'td:nth-child(3)')

            # Extract the daily trading volumes of AVA and clean the data
            for e in ava_exchange_elements:

                if " billion" in e.text:
                    ava_exchange_list.append(float(e.text.replace(" billion", "").replace("$ ", "").replace(",", "")) * 1000000000)
                elif " million" in e.text:
                    ava_exchange_list.append(float(e.text.replace(" million", "").replace("$ ", "").replace(",", "")) * 1000000)
                else: 
                    ava_exchange_list.append(float(e.text.replace("$ ", "").replace(",", "")))

            # Attempt to click the next page button
            try:
                next_page_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[3]/section/section/div[3]/a/img')
                driver.execute_script("arguments[0].scrollIntoView();", next_page_button)
                if next_page_button.find_element(By.XPATH, '..').get_attribute('class') == 'active-link pagination__button pagination__button--disabled':
                    break

                next_page_button.click()
                time.sleep(2)

            except NoSuchElementException:
                break  # Exit the loop if there is no next page button (last page)

        driver.quit()

        print(f"Avalanche's distribution of trading volume per exchange: {ava_exchange_list}")

        return ava_exchange_list
    
    else: # If the website is not available, use the backup data source

        driver = webdriver.Chrome()
        driver.get("https://cryptorank.io/price/avalanche/exchanges")
        time.sleep(10)

        while True:

            # Find the relevant elements
            relevant_table = driver.find_element(By.CSS_SELECTOR, '#root-container > section > div.sc-be4b7d84-0.sc-e739bd4e-0.lfEaaA.bxDZvl > div > div.sc-7145b3a-0.kcNxkD > table')
            time.sleep(1)
            exchange_elements = relevant_table.find_elements(By.CSS_SELECTOR, 'td:nth-child(8)')

            # Clean the data
            for e in exchange_elements:

                if "N/A" in e.text:
                    pass
                elif "B" in e.text.split()[1]:
                    ava_exchange_list.append(float(e.text.split()[1].replace("B", "").replace("$ ", "").replace(",", "")) * 1000000000)
                elif "M" in e.text.split()[1]:
                    ava_exchange_list.append(float(e.text.split()[1].replace("M", "").replace("$ ", "").replace(",", "")) * 1000000)
                elif "K" in e.text.split()[1]:
                    ava_exchange_list.append(float(e.text.split()[1].replace("K", "").replace("$ ", "").replace(",", "")) * 1000)
                else: 
                    ava_exchange_list.append(float(e.text.split()[1].replace("$ ", "").replace(",", "")))

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

        print(f"Avalanche's distribution of trading volume per exchange: {ava_exchange_list}")

        return ava_exchange_list


# ----------------------------------------------------------------------------------------
# OWNER CONTROL
# ----------------------------------------------------------------------------------------
def ava_owner_control():
    """Return a list of the amount of pre-mined AVA and the current supply of AVA."""

    ava_owner_list = [4500000] # Pre-mined AVA by the founders -> source: https://cryptorank.io/price/avalanche/vesting (only 4.5M AVAX as Owner Control concerns the early stage of the project)

    response = requests.get('https://avascan.info/') # Check if the website is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://avascan.info/')
        time.sleep(10)

        # Find the current supply of AVA
        market_cap_element = driver.find_element(By.XPATH, '//*[@id="stats-container"]/div/div[1]/div[1]/div[2]/div/div[2]/span[2]')
        ava_owner_list.append(float(market_cap_element.text.replace(",", "").replace("M AVAX", "").replace("(", "").replace(")", "")) * 1000000) # Clean the data

        driver.quit()

        print(f"Avalanche's pre-mined AVAX and current supply: {ava_owner_list}")

        return ava_owner_list
    
    else: # If the website is not available, use the backup data source

        driver = webdriver.Chrome()
        driver.get("https://coinmarketcap.com/currencies/avalanche/")
        time.sleep(10)

        supply_element = driver.find_element(By.XPATH, '//*[@id="section-coin-stats"]/div/dl/div[4]/div[1]/dd')

        # Scenario planning as sometimes the website displays the supply in millions and sometimes in full numbers
        if "M" in supply_element.text:
            ava_owner_list.append(float(supply_element.text.replace(",", "").replace(" AVAX", "").replace("M", ""))*1000000)

        else:
            ava_owner_list.append(float(supply_element.text.replace(",", "").replace(" AVAX", "")))

        driver.quit()

        print(f"Avalanche's pre-mined AVAX and current supply: {ava_owner_list}")
        
        return ava_owner_list

