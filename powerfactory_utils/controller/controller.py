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

    def get_all_generators(self, category: str='') -> list:
        #gen_lst = self.pfi.app.GetCalcRelevantObjects('*.ElmGenstat') #TODO: kann eigentlich weg
        gen_lst = self.pfi.generators(grid=self.grid_name)
        if not category == '':
            gen_lst=[gen for gen in gen_lst if gen.cCategory==category]
        return gen_lst

    def get_generator_attr(self, gen) -> dict: #TODO gibt es hier noch eine unspezifischere Lösung?
        attributes = {"name" : gen.loc_name,
        "outserv" : gen.outserv,
        "load_fl_mode" : gen.mode_inp,
        "power" : gen.pgini,
        "cos_phi" : gen.cosgini,
        "cos_attr" : gen.pf_recap,
        "cCategory" : gen.cCategory}
        return attributes

    #TODO func create_generator()
    def create_generator(self, name) -> bool: #TODO später Interface-function
        #characteristics of a generator
        #PowerFactory function CreateObject --> creates new target object
        
        bus = self.pfi.app.GetCalcRelevantObjects('Feld_12.StaCubic')
        print(bus)
        loc = self.pfi.grid(self.grid_name)
        dat = {"pgini" : 56, "bus1" : bus[0]}#, 'bus1_bar' : 'Node4'}
        element=self.pfi.create_object(name=name, class_name='ElmGenstat',location=loc,data=dat)
        #element.bus1 = bus[0]

        return element 



    #TODO func replace_gen_template() #stays as an PowerfactoryController function
    # --> What kind of generators --> what could be filter or characteristic element 
    # use create_generator()-->use create_gen_name
