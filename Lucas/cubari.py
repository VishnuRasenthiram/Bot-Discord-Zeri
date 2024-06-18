from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# Initialize Chrome WebDriver with ChromeDriverManager
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open the cubari.moe website
driver.get("https://cubari.moe/")

# Find the search input element
search_input = driver.find_element(By.ID, "search")

# Enter the desired link in the search input
link_to_enter = "https://imgur.com/a/MBjAocc"  # Replace with your link
search_input.send_keys(link_to_enter)

# Simulate pressing the Enter key
search_input.send_keys(Keys.RETURN)

# Wait for the page to load (adjust as needed)
time.sleep(5)

# Get the current URL after navigation
current_url = driver.current_url

# Print the current URL
print("URL after navigation:", current_url)

# Close the browser window
driver.quit()
