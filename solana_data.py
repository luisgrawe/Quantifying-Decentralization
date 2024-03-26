# IMPORTS
from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver 
from selenium.webdriver.common.by import By
from collections import Counter
import re
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

#GLOBAL VARIABLE OPTIONS FOR CHROMEDRIVER
options = Options()
options.add_argument("--headless")
options.add_argument('--disable-dev-shm-usage')        
options.add_argument('--no-sandbox')


# --------------------------------------
# REFERENCE-CLIENT CONTRIBUTION
# --------------------------------------
def sol_reference_client_concentration():
    """Return a list of the amounts of commits to the Solana reference client per author."""

    sol_commits_list = []

    while not sol_commits_list:  # Keep retrying until the list is not empty, as the website does not always load correctly
        try:
            driver = webdriver.Chrome(options=options)
            driver.get('https://github.com/solana-labs/solana/graphs/contributors')
            time.sleep(15)

            # Find all the contributors to the Cardano Foundation's developer portal
            contributors = driver.find_elements(By.CSS_SELECTOR, 'a.Link--secondary.text-normal')

            for contributor in contributors: 
                sol_commits_list.append(int(contributor.text.replace(",","").replace(" commits", "").replace(" commit", ""))) # clean the data

            driver.quit()

            if sol_commits_list == []:
                print("Error: Solana's Commit Page did not load properly. Retrying...")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    return sol_commits_list


# --------------------------------------
# GEOGRAPHIC DIVERSITY
# --------------------------------------
def sol_geo_index():
    """Return a list of the number of nodes per country."""
    sol_geo_case_list = []

    response = requests.get('https://www.validators.app/data-centers?locale=en&network=mainnet&sort_by=data_center') # Check if the first data source is available
    if response.status_code == 200:

        #Define a pattern that matches two capital letters between word boundaries -> Finds country codes
        pattern = r'\b[A-Z]{2}\b'

        driver = webdriver.Chrome(options=options)
        driver.get("https://www.validators.app/data-centers?locale=en&network=mainnet&sort_by=data_center")
        time.sleep(10)
        
        # Get the number of nodes per country, by multiplying the country code by the number of nodes
        country_elements = driver.find_elements(By.CSS_SELECTOR, "td:nth-child(1)")
        mulitply_elements = driver.find_elements(By.CSS_SELECTOR, "td:nth-child(3)")

        for e, m in zip(country_elements, mulitply_elements):
            matches = re.findall(pattern, e.text)
            sol_geo_case_list.extend(matches * int(m.text))

        sol_geo_list = list(Counter(sol_geo_case_list).values())

        driver.quit

        return sol_geo_list

# For the moment this alternative website is not being updated thus I disabled it. However, it might be useful in the future.
#    else: #alternative website if the first one fails

        sol_geo_response = requests.get('https://solanacompass.com/statistics/decentralization')
        time.sleep(20)
        sol_geo_html_content = sol_geo_response.content.decode('UTF-8')
        soup = BeautifulSoup(sol_geo_html_content, 'html.parser')

        # Find the relevant data
        bar_chart_element = soup.find('bar-chart')
        data_attribute_value = bar_chart_element[':data']

        # Define a regular expression to extract numeric values
        pattern = re.compile(r'\d+')

        # Find all numeric values in the :data attribute value
        sol_geo_list = [int(match.group()) for match in pattern.finditer(data_attribute_value)]

        return(sol_geo_list)


# --------------------------------------
# OWNER CONTROL
# --------------------------------------
def sol_owner_control():
    """Return a list of the amount of pre-mined SOL and its current supply."""

    sol_owner_list = [500000000*0.202] # Pre-mined SOL by the founders -> source: https://www.coingecko.com/en/coins/solana/tokenomics

    response = requests.get('https://explorer.solana.com/supply') # Check if the first data source is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://explorer.solana.com/supply')
        time.sleep(10)

        # Get the current supply of SOL
        market_cap_element = driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/div/div[2]/table/tbody/tr[1]/td[2]/span/span')
        sol_owner_list.append(float(market_cap_element.text.replace(",", "").replace("◎", ""))) # clean the data

        driver.quit()

        return sol_owner_list
    
    else: # if the first data source is not available, use the second one

        driver = webdriver.Chrome(options=options)
        driver.get("https://coinmarketcap.com/currencies/solana/")
        time.sleep(10)

        supply_element = driver.find_element(By.XPATH, '//*[@id="section-coin-stats"]/div/dl/div[4]/div[1]/dd')

        # Scenario planning as sometimes the website displays the supply in millions and sometimes in full numbers
        if "M" in supply_element.text:
            sol_owner_list.append(float(supply_element.text.replace(",", "").replace(" SOL", "").replace("M", ""))*1000000)

        else:
            sol_owner_list.append(float(supply_element.text.replace(",", "").replace(" SOL", "")))

        driver.quit()

        return sol_owner_list


# --------------------------------------
# IMPROVEMENT PROTOCOL
# --------------------------------------
def sol_improvement_protocol():
    """Return a list of the amount of SIPs per author."""

    sol_ip_list = []
    author_ip_list = []

    driver = webdriver.Chrome(options=options)
    driver.get('https://github.com/solana-foundation/solana-improvement-documents/pulls?page=&q=')
    time.sleep(10)

    # Get the authors that have contributed to the SIPs
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
        
    name_counts = Counter(author_ip_list) # Count the number of SIPs per author
    sol_ip_list = list(name_counts.values())

    driver.quit()

    return sol_ip_list


# --------------------------------------
# EXCHANGE CONCENTRATION
# --------------------------------------
def sol_exchange_concentration():
    """Return a list of the volume of SOL traded on each exchange."""

    sol_exchange_list = []

    response = requests.get('https://coinranking.com/coin/solana-sol/exchanges') # Check if the first data source is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://coinranking.com/coin/solana-sol/exchanges')
        time.sleep(10)

        # Click the cookies button
        cookies_button = driver.find_element(By.CSS_SELECTOR, 'button.fc-button.fc-cta-consent.fc-primary-button')
        cookies_button.click()
        time.sleep(1)

        # Get the volume of SOL traded on each exchange per page
        while True:
            sol_exchange_elements = driver.find_elements(By.CSS_SELECTOR, 'td:nth-child(3)')

            # Clean the data
            for e in sol_exchange_elements:

                if " billion" in e.text:
                    sol_exchange_list.append(float(e.text.replace(" billion", "").replace("$ ", "").replace(",", "")) * 1000000000)
                elif " million" in e.text:
                    sol_exchange_list.append(float(e.text.replace(" million", "").replace("$ ", "").replace(",", "")) * 1000000)
                else: 
                    sol_exchange_list.append(float(e.text.replace("$ ", "").replace(",", "")))

            # Attempt to click the next page button
            try:
                next_page_button = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[3]/section/section/div[3]/a/img')
                driver.execute_script("arguments[0].scrollIntoView();", next_page_button)

                # Exit the loop if the next page button is disabled
                if next_page_button.find_element(By.XPATH, '..').get_attribute('class') == 'active-link pagination__button pagination__button--disabled':
                    break

                next_page_button.click()
                time.sleep(2)

            except NoSuchElementException:
                break  # Exit the loop if there is no next page button (last page)

        driver.quit()

        return sol_exchange_list
    
    else: # if the first data source is not available, use the second one

        driver = webdriver.Chrome(options=options)
        driver.get('https://cryptorank.io/price/solana/exchanges')
        time.sleep(10)

        while True:

            # Finde the relevant elements
            relevant_table = driver.find_element(By.CSS_SELECTOR, '#root-container > section > div.sc-be4b7d84-0.sc-e739bd4e-0.lfEaaA.bxDZvl > div > div.sc-7145b3a-0.kcNxkD > table')
            time.sleep(1)
            exchange_elements = relevant_table.find_elements(By.CSS_SELECTOR, 'td:nth-child(8)')

            #Clean the data
            for e in exchange_elements:
                if "N/A" in e.text:
                    pass
                elif "B" in e.text.split()[1]:
                    sol_exchange_list.append(float(e.text.split()[1].replace("B", "").replace("$ ", "").replace(",", "")) * 1000000000)
                elif "M" in e.text.split()[1]:
                    sol_exchange_list.append(float(e.text.split()[1].replace("M", "").replace("$ ", "").replace(",", "")) * 1000000)
                elif "K" in e.text.split()[1]:
                    sol_exchange_list.append(float(e.text.split()[1].replace("K", "").replace("$ ", "").replace(",", "")) * 1000)
                else: 
                    sol_exchange_list.append(float(e.text.split()[1].replace("$ ", "").replace(",", "")))

            # Attempt to click the next page button
            next_page = relevant_table.find_element(By.XPATH, '//*[@id="root-container"]/section/div[1]/div/div[3]/div[1]/button[9]')
            time.sleep(1)

            # Exit the loop if the next page button is disabled
            if next_page.get_attribute('disabled'):
                break

            else:
                try:
                    next_page.click()
                    time.sleep(3)

                except NoSuchElementException:
                    break

        driver.quit()

        return sol_exchange_list


# --------------------------------------
# HOSTING CONCENTRATION 
# --------------------------------------
def sol_hosting_concentration():
    """Return a list of the number of validators per hosting provider."""

    response = requests.get('https://www.validators.app/data-centers?locale=en&network=mainnet&sort_by=asn') # Check if the first data source is available
    if response.status_code == 200:
        sol_hosting_list = []
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.validators.app/data-centers?locale=en&network=mainnet&sort_by=asn")
        time.sleep(10)
        
        # Get the number of nodes per hosting provider
        hosting_elements = driver.find_elements(By.CSS_SELECTOR, "td:nth-child(4)")

        for e in hosting_elements:
            sol_hosting_list.append(int(e.text))

        driver.quit

        return sol_hosting_list
    
    else: #alternative website if the first one fails

        hosting_list = []

        driver = webdriver.Chrome(options=options)
        driver.get('https://solanabeach.io/validators')
        time.sleep(10)

        # Click the cookies button
        cookies_button = driver.find_element(By.XPATH, '//*[@id="cookiescript_accept"]')
        cookies_button.click()

        # Scroll down to the bottom of the page to load all elements
        while True:
            # Get the current page height
            last_height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(2)
            # Scroll down to the bottom of the page
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)
            # Calculate the new page height after scrolling
            new_height = driver.execute_script("return document.body.scrollHeight")
            # Break the loop if no additional content is loaded
            if new_height == last_height:
                break

        # Find the validator profiles on the page
        stakers = driver.find_elements(By.CSS_SELECTOR, 'a.sc-lkqHmb.hSwWYd')

        hosting_links = []

        for s in stakers: 
            # Check if the validator is delinquent
            try:
                if s.find_element(By.XPATH, 'ancestor::div/following-sibling::span').text == 'delinquent':
                    continue
            
            # Get the hosting provider's link if the validator is not delinquent
            except NoSuchElementException:
                hosting_links.append(s.get_attribute('href'))

        # Get the hosting provider from the validator's page
        for link in hosting_links:
            try:

                driver.get(link)
                time.sleep(3)

                try:
                    host_element = driver.find_element(By.XPATH, '//ul[@class="sc-daURTG jIngfa"]/li[last()]/span')
                    hosting_list.append(host_element.text.split(' - ', 1)[-1])

                # Skip if the hosting provider is not displayed on the page   
                except:
                    pass
                    
            except WebDriverException:
                driver = webdriver.Chrome(options=options) # Restart the driver if it crashes, as it sometimes does due to the long runtime
                continue

        host_counts = Counter(hosting_list) # Count the number of validators per hosting provider
        sol_hosting_list = list(host_counts.values())

        driver.quit()

        return sol_hosting_list


# --------------------------------------
# DECISION MAKING
# --------------------------------------
def sol_decision_making():
    """Return a list of the number of validators per hosting provider and the amount of staked SOL per validator."""

    sol_stake_list = []

    response = requests.get('https://solanabeach.io/validators') # Check if the first data source is available
    if response.status_code == 200:
        driver = webdriver.Chrome(options=options)
        driver.get('https://solanabeach.io/validators')
        time.sleep(10)

        # Click the cookies button
        cookies_button = driver.find_element(By.XPATH, '//*[@id="cookiescript_accept"]')
        cookies_button.click()

        # Scroll down to the bottom of the page to load all elements
        while True:
            # Get the current page height
            last_height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(2)
            # Scroll down to the bottom of the page
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)
            # Calculate the new page height after scrolling
            new_height = driver.execute_script("return document.body.scrollHeight")
            # Break the loop if no additional content is loaded
            if new_height == last_height:
                break

        # Get the amount of staked SOL per validator
        stake_elements = driver.find_elements(By.CSS_SELECTOR, 'span.sc-fOKMvo')

        for e in stake_elements:
            # Check if the validator is delinquent
            if e.get_attribute('delinquent') == 'false':
                # Clean the data and add it if the validator is not delinquent
                sol_stake_list.append(int(e.text.replace(",", "")))

            else: next
        
        driver.quit()
        
        return sol_stake_list
    
    else: #alternative website if the first one fails
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://solscan.io/validator")
        time.sleep(10)

        while True:

            # Locate the stake data
            stake_elements = driver.find_elements(By.CSS_SELECTOR, "td:nth-child(10)")

            # Clean and add the data except the header
            for e in stake_elements[1:]:
                sol_stake_list.append(float(e.text.strip().replace(",", "")))

            # Attempt to click the next page button
            try:
                next_page_button = driver.find_element(By.XPATH, '/html/body/div/section/main/div/div[3]/div[2]/div/div/div/div[3]/div/div[4]/button')
                time.sleep(1)

                # Exit the loop if the next page button is disabled -> last page
                if next_page_button.get_attribute('disabled'):
                    break

                else:
                    next_page_button.click()

            except NoSuchElementException:
                break

            time.sleep(8)

        driver.quit()
        
        return sol_stake_list
