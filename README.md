# Network and System Administration Script

This Python script is designed to assist with common network and operating system administration tasks on both Linux and Windows systems.

## Project Structure

network_admin_script/
├── main.py
├── utils/
│   ├── init.py
│   ├── os_detector.py
│   └── common.py
├── user_management/
│   ├── init.py
│   ├── linux_users.py
│   └── windows_users.py
├── network_management/
│   ├── init.py
│   ├── linux_networking.py
│   └── windows_networking.py
├── firewall_management/
│   ├── init.py
│   ├── linux_firewall.py
│   └── windows_firewall.py
├── proxy_management/
│   ├── init.py
│   ├── browser_proxy.py
│   └── system_proxy.py
├── system_monitoring/
│   ├── init.py
│   ├── linux_resources.py
│   └── windows_resources.py
└── README.md

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/network_admin_script.git](https://github.com/your-username/network_admin_script.git)
    cd network_admin_script
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    # On Linux/macOS
    source venv/bin/activate
    # On Windows
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    This script relies on `psutil` for system monitoring.
    ```bash
    pip install psutil
    ```

## How to Run

Execute the `main.py` script from the root directory of the project:

```bash
python main.py
```

## Permissions
IMPORTANT: Most administrative tasks require elevated privileges. You must run this script with administrator (on Windows) or root (on Linux) permissions for it to function correctly.

On Linux:

```bash
sudo python3 main.py
```

On Windows: Open your command prompt or PowerShell as an Administrator, then navigate to the script directory and run:

```bash
python main.py
```

## Features

The script provides the following functionalities:

- User and Group Management: Create, delete, modify users and groups.
- Network Management: Configure IP addresses, DNS, routing.
- Firewall Management: Manage firewall rules (UFW/Firewalld on Linux, Windows Defender Firewall on Windows).
- Browser Proxy Management: (Informational, focuses on system-level proxy due to browser complexity).
- System Resource Monitoring: Monitor CPU, memory, disk, processes, and network statistics.

## Contributing
Feel free to fork the repository, make improvements, and submit pull requests.

## License
[Apache 2.0]