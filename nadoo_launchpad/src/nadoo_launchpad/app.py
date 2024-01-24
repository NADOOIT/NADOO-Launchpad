import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from nadoo_launchpad.services import check_installation_state
from nadoo_launchpad.components.InstallationComponent import InstallationComponent
from nadoo_launchpad.components.ProjectInfoComponent import ProjectInfoComponent




class NADOOLaunchpad(toga.App):
   

    def startup(self):
        main_box = toga.Box(style=Pack(direction=COLUMN))
       
        # Check if installation has already occurred
        if check_installation_state(self.app):
            # Add ProjectInfoComponent to UI blocks if already installed
            project_info_component = ProjectInfoComponent(self, project_data=None)
            main_box.add(project_info_component)
        else:
            # Add InstallationComponent to UI blocks if not installed
            installation_component = InstallationComponent(self)
            main_box.add(installation_component)
        # Set the initial content of the main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content=main_box
        self.main_window.show()

def main():
    return NADOOLaunchpad()
