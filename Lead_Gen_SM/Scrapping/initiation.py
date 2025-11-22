from libraries import (
    os,
    time,
    random,
    subprocess,
    webdriver,
    Options,
    By,
    WebDriverWait,
    EC,
    socket,
)

########## Find a Free Port ##########

def get_free_port():
    """Find an available port on localhost."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))  # let OS assign a free port
    port = s.getsockname()[1]
    s.close()
    return port


########## Seting up Chrome with remote debugging ##########


def initiate_driver(profile, target=None):
    chrome_path = "/usr/bin/google-chrome"
    user_data_dir = os.path.expanduser(f"~/selenium_learning/{profile}")

    # Pick a free port dynamically
    port = get_free_port()

    # Launch Chrome with unique profile + port
    proc = subprocess.Popen(
        [
            chrome_path,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={user_data_dir}",
            f"--profile-directory={profile}",
        ]
    )

    time.sleep(5)  # give Chrome time to start

    # Connect Selenium to THAT Chrome instance
    options = Options()
    options.debugger_address = f"127.0.0.1:{port}"
    driver = webdriver.Chrome(options=options)

    if target:
        driver.get(target)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(random.uniform(2, 5))

    return driver
