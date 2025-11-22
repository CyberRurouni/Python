from libraries import EC, By, time


def navigation(action, wait, erratic_pause):
    """
    Handles navigation actions like search, home, explore, reels.
    """
    match action:
        case "search":
            # Open search box
            search_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='#']"))
            )
            search_btn.click()
            time.sleep(erratic_pause)


        case "home":
            home_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='/']"))
            )
            home_btn.click()
            time.sleep(erratic_pause)

        case "explore":
            explore_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='/explore/']"))
            )
            explore_btn.click()
            time.sleep(erratic_pause)

        case "reels":
            reels_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='/reels/']"))
            )
            reels_btn.click()
            time.sleep(erratic_pause)

        case _:
            print(f"Unknown action: {action}")
