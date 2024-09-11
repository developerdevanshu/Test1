from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import imaplib
import email
import time
import re


# Step 1: Automate logging into the portal
def login_to_portal(driver, username, password, captcha=True):
    driver.get(" https://jioauto.sit.jio.com/oem-connect/#/auth/login")  # Replace with the actual URL of the portal

    # Fill in the username
    username_field = driver.find_element(By.ID, "userName")  # Adjust based on the ID of the username field
    username_field.send_keys(username)

    # Fill in the password
    password_field = driver.find_element(By.ID, "usrpwd")  # Adjust based on the ID of the password field
    password_field.send_keys(password)

    # Handle captcha (manual or service needed if it's a visual captcha)
    if captcha:
        captcha_checkbox = driver.find_element(By.ID, "recaptcha-checkbox-checkmark")  # Adjust for the actual captcha checkbox
        captcha_checkbox.click()

    # Click the login button
    login_button = driver.find_element(By.ID, "btn secondry-bg text-white")  # Adjust based on the ID of the login button
    login_button.click()


# Step 2: Retrieve OTP from email (Gmail example using IMAP)
def get_otp_from_email(email_address, email_password):
    # Connect to Gmail using IMAP
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_address, email_password)
    mail.select("inbox")  # Select the inbox to search for emails

    # Search for unread emails (use "UNSEEN" for unseen emails)
    result, data = mail.search(None, "UNSEEN")

    otp = None
    for num in data[0].split():
        result, email_data = mail.fetch(num, "(RFC822)")
        raw_email = email_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Check if the email subject contains OTP (adjust based on your OTP email subject)
        if "your otp" in msg["subject"].lower():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    email_body = part.get_payload(decode=True).decode()
                    otp = extract_otp_from_text(email_body)
                    break

    mail.logout()
    return otp


# Step 3: Extract OTP from email body (using regex for 6-digit OTP)
def extract_otp_from_text(email_body):
    otp_match = re.search(r"\b\d{5}\b", email_body)  # Adjust regex based on OTP format
    return otp_match.group(0) if otp_match else None


# Step 4: Automate submission of OTP on the OTP page
def submit_otp(driver, otp):
    otp_field = driver.find_element(By.ID, "otp")  # Adjust based on the OTP input field ID
    otp_field.send_keys(otp)

    submit_button = driver.find_element(By.ID, "btn secondry-bg text-white text-white")  # Adjust based on the submit button ID
    submit_button.click()


def main():
    # Portal and email credentials
    portal_username = "test@gmail.com"
    portal_password = "@12345"
    gmail_email = "test@gmail.com"
    gmail_password = "@123"

    # Step 1: Launch Chrome browser with WebDriver Manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # Step 2: Log in to the portal
    login_to_portal(driver, portal_username, portal_password)

    # Wait for the login process to complete and page redirection to OTP page
    time.sleep(5)  # Adjust based on actual timing

    # Step 3: Retrieve OTP from Gmail
    otp = get_otp_from_email(gmail_email, gmail_password)

    if otp:
        print(f"OTP received: {otp}")

        # Step 4: Submit OTP on the OTP page
        submit_otp(driver, otp)

        # Wait for the OTP submission to complete
        time.sleep(5)  # Adjust according to the response time

        print("Login and OTP verification successful!")
    else:
        print("Failed to retrieve OTP from email.")

    # Close the browser after the process
    driver.quit()


if __name__ == "__main__":
    main()
