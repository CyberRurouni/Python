from libraries import EC, By, Keys, time, json, random

# =========== Actions ============ #


# ========== Smooth Scrolling ============ #
def smooth_scroll(driver, pixels):
    """Scroll smoothly by a certain number of pixels and wait for inertia."""
    driver.execute_script(
        """
            window.scrollBy({
                top: arguments[0],
                left: 0,
                behavior: 'smooth'
            });
            """,
        pixels,
    )
    # Dynamic wait proportional to scroll distance (to let animation finish)
    time.sleep(0.25 + abs(pixels) / 500)


# ========== Naviagate to Target ============ #


def target_profile(wait, erratic_pause, username):
    """
    Search and go to a target profile.
    """
    search_input = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@aria-label='Search input']")
        )
    )
    search_input.clear()
    search_input.send_keys(username)
    time.sleep(erratic_pause)

    # wait for dropdown results
    first_result = wait.until(
        EC.element_to_be_clickable((By.XPATH, f"//a[contains(@href, '/{username}/')]"))
    )

    print(f"Navigating to profile: {username}")
    first_result.click()
    time.sleep(erratic_pause)


# ========== Close Instagram Modal ============ #


def close_instagram_modal(driver, wait, timeout=6):
    dlg_xpath = "//div[@role='dialog']"
    btn_xpath = (
        "(//*[name()='svg' and @aria-label='Close']/ancestor::div[@role='button'])[1]"
    )

    # Try 1: XPath (handles SVG namespace)
    try:
        print("Trying to close modal via XPath...")
        btn = wait.until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        driver.execute_script("arguments[0].click();", btn)
    except Exception:
        print("XPath close button not found or not clickable, trying alternatives...")
        print("Trying to close modal via JS")
        # Try 2: JS (pick a VISIBLE close button)
        clicked = driver.execute_script(
            """
            const btns = [...document.querySelectorAll("div[role='button'] svg[aria-label='Close']")]
            .map(s => s.closest("div[role='button']"))
            .filter(b => b && b.getBoundingClientRect().width>0 && b.getBoundingClientRect().height>0 && b.offsetParent !== null);
            if (btns.length){ btns[0].click(); return true; }
            return false;
            """
        )
        if not clicked:
            print("JS close button not found or not clickable, trying alternatives...")
            print("Trying to close modal via ESC key")
            # Try 3: ESC key
            try:
                driver.switch_to.active_element.send_keys(Keys.ESCAPE)
            except Exception:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)

    # Always wait for the dialog to actually close before moving on
    try:
        wait.until(EC.invisibility_of_element_located((By.XPATH, dlg_xpath)))
        return True
    except Exception:
        return False


# ========== Act on Post ============ #
def act_on_post(driver, post, ai_decision):
    """Act on post with human-like micro behaviors."""
    try:
        if ai_decision == "Yes":
            print("AI decided: YES → Showing interest")

            # --- Step 1: Scroll to "... more" if available ---
            try:
                more_button = post.find_element(By.XPATH, ".//span[text()='more']")

                # Smooth scroll to bring the 'more' button into view
                # more_button_bottom = driver.execute_script(
                #     "arguments[0].getBoundingClientRect().bottom", more_button
                # )
                # smooth_scroll(driver, more_button_bottom)
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                    more_button,
                )
                time.sleep(random.uniform(0.8, 1.5))  # pause like a human noticing it

                # Click "... more"
                driver.execute_script("arguments[0].click();", more_button)
                print("Expanded post description.")
                time.sleep(random.uniform(0.5, 1.2))  # pause after expansion
            except:
                print("No 'more' button found for this post.")

            # --- Step 2: Simulate reading caption ---
            try:
                # Capture all visible spans (expanded text)
                spans = post.find_elements(By.CSS_SELECTOR, 'span[dir="auto"]')
                text = " ".join([s.text for s in spans if s.text.strip()])
                text_len = len(text)

                if text_len > 0:
                    # Estimate reading time (humans read ~150–200 wpm ≈ 3–4 chars/sec)
                    est_time = text_len / random.uniform(15, 18)
                    est_time = min(est_time, 30)  # cap max reading time
                    print(
                        f"Estimated reading time {est_time:.2f}s for {text_len} chars."
                    )

                    # Simulate reading in chunks by small smooth scrolls
                    total_scrolled = 0
                    chunk_scroll = 40  # px per chunk
                    while total_scrolled < 200:  # stop after ~200px scroll
                        smooth_scroll(driver, random.randint(20, chunk_scroll))
                        pause = random.uniform(1.0, 2.5)
                        print(f"Reading chunk... pausing {pause:.2f}s")
                        time.sleep(pause)
                        total_scrolled += chunk_scroll

                    # Final pause to finish reading
                    time.sleep(random.uniform(1.5, 3))
                else:
                    print("No readable text found, just pausing briefly.")
                    time.sleep(random.uniform(3, 6))
            except Exception as e:
                print("Error simulating reading:", e)
                time.sleep(random.uniform(3, 6))

        else:
            print("AI decided: NO → Scrolling past")
            time.sleep(random.uniform(0.03, 0.1))

    except Exception as e:
        print("Some Unknown Err:", e)
