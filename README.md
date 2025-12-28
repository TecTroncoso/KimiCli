# Kimi Reverse Client

A reverse-engineered Python client for Kimi AI (Moonshot) that bypasses the web interface and provides direct API access with advanced features like deep thinking and web search capabilities.

## Features

### Current Features
- **Direct API Access**: Bypass the web interface and communicate directly with Kimi's backend
- **Authentication Management**: Automated login with session persistence and token management
- **Interactive Chat Mode**: Real-time conversation with streaming responses
- **Single Prompt Mode**: Execute one-off queries from command line
- **Session Persistence**: Maintain conversation context across multiple interactions
- **Rich Console Output**: Beautiful terminal interface with colored status messages
- **Headless Browser Automation**: Seamless credential extraction without GUI interference

## Installation

1. Clone or navigate to the kimi directory:
```bash
cd kimi-reverse-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your credentials:
   - Edit `data/.env` with your Google credentials (Kimi uses Google OAuth):
```env
KIMI_EMAIL=your_email@gmail.com
KIMI_PASSWORD=your_password
```

## How to Use

### Interactive Mode
Start an interactive chat session:
```bash
python main.py
```

Available commands during chat:
- `/exit`, `/quit`, `/q` - Exit the program

### Single Prompt Mode
Execute a single query and exit:
```bash
python main.py "What is the capital of France?"
```

## Project Structure

```
kimi/
├── data/                    # Data storage directory
│   ├── .env                # Environment variables (credentials)
│   ├── auth_token.txt      # Stored authentication token
│   ├── kimi_cookies.json   # Browser cookies
│   └── last_login.txt      # Last login timestamp
├── src/                    # Source code
│   ├── __init__.py
│   ├── auth.py            # Authentication and credential extraction
│   ├── client.py          # Main Kimi API client
│   ├── config.py          # Configuration management
│   └── display.py         # Terminal UI and formatting
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Technical Details

### Authentication Flow
1. Checks for existing valid session
2. If expired, launches headless browser
3. Automatically fills Google OAuth login
4. Extracts cookies and auth token
5. Stores credentials for future use

### Session Management
- Sessions expire after 1 hour
- Automatic re-authentication when needed
- Conversation context maintained within sessions
- Graceful handling of network interruptions

## Requirements

- Python 3.8+
- Or manually put cookie in the kimi_cookies.json and auth_token.txt also change last_login.txt to current time i will change it later. 
- Valid Google account (for Kimi login)
- Chrome/Chromium browser (for authentication)
- Internet connection

## Dependencies

- `rich` - Terminal formatting and colors
- `nodriver` - Headless browser automation
- `python-dotenv` - Environment variable management
- `httpx` - HTTP client for API calls

## Troubleshooting

### Common Issues

**Login Failed**
- Verify Google credentials in `data/.env`
- Check internet connection
- Ensure Google account can access Kimi

**Session Expired**
- Delete `data/last_login.txt` to force re-authentication
- Check if Kimi changed their login process

**Browser Issues**
- Install/update Chrome or Chromium
- Check if browser automation is blocked by antivirus

## Security Notes

- Credentials are stored locally in plain text
- Use environment variables for production deployments
- This tool is for educational and research purposes
- Respect Kimi's terms of service

## License

This project is for educational and research purposes. Please respect Kimi's terms of service and use responsibly.

## Disclaimer

This is a reverse-engineered client and is not officially supported by Kimi/Moonshot. Use at your own risk. The authors are not responsible for any issues that may arise from using this software.
