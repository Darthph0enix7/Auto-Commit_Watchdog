import os
import time
import yaml
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
from plyer import notification

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, project_path, project_name, notification_callback):
        self.project_path = project_path
        self.project_name = project_name
        self.notification_callback = notification_callback
        self.last_change_time = datetime.now()
        self.commit_delay = timedelta(hours=1)
        self.size_limit_mb = 150

    def on_any_event(self, event):
        if event.is_directory:
            return None
        else:
            self.last_change_time = datetime.now()

    def check_and_commit(self):
        if datetime.now() - self.last_change_time >= self.commit_delay:
            self.commit_and_push()

    def commit_and_push(self):
        os.chdir(self.project_path)
        if not os.path.isfile('.gitignore'):
            self.notification_callback(f'{self.project_name} is missing a .gitignore file. Please create one.')
            return

        total_size = self.get_total_size()
        if total_size > self.size_limit_mb * 1024 * 1024:
            self.notification_callback(f'{self.project_name} exceeds size limit of {self.size_limit_mb} MB. Please reduce the size.')
            return

        try:
            subprocess.call(['git', 'add', '.'])
            subprocess.call(['git', 'commit', '-m', f'Automated commit: {datetime.now().ctime()}'])
            subprocess.call(['git', 'push', 'origin', 'main'])
            self.notification_callback(f'{self.project_name} has been successfully committed and pushed.')
        except Exception as e:
            self.notification_callback(f'Error in {self.project_name}: {str(e)}')

    def get_total_size(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.project_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

def monitor_projects(config_file, notification_callback):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    projects_dir = config.get('projects_dir', None)
    if not projects_dir:
        notification_callback("Projects directory is not configured. Please run the script manually to set it up.")
        return

    observer = Observer()
    handlers = []

    for project_name in config['projects']:
        if project_name == '*':
            for dir_name in os.listdir(projects_dir):
                project_path = os.path.join(projects_dir, dir_name)
                if os.path.isdir(project_path):
                    handler = ChangeHandler(project_path, dir_name, notification_callback)
                    observer.schedule(handler, path=project_path, recursive=True)
                    handlers.append(handler)
                    notification_callback(f'Monitoring project: {dir_name}')
        else:
            project_path = os.path.join(projects_dir, project_name)
            if os.path.isdir(project_path):
                handler = ChangeHandler(project_path, project_name, notification_callback)
                observer.schedule(handler, path=project_path, recursive=True)
                handlers.append(handler)
                notification_callback(f'Monitoring project: {project_name}')

    observer.start()
    try:
        notification_callback("Git automation script is now running.")
        while True:
            time.sleep(60)  # Check every minute
            for handler in handlers:
                handler.check_and_commit()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    notification_callback("Git automation script has been stopped.")

def log_notification(message):
    with open("notification_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now().ctime()}: {message}\n")
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
    log_notification("Projects directory has been configured. Please run the script again.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, 'config.yaml')
    log_file = os.path.join(script_dir, 'notification_log.txt')

    if not os.path.isfile(config_file):
        initial_config = {'projects': ['*']}
        with open(config_file, 'w') as file:
            yaml.safe_dump(initial_config, file)
    
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    
    if not config.get('projects_dir'):
        setup_projects_directory(config_file)
        log_notification("Projects directory has been configured. Please run the script again.")
    else:
        monitor_projects(config_file, log_notification)
import os
import time
import yaml
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
from plyer import notification

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, project_path, project_name, notification_callback):
        self.project_path = project_path
        self.project_name = project_name
        self.notification_callback = notification_callback
        self.last_change_time = datetime.now()
        self.commit_delay = timedelta(hours=1)
        self.size_limit_mb = 150

    def on_any_event(self, event):
        if event.is_directory:
            return None
        else:
            self.last_change_time = datetime.now()

    def check_and_commit(self):
        if datetime.now() - self.last_change_time >= self.commit_delay:
            self.commit_and_push()

    def commit_and_push(self):
        os.chdir(self.project_path)
        if not os.path.isfile('.gitignore'):
            self.notification_callback(f'{self.project_name} is missing a .gitignore file. Please create one.')
            return

        total_size = self.get_total_size()
        if total_size > self.size_limit_mb * 1024 * 1024:
            self.notification_callback(f'{self.project_name} exceeds size limit of {self.size_limit_mb} MB. Please reduce the size.')
            return

        try:
            subprocess.call(['git', 'add', '.'])
            subprocess.call(['git', 'commit', '-m', f'Automated commit: {datetime.now().ctime()}'])
            subprocess.call(['git', 'push', 'origin', 'main'])
            self.notification_callback(f'{self.project_name} has been successfully committed and pushed.')
        except Exception as e:
            self.notification_callback(f'Error in {self.project_name}: {str(e)}')

    def get_total_size(self):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.project_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

def monitor_projects(config_file, notification_callback):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)

    projects_dir = config.get('projects_dir', None)
    if not projects_dir:
        notification_callback("Projects directory is not configured. Please run the script manually to set it up.")
        return

    observer = Observer()
    handlers = []

    for project_name in config['projects']:
        if project_name == '*':
            for dir_name in os.listdir(projects_dir):
                project_path = os.path.join(projects_dir, dir_name)
                if os.path.isdir(project_path):
                    handler = ChangeHandler(project_path, dir_name, notification_callback)
                    observer.schedule(handler, path=project_path, recursive=True)
                    handlers.append(handler)
                    notification_callback(f'Monitoring project: {dir_name}')
        else:
            project_path = os.path.join(projects_dir, project_name)
            if os.path.isdir(project_path):
                handler = ChangeHandler(project_path, project_name, notification_callback)
                observer.schedule(handler, path=project_path, recursive=True)
                handlers.append(handler)
                notification_callback(f'Monitoring project: {project_name}')

    observer.start()
    try:
        notification_callback("Git automation script is now running.")
        while True:
            time.sleep(60)  # Check every minute
            for handler in handlers:
                handler.check_and_commit()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    notification_callback("Git automation script has been stopped.")

def log_notification(message):
    with open("notification_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now().ctime()}: {message}\n")
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
    log_notification("Projects directory has been configured. Please run the script again.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, 'config.yaml')
    log_file = os.path.join(script_dir, 'notification_log.txt')

    if not os.path.isfile(config_file):
        initial_config = {'projects': ['*']}
        with open(config_file, 'w') as file:
            yaml.safe_dump(initial_config, file)
    
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    
    if not config.get('projects_dir'):
        setup_projects_directory(config_file)
        log_notification("Projects directory has been configured. Please run the script again.")
    else:
        monitor_projects(config_file, log_notification)
