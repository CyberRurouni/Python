from libraries import EC, By, time, random, re


def collect_links(links, side_driver, side_driver_wait):
    for link in links:
        side_driver.get(link)
        # side_driver_wait.until(EC.presence_of_element_located(By.TAG_NAME, "body"))
        time.sleep(random.uniform(2,3))

        article_elem = side_driver.find_element(By.CSS_SELECTOR, "div[role='presentation']")
        h1_elem = article_elem.find_element(By.CSS_SELECTOR, "h1[dir='auto']")
        print(h1_elem)