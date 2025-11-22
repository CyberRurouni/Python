from libraries import WebDriverWait, EC, By, time, random, Keys

from navigation import navigation
from actions import target_profile, close_instagram_modal
from initiation import initiate_driver
from humanism import PostHandler


########## Seting up Chrome for Insta Browsing ##########
def main_driver():
    profile = "Profile 1"
    target = "https://instagram.com/"
    driver = initiate_driver(profile, target)
    return driver


########## Seting up Chrome for Post Info Scrapping ##########
def auxiliary_driver():
    profile = "Profile 2"
    side_driver = initiate_driver(profile)
    return side_driver


########## Use ThreadPoolExecutor ##########


driver_main = main_driver()
side_driver = auxiliary_driver()


### Constants & Variables
wait = WebDriverWait(driver_main, 10)
side_driver_wait = WebDriverWait(side_driver, 10)
erratic_pause = random.uniform(2, 5)
roll_dice = random.randint(1, 6)

############# Human Touch #############

### Note that It includes Smooth scrolling, home feeds browsing, erratic pauses, reels watching, etc.
post_handler = PostHandler(driver_main, wait, side_driver, side_driver_wait)
post_handler.browse_feed()

############# Scraping with Selenium #############
# navigation("search", wait, erratic_pause)

# target_profile(wait, erratic_pause, username="faseeh_wazir")

# posts = wait.until(
#     EC.presence_of_all_elements_located(
#         (By.XPATH, "//a[contains(@href, '/p/') or contains(@href, '/reel/')]")
#     )
# )

# posts_matrix = [posts[i : i + 3] for i in range(0, len(posts), 3)]

# for idx, row in enumerate(posts_matrix):
#     try:
#         # Pick a random post in this row (1–3 depending on row size)
#         random_post_selection = random.randint(0, len(row) - 1)
#         post = row[random_post_selection]

#         # Scroll & open post
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post)
#         time.sleep(random.uniform(1, 2))
#         driver.execute_script("arguments[0].click();", post)
#         print(f"Opened post/reel from row-{idx+1}, col-{random_post_selection+1}")

#         # Wait for modal viewer
#         wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))

#         # Try to detect if it's a reel (has video tag)
#         try:
#             video_el = wait.until(
#                 EC.presence_of_element_located(
#                     (By.XPATH, "//div[@role='dialog']//video")
#                 )
#             )
#             duration = driver.execute_script("return arguments[0].duration;", video_el)

#             if duration and duration > 0:
#                 watch_time = duration * random.uniform(0.8, 0.95)  # watch 80–95%
#                 print(f"Reel duration: {duration:.2f}s, watching ~{watch_time:.2f}s")
#                 time.sleep(watch_time)
#             else:
#                 print("Duration not ready, fallback wait")
#                 time.sleep(random.uniform(5, 10))
#         except Exception:
#             print("Not a reel, treating as image post")
#             time.sleep(random.uniform(3, 6))

#         # Close modal
#         closed = close_instagram_modal(driver, wait) # returns True/False
#         if closed:
#             print(f"Closed post/reel from row-{idx+1}")
#             time.sleep(random.uniform(2, 4))
#             print("-" * 40)
#         else:
#             print(f"Failed to close modal in row-{idx+1}")
#             continue
#             # optional: continue/retry

#     except Exception as e:
#         print(f"Error with post/reel from row-{idx+1}: {e}")


# Clean shutdown
# driver.quit()  # Selenium releases the browser
# proc.terminate()  # Kill Chrome process you launched
