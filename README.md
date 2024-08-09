# Auto-Commit Watchdog

Auto-Commit Watchdog is a Python script designed to monitor specified project directories, automatically commit changes, and push them to a GitHub repository. It runs silently in the background, ensuring that your projects are always up-to-date without manual intervention.

## Features

- **Automatic Git Commit and Push**: Monitors specified project directories for changes and commits/pushes them to GitHub.
- **Configurable Projects Directory**: Specify which projects to monitor using a YAML configuration file.
- **Size Limit Check**: Ensures that the total size of committed projects does not exceed 150 MB.
- **Commit Delay**: Commits changes only if no further changes are detected for one hour.
- **Error Notifications**: Provides system notifications and logs errors and status messages.
- **Runs Silently**: Operates in the background without user intervention after initial setup.

## Setup Instructions

### Prerequisites

- Python 3.x
- Git

### Installation

**Note:**
- Ensure that you have initialized the GitHub repository beforehand and have set up your GitHub credentials. This script will only update the repository.
- Currently, this program only monitors projects with a `.gitignore` file to avoid pushing large files and folders (e.g., datasets). Some manual setup is required to ensure proper functionality.

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Darthph0enix7/Auto-Commit_Watchdog
   cd auto-commit-watchdog
   ```

2. **Install Required Python Packages**

    Create a virtual environment (optional but recommended) and install dependencies:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3. **Initial Configuration**
    Run the script manually to configure the projects directory:

        ```bash
        python watcher.py
        ```
    You will be prompted to enter the path to your projects directory. This path will be saved in the config.yaml file.

### Running the Script

1. **Run Silently in the Background**

    Use the provided batch file to run the script silently:

        ```bash
        .\run_watcher.bat
        ```
    This will start the script in the background, and it will log output to script_output.log.

2. **Add to Startup (Optional)**

    To run the script automatically on startup:

    Create a shortcut of run_watcher.bat.
    Press Win + R, type shell:startup, and press Enter.
    Move the shortcut to the Startup folder.

### Configuration

The configuration is stored in config.yaml. Here is an example configuration:

    ```yaml
    projects:
    - "Project1"
    - "Project2"
    - "*"
    projects_dir: "C:/path/to/your/projects"
    ```
- **projects**: List of project directories to monitor. Use "*" to monitor all directories in the projects folder.
- **projects_dir**: Path to the main projects directory.

### Logging and Notifications

- **Notifications**: The script provides system notifications for important events (e.g., commit success, errors).
- **Logging**: All events are logged to notification_log.txt in the script's directory.

### Contributing
Contributions are welcome! Please fork the repository and submit pull requests. :)