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
        gen_lst = self.pfi.generators(grid=self.grid_name)
        if not category == '':
            gen_lst=[gen for gen in gen_lst if gen.cCategory==category]
        return gen_lst

    def get_generator_attr(self, gen) -> dict: #TODO gibt es hier noch eine unspezifischere Lösung?
        #function in interface.py
        #working with dict and hasasttribute?
        attributes = {"name" : gen.loc_name,
        "outserv" : gen.outserv,
        "load_fl_mode" : gen.mode_inp,
        "power" : gen.pgini,
        "cos_phi" : gen.cosgini,
        "cos_attr" : gen.pf_recap,
        "cCategory" : gen.cCategory}
        return attributes

    def create_generator(self, name) -> bool: #TODO später Interface-function
        bus = self.pfi.app.GetCalcRelevantObjects('Feld_12.StaCubic')#TODO: create field automatically, in interfac.py
        #case 1: new generator -->needed information --> which bus --> is there open field on bus, if not, create new one
        #case 2: exchange generator with new template --> use same field
        loc = self.pfi.grid(self.grid_name)
        dat = {"pgini" : 56, "bus1" : bus[0]}
        element=self.pfi.create_object(name=name, class_name='ElmGenstat',location=loc,data=dat)

        print(ldf)
        return element 

    def run_layout(self):
        layout = self.pfi.app.GetFromStudyCase(
            "ComSgllayout")
        layout.nodeDispersion = 2
        layout.orthoType = 1
        layout.Execute()



    def replace_gen_template(self, name: str, temp: str):
        loc = self.pfi.grid(self.grid_name)
        vorlage = self.pfi.app.GetProjectFolder("templ")
        template = vorlage.GetContents('WindFarm_direct.IntTemplate')
        if len(template) > 1:
            logger.warning("Found more then one element, returning only the first one.")
        print(template)
        elements = template[0].GetContents()
        liste = []
        for ele in elements:
            class_n = ele.GetClassName()
            name = ele.loc_name + 'New'
            next = loc.AddCopy(ele, name)
            liste.append(next)
        _=[print(el.loc_name) for el in liste]
        bus_Feld2=self.pfi.app.GetCalcRelevantObjects('Feld_2.StaCubic')
        bus_Feld1=self.pfi.app.GetCalcRelevantObjects('Feld_1.StaCubic')
        print(bus_Feld2)
        print(bus_Feld1)

        for new_one in liste:
            if new_one.loc_name == 'Line_WFNew':
                new_one.bus2 = self.pfi.app.GetCalcRelevantObjects('Feld_12.StaCubic')[0]
                new_one.bus1 = bus_Feld2[9]
            if new_one.loc_name == 'Line_WTGNew':
                new_one.bus1 = bus_Feld2[10]
                new_one.bus2 = bus_Feld1[9]
            if new_one.loc_name == 'WTGNew':
                new_one.bus1 = bus_Feld1[10]
        #run_layout()
        return liste

    #TODO func replace_gen_template() #stays as an PowerfactoryController function
    # --> What kind of generators --> what could be filter or characteristic element 
    # use create_generator()-->use create_gen_name
