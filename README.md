# Twitch Viewbot Proxy

A Python-based Twitch viewbot that simulates concurrent viewer sessions using SOCKS5 proxies. Features a GUI for configuring sessions, proxy rotation, and capturing screenshots of streams.

## Features
- **Concurrent Sessions**: Run 1–10 browser sessions with staggered launches (30–60s delays).
- **Proxy Support**: Load SOCKS5 proxies from a `.txt` file for random rotation.
- **Headed/Headless Mode**: Toggle between visible and invisible Chrome browsers.
- **Screenshot Capture**: Takes screenshots after 60 seconds of page load.
- **GUI Log**: Displays real-time logs of session starts, proxy usage, and screenshot saves.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/JimWas/Twitch-Viewbot-Proxy.git
   cd Twitch-Viewbot-Proxy





Create and activate a virtual environment:


   python -m venv .venv
.\.venv\Scripts\activate


pip install selenium-wire webdriver_manager blinker

Create a proxies.txt file with SOCKS5 proxies (format: username:password@host:port).

Run the script:


python webscraper.py





Enter a Twitch URL (e.g., https://www.twitch.tv/illphated).
Specify the number of sessions (1–10).
Choose Headed or Headless mode.
Load a proxy file or select None for random proxy selection.
Click "Start Scraping" to launch sessions, which capture screenshots after 60 seconds.

DisclaimerThis tool is for educational purposes only. Using it to artificially inflate Twitch view counts violates Twitch's Terms of Service and may result in account suspension. Use responsibly.LicenseMIT License


