import os
import time
import yaml
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
from plyer import notification

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, project_path, project_name, log_callback):
        self.project_path = project_path
        self.project_name = project_name
        self.log_callback = log_callback
        self.last_change_time = None
        self.commit_delay = timedelta(seconds=10)
        self.size_limit_mb = 150
        self.retry_delay = timedelta(minutes=10)

        self.gitignore_patterns = self.read_gitignore()

    def read_gitignore(self):
        gitignore_path = os.path.join(self.project_path, '.gitignore')
        patterns = ['.git/']  # Always ignore the .git directory
        if os.path.isfile(gitignore_path):
            with open(gitignore_path, 'r') as f:
                patterns.extend(f.read().splitlines())
        return patterns

    def is_ignored(self, path):
        for pattern in self.gitignore_patterns:
            if path.startswith(os.path.join(self.project_path, pattern.strip('/'))):
                return True
        return False

    def on_any_event(self, event):
        if event.is_directory:
            return None
        else:
            if not self.is_ignored(event.src_path):
                self.last_change_time = datetime.now()
                self.log_callback(f'Change detected in {self.project_name}: {event.src_path}')

    def check_and_commit(self):
        if self.last_change_time and datetime.now() - self.last_change_time >= self.commit_delay:
            self.commit_and_push()

    def commit_and_push(self):
        os.chdir(self.project_path)
        if not os.path.isfile('.gitignore'):
            return

        total_size = self.get_total_size()
        if total_size > self.size_limit_mb * 1024 * 1024:
            self.log_callback(f'{self.project_name} exceeds size limit of {self.size_limit_mb} MB. Skipping.')
            return

        try:
            # Check if there are any changes to commit
            status_output = subprocess.check_output(['git', 'status', '--porcelain'], stderr=subprocess.STDOUT, shell=True)
            if not status_output.strip():
                self.log_callback(f'No changes to commit for {self.project_name}. Skipping.')
                return

            self.log_callback(f'Starting commit and push for {self.project_name}')
            commit_message = f'Automated commit: {datetime.now().ctime()}'
            subprocess.check_call(['git', 'add', '.'], shell=True)
            subprocess.check_call(['git', 'commit', '-m', commit_message], shell=True)
            subprocess.check_call(['git', 'push', 'origin', 'main'], shell=True)
            self.log_callback(f'Successfully committed and pushed {self.project_name} with message: "{commit_message}"')
        except subprocess.CalledProcessError as e:
            self.log_callback(f'Error in {self.project_name}: {str(e)}. Retrying in {self.retry_delay.seconds // 60} minutes.')
            time.sleep(self.retry_delay.seconds)  # Wait before retrying
            self.check_and_commit()

    def get_total_size(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.project_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not self.is_ignored(fp):
                    total_size += os.path.getsize(fp)
        return total_size

def monitor_projects(config_file, log_callback):
    log_callback("Starting to monitor projects")
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    projects_dir = config.get('projects_dir', None)
    project_names = config.get('projects', [])

    if not projects_dir:
        log_callback("Projects directory is not configured. Please run the script manually to set it up.")
        return

    observer = Observer()
    handlers = []

    for dir_name in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, dir_name)

        # Check if we should monitor this project
        should_monitor = (
            '*' in project_names or
            dir_name in project_names
        )
        if os.path.isdir(project_path) and os.path.isfile(os.path.join(project_path, '.gitignore')) and should_monitor:
            handler = ChangeHandler(project_path, dir_name, log_callback)
            observer.schedule(handler, path=project_path, recursive=True)
            handlers.append(handler)
            log_callback(f'Monitoring project: {dir_name}')

    observer.start()
    log_callback("Git automation script is now running.")
    notify("Git automation script is now running.")

    try:
        while True:
            time.sleep(60)  # Check every minute
            for handler in handlers:
                handler.check_and_commit()
    except KeyboardInterrupt:
        observer.stop()
    except Exception as e:
        log_callback(f"Unexpected error: {str(e)}. Restarting monitor.")
        observer.stop()
        time.sleep(10)
        monitor_projects(config_file, log_callback)

    observer.join()

def log_callback(message):
    # Save log in the same directory as the script, not in the project folders
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notification_log.txt")
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{datetime.now().ctime()}: {message}\n")

def notify(message):
    # Send a notification to the user
    notification.notify(
        title="Git Automation Script",
        message=message,
        app_name="Git Automation",
        timeout=10
    )

def setup_projects_directory(config_file):
    projects_dir = input("Enter the path to your projects directory: ")
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    config['projects_dir'] = projects_dir

    with open(config_file, 'w') as file:
        yaml.safe_dump(config, file)
    print("Projects directory has been configured. You can now run the script silently.")
    log_callback("Projects directory has been configured. Please run the script again.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, 'config.yaml')

    log_callback("Script started")

    if not os.path.isfile(config_file):
        initial_config = {'projects': ['*']}
        with open(config_file, 'w') as file:
            yaml.safe_dump(initial_config, file)
        log_callback("Initial config created")
    
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    
    if not config.get('projects_dir'):
        setup_projects_directory(config_file)
        log_callback("Projects directory has been configured. Please run the script again.")
    else:
        monitor_projects(config_file, log_callback)
