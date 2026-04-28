# Polimi Gym Booking Automation

An automated tool that books gym time slots at Polimi's Giurati Fit Center by simulating human-like interactions through web automation.

## Overview

This project uses Selenium WebDriver to automate the gym booking process on the SportRick platform. It logs into the Polimi system, navigates through the booking flow, handles two-factor authentication via OTP, and automatically books a time slot at the Giurati Fit Center for two days in advance.

The tool mimics human behavior by:
- Adding random delays between actions
- Typing text with human-like keystroke delays
- Respecting page load times

Upon successful booking, it sends a screenshot confirmation email. If an error occurs, it sends an error report email.

## Project Structure

```
polimi-gym-booking-automation/
├── main.py                 # Main automation script with all booking logic
├── requirements.txt        # Python package dependencies
├── .env.example           # Template for environment variables
├── .gitignore             # Git ignore configuration
├── log.log                # Application log file (optionally generated at runtime)
└── README.md              # This file
```

## Features

- **Automated Login**: Authenticates with Polimi credentials
- **OTP Verification**: Generates and enters one-time passwords for 2FA using TOTP
- **Smart Booking**: Books the latest available time slot for two days in advance
- **Email Notifications**: Sends confirmation or error emails via Gmail SMTP
- **Human-like Interaction**: Simulates natural user behavior with random delays
- **Environment-aware Execution**: Supports both development and production modes
- **Intelligent Scheduling**: Only books on weekdays
- **Headless Support**: Can run in headless mode for server environments

## Setup

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser installed
- Gmail account with app-specific password configured
- Polimi credentials with 2FA enabled

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd polimi-gym-booking-automation
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in the project root (use `.env.example` as a template):

```
USER_NAME=your_polimi_username
PASSWORD=your_polimi_password
TOKEN=your_totp_secret_key
DESTINATION_EMAIL_ADDRESS=recipient@example.com
SMTP_EMAIL_ADDRESS=your_gmail@gmail.com
SMTP_PASSWORD=your_gmail_app_password
ENV=prod  # 'dev' or 'prod'
```

#### Variable Details

- **USER_NAME**: Your Polimi account username
- **PASSWORD**: Your Polimi account password
- **TOKEN**: The secret key for TOTP (Time-based One-Time Password) - obtain from your Polimi 2FA settings
- **DESTINATION_EMAIL_ADDRESS**: Email address where booking confirmations/errors will be sent
- **SMTP_EMAIL_ADDRESS**: Gmail account used to send emails
- **SMTP_PASSWORD**: Gmail app-specific password (not your regular password)
- **ENV**: 
  - `dev`: Browser window stays open after execution for debugging
  - `prod`: Runs in headless mode (no visible browser window)

### Gmail Setup

To send emails via Gmail:
1. Enable 2FA on your Google Account
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use the app password in the `SMTP_PASSWORD` variable

## Usage

Run the automation script:

```bash
python main.py
```

The script will:
1. Check if today is a valid booking day (Monday-Friday, adjusted for 2-day advance booking)
2. Initialize a Chrome WebDriver with appropriate options
3. Log into SportRick platform
4. Authenticate with Polimi credentials
5. Enter OTP for 2FA verification
6. Navigate to bookings and select Giurati Fit Center
7. Book the latest available time slot for two days in advance
8. Send a confirmation email with a screenshot
9. Clean up and close the browser

## Logging

Log messages are printed to stdout during execution. Each major action is prefixed with "Started" to track execution flow.

When running via crontab (see [Scheduling](#scheduling) section), both standard output and error messages can be automatically redirected to `log.log` using the `>> log.log 2>&1` redirection, creating a persistent log file for debugging and monitoring past executions.

To manually capture logs to a file when running directly:
```bash
python main.py >> log.log 2>&1
```

## Code Architecture

The project is organized using page object patterns:

- **Page**: Base class for all page interactions with common utilities
- **SportRickLoginPage**: Handles SportRick platform login and cookie acceptance
- **PolimiLoginPage**: Handles Polimi credential authentication
- **VerifyOTPPage**: Generates and enters TOTP codes
- **DashboardPage**: Navigates to bookings section
- **BookingsPage**: Initiates new booking flow
- **NewBookingPage**: Selects the Giurati Fit Center
- **GiuratiFitCenterBookingPage**: Selects available time slot
- **ConfirmTimeSlotPage**: Confirms booking and declines additional slots
- **EmailSMTPClient**: Handles SMTP email operations
- **EmailBookingOutcome**: Sends success/error emails

## Dependencies

See [requirements.txt](requirements.txt) for the complete list. Key dependencies:

- **selenium**: Web automation framework
- **webdriver-manager**: Automatically manages ChromeDriver versions
- **python-dotenv**: Loads environment variables from .env
- **pyotp**: Generates TOTP codes for 2FA
- **trio**: Async I/O library (required by selenium)

## Scheduling

To run this script automatically at scheduled intervals, use:

### macOS/Linux (cron)

```bash
crontab -e
```

Add a line to run daily at a specific time. For example, run at 8:00 AM:

```
0 8 * * * cd /path/to/polimi-gym-booking-automation && source .venv/bin/activate && python main.py >> log.log 2>&1
```

This command redirects both standard output and error messages to `log.log` for debugging and monitoring purposes.

### Windows (Task Scheduler)

Create a task that runs the script at your desired interval using Windows Task Scheduler.

## Troubleshooting

### Common Issues

1. **ElementClickInterceptedException**: Cookie consent buttons may block interaction. The script handles this on certain pages; verify selectors are current if this persists.

2. **No time slots available**: If all slots are booked, the script will raise an exception, which is caught and reported via email.

3. **OTP generation fails**: Ensure your TOKEN environment variable contains a valid TOTP secret (usually a base32-encoded string).

4. **Email not sent**: Verify Gmail app-specific password is correct and 2FA is enabled on the Gmail account.

5. **ChromeDriver issues**: The webdriver-manager handles ChromeDriver automatically, but ensure Chrome browser is installed.

### Development Tips

- Set `ENV=dev` to keep the browser window open for inspection
- Use `log.log` to review execution history
- The script includes various `time.sleep()` calls with random durations to simulate human behavior

## Future Enhancements

- Implement fallback logic to book alternative time slots if preferred slot is unavailable
- Add configurable booking date offset
- Implement retry logic for failed bookings