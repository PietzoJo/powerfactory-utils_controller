# this is a comment --> why is there a failure symbol TODO
import pathlib
from dataclasses import dataclass
from powerfactory_utils.interface import PowerfactoryInterface


POWERFACTORY_PATH = pathlib.Path("C:/Program Files/DIgSILENT")
POWERFACTORY_VERSION = "2022 SP2"


@dataclass
class PowerfactoryController:
    project_name: str
    grid_name: str
    powerfactory_user_profile: str = ""
    powerfactory_path: pathlib.Path = POWERFACTORY_PATH
    powerfactory_version: str = POWERFACTORY_VERSION

    def __post_init__(self) -> None:
        self.pfi = PowerfactoryInterface(
            project_name=self.project_name,
            powerfactory_user_profile=self.powerfactory_user_profile,
            powerfactory_path=self.powerfactory_path,
            powerfactory_version=self.powerfactory_version)

    test = "some Words."
    print(test)

    def get_all_generators(self) -> list:
        gen_lst = self.pfi.app.GetCalcRelevantObjects('*.ElmGenstat')
        return gen_lst