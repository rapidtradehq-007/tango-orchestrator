import os, shutil, uuid, logging

def ignore_chrome_temp_files(_, names):
    return [n for n in names if n in {
        "SingletonSocket", "SingletonCookie", "SingletonLock", "RunningChromeVersion"
    }]

def clone_profile(base_path, root_path):
    clone = os.path.join(root_path, f"profile_{uuid.uuid4().hex}")
    shutil.copytree(base_path, clone, ignore=ignore_chrome_temp_files)
    return clone

def cleanup_driver(driver, profile_path):
    try:
        driver.quit()
    finally:
        if profile_path and os.path.exists(profile_path):
            shutil.rmtree(profile_path, ignore_errors=True)
