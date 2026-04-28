# Polimi Gym Booking Automation

An automated tool that books gym time slots at Polimi's Giurati Fit Center by simulating human-like interactions through web automation.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Features](#features)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Gmail Setup](#gmail-setup)
- [Usage](#usage)
- [Logging](#logging)
- [Code Architecture](#code-architecture)
- [Dependencies](#dependencies)
- [Hosting & Scheduling](#hosting--scheduling)
  - [Local Machine](#local-machine)
  - [Cloud Hosting](#cloud-hosting)
    - [Google Cloud Platform (GCP)](#google-cloud-platform-gcp---compute-engine)
    - [Amazon Web Services (AWS)](#amazon-web-services-aws---ec2)
    - [Microsoft Azure](#microsoft-azure---virtual-machines)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Development Tips](#development-tips)
- [Known Limitations](#known-limitations)
- [Future Enhancements](#future-enhancements)

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
git clone https://www.github.com/barokdg/polimi-gym-booking-automation
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

## Hosting & Scheduling

### Local Machine

To run this script automatically at scheduled intervals on your local machine, use:

#### macOS/Linux (cron)

```bash
crontab -e
```

Add a line to run daily at a specific time. For example, run at 8:00 AM:

```
0 8 * * * DISPLAY=:0 /home/username/polimi-gym-booking-automation/.venv/bin/python3 /home/username/polimi-gym-booking-automation/main.py >> log.log 2>&1
```

**⚠️ Important**: Your computer **must be powered on** for crontab to execute the scheduled task. If you find that this is not the case or have a workaround, please [create an issue](../../issues) or [submit a PR](../../pulls).

#### Windows (Task Scheduler)

Create a task that runs the script at your desired interval using Windows Task Scheduler.

### Cloud Hosting

For continuous automated booking, cloud hosting ensures the script runs reliably without requiring your personal machine to be on.

#### Google Cloud Platform (GCP) - Compute Engine

**Setup Instructions:**

1. Create a Compute Engine VM instance with Ubuntu 26.04 LTS (Minimal). Feel free to choose another VM.
2. Connect to the instance via SSH
3. Install required dependencies:

```bash
# Update package manager
sudo apt update && sudo apt upgrade -y

# Install git
sudo apt install -y git

# Install cron
sudo apt install -y cron

# Install vim or a text editor of your choice
sudo apt install -y vim

# Install Python and venv
sudo apt install -y python3.14 python3.14-venv

# Install Chrome and dependencies for Selenium
wget wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install google-chrome-stable_current_amd64.deb
```

4. Clone the repository:

```bash
git clone https://www.github.com/barokdg/polimi-gym-booking-automation.git
cd polimi-gym-booking-automation
```

5. Create and activate virtual environment:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

6. Configure `.env` file with your credentials:

```bash
vim .env
```

7. Set up crontab:

```bash
crontab -e
```

Add the scheduling line (e.g., run at 8:00 AM UTC):

```
0 8 * * * DISPLAY=:0 /home/username/polimi-gym-booking-automation/.venv/bin/python3 /home/username/polimi-gym-booking-automation/main.py >> log.log 2>&1
```

**Cost Estimate**: A GCP e2-micro instance with minimal Ubuntu is eligible for the free tier (up to 730 hours/month for the first 12 months).

#### Amazon Web Services (AWS) - EC2

*Coming soon. Please refer to the GCP setup above as a general reference, adapting as needed for AWS EC2 instances.*

#### Microsoft Azure - Virtual Machines

*Coming soon. Please refer to the GCP setup above as a general reference, adapting as needed for Azure VMs.*

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