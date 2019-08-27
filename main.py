# coding: utf8

import platform
from pprint import pprint

if platform.system() == 'Linux':
    import ifcopenshell as ifcopenshell
else:
    import ifcopenshell as ifcopenshell


class MetaModel(object):
    def __init__(self, id, project_id, type, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.project_id = project_id
        self.type = type
        self.meta_objects = []

    def __repr__(self):
        return repr(
            {'id': self.id, 'project_id': self.project_id, 'type': self.type, 'meta_objects': self.meta_objects})


class MetaObject(object):
    def __init__(self, id, name, type, parent, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.name = name
        self.type = type
        self.parent = parent

    def __repr__(self):
        return repr({'id': self.id, 'name': self.name, 'type': self.type, 'parent': self.parent})


class IfcParse(object):
    '''
    classdocs
    '''

    def __init__(self, ifc_filename):
        '''
        Constructor
        '''

        self.ifc_filename = ifc_filename
        self.ifcfile = ifcopenshell.open(self.ifc_filename)
        self.project = self.ifcfile.by_type("IfcProject")[0]
        self.metaObjects = []

    def calculate(self):
        self.metaModel = MetaModel(id=self.project.Name, project_id=self.project.GlobalId, type=self.project.is_a())
        metaObjects = self.extractHierarchy(self.project)
        self.metaModel.meta_objects = metaObjects
        return self.metaModel

    def extractHierarchy(self, objectDefinition):

        parentObject = MetaObject(id=objectDefinition.GlobalId, name=objectDefinition.Name,
                                  type=objectDefinition.is_a(), parent=None)

        if str(objectDefinition.is_a()) != "IfcProject":
            self.metaObjects.append(parentObject)

        spatialElement = self.ifcfile.by_type("IfcSpatialStructureElement")

        for element in spatialElement:

            a = element.get_info(recursive=False)
            # pprint(a)
            # pprint(a.keys())
            for cE in element.ContainsElements:
                for rE in cE.RelatedElements:
                    mo = MetaObject(id=rE.GlobalId, name=rE.Name,
                                    type=rE.is_a(), parent=element.GlobalId)
                    self.metaObjects.append(mo)

        # if hasattr(objectDefinition, 'IsDecomposedBy'):
        #     relatedObjects = objectDefinition.IsDecomposedBy
        #     for rO in relatedObjects:
        #         children = self.extractHierarchy(rO)
        #         self.metaObjects.append(children)
        #         # pprint(item.get_info(recursive=True))

        return list(self.metaObjects)


    def response(self):
        result = self.calculate()

        return self.metaModel


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process')
    parser.add_argument('--ifc_filename', metavar='ifc', help='ifc_filename')
    # parser.add_argument('--entities', metavar='entities', help='entities', nargs='+')

    args = parser.parse_args()
    ifc_filename = args.ifc_filename
    # entities = args.entities

    # #print(ifc_filename)
    projet = IfcParse(ifc_filename=ifc_filename)
    # pprint(len(projet.response().meta_objects))
    pprint(projet.response())
