@dataclass
class PowerfactoryController:
    project_name: str
    grid_name: str
    powerfactory_user_profile: str = ""
    powerfactory_path: pathlib.Path = POWERFACTORY_PATH
    powerfactory_version: str = powerfactory_version