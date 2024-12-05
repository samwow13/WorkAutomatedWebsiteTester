# Login Checker Tool

This tool automates the process of checking login functionality across multiple URLs.

## Setup

1. Install Python 3.7 or higher
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Edit the `urls_to_check` list in `login_checker.py` to include your system URLs
2. Run the script:
   ```
   python login_checker.py
   ```

## Features

- Headless browser automation (runs in background)
- Timeout handling
- Error reporting
- Timestamp for each check
- Detailed status report for each URL

## Configuration

The script currently uses default credentials:
- Username: "username"
- Password: "password"

To use your actual credentials, uncomment the environment variable lines and create a `.env` file with:
```
LOGIN_USERNAME=your_username
LOGIN_PASSWORD=your_password
```

## Notes

- The script uses Chrome in headless mode
- Adjust the selectors (By.NAME, By.CSS_SELECTOR) according to your actual login page structure
- Default timeout is 10 seconds per page
