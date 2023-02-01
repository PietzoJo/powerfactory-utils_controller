import pathlib
from dataclasses import dataclass
from powerfactory_utils.interface import PowerfactoryInterface
from powerfactory_utils import powerfactory_types as pft
from loguru import logger

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
        gen_lst = self.pfi.generators(grid=self.grid_name)#function already existsin interface.py
        if not category == '': #if given. specific category of generator is filtered
            gen_lst=[gen for gen in gen_lst if gen.cCategory==category]
        return gen_lst

    def get_generator_attr(self, gen) -> dict: 
        #just an examplehowtoget generator information in PowerFactory
        attributes = {"name" : gen.loc_name,
        "outserv" : gen.outserv,
        "load_fl_mode" : gen.mode_inp,
        "power" : gen.pgini,
        "cos_phi" : gen.cosgini,
        "cos_attr" : gen.pf_recap,
        "cCategory" : gen.cCategory}
        return attributes

    def create_generator(self, name: str, name_bus:str) -> bool:
        try:
            bus = self.pfi.app.GetCalcRelevantObjects(name_bus+'.ElmTerm')[0] 
        except:
            print('No bus with the given name exists in this grid.')
        bus_cubic = bus.GetContents('*.StaCubic')[0]
        #it is necessary to add the copy exactly ona bus,otherwise the field won'thave the attribute 'cterm', no clue why it is like that
        new_field=bus.AddCopy(bus_cubic, 'field_ext_'+name) 
        loc = self.pfi.grid(self.grid_name)
        dat = {"pgini" : 56, "bus1" : new_field}
        #I added this create_object() and update_object() from original repository into my fork
        # my fork wasn't up to date with recent merge in original fork
        element=self.pfi.create_object(name=name, class_name='ElmGenstat',location=loc,data=dat) 
        return element 

    def run_layout(self):
        #this function gets command "ComSgllayout, adjustand executes it."
        layout = self.pfi.app.GetFromStudyCase(
            "ComSgllayout")
        layout.iAction = 0
        layout.nodeDispersion = 1
        layout.orthoType = 1
        try:
            layout.Execute()
        except:
            print('ComSgllayout failed.')
        return True

    def replace_gen_template(self, generator: str, template: str) -> list:
        copy_gen = self.pfi.app.GetCalcRelevantObjects(generator + '.ElmGenstat')[0]
        bus_con = copy_gen.bus1.cterm
        #it is necessary to add the copy exactly ona bus,otherwise the field won'thave the attribute 'cterm', no clue why it is like that
        bus_cubic = bus_con.GetContents('*.StaCubic')[0]
        loc = self.pfi.grid(self.grid_name)
        vorlage = self.pfi.app.GetProjectFolder("templ")
        template = vorlage.GetContents(template + '.IntTemplate') #gets all template objects
        if len(template) > 1:
            logger.warning("Found more then one element, returning only the first one.")
        elements = template[0].GetContents()
        liste = []
        new_field = pft.DataObject
        station_control = pft.DataObject
        new_gen = pft.DataObject
        for ele in elements:
            name = ele.loc_name + generator
            class_name = ele.GetClassName()
            obj = self.pfi.element_of(loc, filter=f"{name}.{class_name}") #check,whether object already exists
            if obj is not None:
                logger.warning(
                    f"{name}.{class_name} already exists. "
                )
            else:
                next = loc.AddCopy(ele, name) #AddCopy is create, it keepsall attributes ofold object except the name
                if next.GetClassName() == "ElmGenstat":
                    next.CopyData(copy_gen) #copys all attributesoforiginal generator, but attributes that exists only intemplate will be overwriten
                    copy_gen.outserv = 1
                    new_gen = next
                if next.GetClassName() == "ElmStactrl":
                    station_control = next
                liste.append(next)
        # set up station controller
        new_gen.av_mode = 'qvchar'
        new_gen.c_pstac = station_control
        ref_nod = self.pfi.app.GetCalcRelevantObjects('PCC_WTG' + generator + '.ElmTerm')[0]
        station_control.refbar = ref_nod
        station_control.p_cub = ref_nod.GetContents('Feld_1.StaCubic')[0]
        # print for user
        _=[print(el.loc_name) for el in liste]
        #ATTENTION: TODO BUG,because template does not store connecting bus1 information
        #############################################################################################################################################
        #after bug fix, this part can be deleted
        bus_field2=self.pfi.app.GetCalcRelevantObjects('Feld_2.StaCubic')
        bus_f2=[field for field in bus_field2 if generator in str(field)]
        bus_field1=self.pfi.app.GetCalcRelevantObjects('Feld_1.StaCubic')
        bus_f1=[field for field in bus_field1 if generator in str(field)]
        for new_one in liste:
            if new_one.loc_name == 'Line_WF'+ generator:
                new_field=bus_con.AddCopy(bus_cubic, 'field_ext_'+generator)
                new_one.bus2 = new_field
                for field in bus_f2:
                    if 'PCC_WTG' in str(field):
                        feld2=field
                        new_one.bus1 = feld2
                        continue
            if new_one.loc_name == 'Line_WTG' + generator:
                for field in bus_f2:
                    if 'Node_WTG' in str(field):
                        feld2=field
                        new_one.bus1 = feld2
                        continue
                for field in bus_f1:
                    if 'PCC_WTG' in str(field):
                        feld1=field
                        new_one.bus2 = feld1
                        continue
            if new_one.loc_name == 'WTG' + generator:
                for field in bus_f1:
                    if 'Node_WTG' in str(field):
                        feld1=field
                        new_one.bus1 = feld1
                        continue
           ########################################################################################################################################################## 
        return liste
