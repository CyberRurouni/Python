from libraries import time, random, re, By, SERE, WDE, EC
from ai_support import recieve_post_info, decide_interest
from actions import act_on_post, smooth_scroll
from post_info import collect_links


class PostHandler:
    def __init__(self, driver_main, wait, side_driver, side_driver_wait):
        self.driver_main = driver_main
        self.wait = wait
        self.side_driver = side_driver
        self.side_driver_wait = side_driver_wait

    # -------------------------------
    # 🔹 Helpers
    # -------------------------------
    def _get_rect(self, element):
        """Return bounding rect (dict with top/bottom/left/right/height/width)."""
        return self.driver_main.execute_script(
            "return arguments[0].getBoundingClientRect();", element
        )

    def _align_post_in_view(self, target, action_butns):
        """Human-like alignment: overshoot down, then correct up, maybe overshoot again."""
        viewport_height = self.driver_main.execute_script("return window.innerHeight;")

        # --- Phase 1: Overshoot down (bigger flicks) ---
        while True:
            target_bottom = self._get_rect(action_butns)["bottom"]
            if target_bottom > viewport_height:
                delta = random.uniform(
                    random.uniform(50, 150), random.uniform(200, 350)
                )
                smooth_scroll(self.driver_main, delta)
                print(f"Initial flick down by {delta:.1f}px")
            else:
                break

        # --- Phase 2: Correction up (smaller nudges) ---
        while True:
            bar_rect = self._get_rect(action_butns)
            bar_top, bar_bottom = bar_rect["top"], bar_rect["bottom"]

            # Stop if action bar is within viewport bounds
            if (bar_top == viewport_height or bar_bottom == viewport_height) or (
                viewport_height > bar_top and viewport_height < bar_bottom
            ):
                print("✅ Actions bar comfortably in view.")
                break

            elif bar_bottom < viewport_height:  # overscrolled past it → scroll up
                correction = random.uniform(
                    random.uniform(20, 30), random.uniform(80, 120)
                )
                smooth_scroll(self.driver_main, -correction)
                print(f"Nudged up by {correction}px")

            elif bar_top > viewport_height:  # not far enough yet → scroll down
                delta = random.uniform(20, 60)
                smooth_scroll(self.driver_main, delta)
                print(f"Nudged down by {delta}px")

    def _stop_scroll(self, post):
        try:
            # Wait for spans inside the post to load (lazy loading case)
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span[dir='auto']"))
            )
        except Exception:
            print("No spans loaded inside post, skipping...")

        post_data = self._extract_post_info(post)
        if post_data:
            info_str = recieve_post_info(post_data)  # JSON string
            ai_decision = decide_interest(info_str)
            print("AI decision:", ai_decision)
            act_on_post(self.driver_main, post, ai_decision)
        else:
            print("Empty post data, skipping...")

    def _extract_post_info(self, post):
        """Extract visible text from spans inside a post."""
        spans = post.find_elements(By.CSS_SELECTOR, 'span[dir="auto"]')
        return [span.text.strip() for span in spans if span.text.strip()]

    def _scroll_until_found(self, find_func, retries=5, delay_range=(1, 3)):
        """Keep scrolling until Selenium can find the element(s) via find_func."""
        attempts, found = 0, None
        while not found and attempts < retries:
            try:
                found = find_func()
            except Exception:
                attempts += 1
                smooth_scroll(self.driver_main, random.uniform(500, 700))
                time.sleep(random.uniform(*delay_range))
                print(f"Scrolling down to find element... (attempt {attempts})")
        return found

    # -------------------------------
    # 🔹 Core Logic
    # -------------------------------
    def _process_post(self, post):
        """Bring post into view, wait for content, decide, and act."""
        try:
            target, action_butns = post, None

            # Locate the first section containing action buttons
            try:
                button = post.find_element(
                    By.CSS_SELECTOR,
                    "section div[data-visualcompletion='ignore-dynamic']",
                )
                action_butns = self.driver_main.execute_script(
                    "return arguments[0].closest('section');", button
                )
                print("✅ Found actions bar.")
            except:
                print("❌ No actions bar found. Using fallback = whole post.")

            if action_butns:
                self._align_post_in_view(target, action_butns)
                time.sleep(random.uniform(3, 6))
                # self._stop_scroll(post)
            else:
                # fallback behavior: wait until bottom in view
                while True:
                    target_bottom = self._get_rect(target)["bottom"]
                    print("Fallback used")
                    if target_bottom <= self.driver_main.execute_script(
                        "return window.innerHeight;"
                    ):
                        self._stop_scroll(post)
                        break
                    smooth_scroll(self.driver_main, random.uniform(30, 120))

        except (WDE, SERE):
            print("Post detached, skipping.")

    # -------------------------------
    # 🔹 Orchestration
    # -------------------------------
    def browse_feed(self):
        """Main driver_main: scroll through feed and process posts."""
        self.wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[contains(@href, '/p/')]")
            )
        )
        urls = self.driver_main.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")

        post_links = []
        seen = set()

        for elem in urls:
            href = elem.get_attribute("href")  # ✅ convert WebElement → string
            if href:
                match = re.match(r"(https://www\.instagram\.com/p/[^/]+/)", href)
                if match:
                    clean_url = match.group(1)
                    if clean_url not in seen:  # keep first occurrence only
                        post_links.append(clean_url)
                        seen.add(clean_url)
                        
        collect_links(post_links, self.side_driver, self.side_driver_wait)
        # post = self._scroll_until_found(
        #     lambda: self.driver_main.find_element(By.XPATH, "//article")
        # )

        # while post:
        #     self._process_post(post)

        #     # Try to get next post
        #     next_post = self.driver_main.execute_script(
        #         "return arguments[0].nextElementSibling;", post
        #     )

        #     if not next_post:
        #         # Retry scroll to trigger lazy load
        #         next_post = self._scroll_until_found(
        #             lambda: post.find_element(By.XPATH, "following-sibling::article")
        #         )
        #         if not next_post:
        #             print("No more posts currently on page.")
        #             break

        #     post = next_post
