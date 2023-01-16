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
        # characteristics of a generator
        #PowerFactory function CreateObject --> creates new target object
        child=self.pfi.grid_data.GetContents(name+'.'+'ElmGenstat')
        print(child)
        a=self.pfi.grid_data.CreateObject('ElmGenstat', name)
        print(a)
        b=self.pfi.grid(self.grid_name).CreateObject('ElmGenstat', name)
        print(b)
        """
        DataObject DataObject.CreateObject(str className,
                                            [int|str objectNamePart0,]
                                            [...]
                                            )
        ARGUMENTS
        className
        The class name of the object to create.

        objectNameParts (optional)
        Parts of the name of the object to create (without classname) which will be concatenated
        to the object name.
        """
        return True #TODO: is only a filler so far



    #TODO func replace_gen_template() #stays as an PowerfactoryController function
    # --> What kind of generators --> what could be filter or characteristic element 
    # use create_generator()-->use create_gen_name
