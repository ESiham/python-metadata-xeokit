# coding: utf8
import ifcopenshell as ifcopenshell
import jsonpickle


class MetaModel(object):
    def __init__(self, id, project_id, type, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self.project_id = project_id
        self.type = type
        self.meta_objects = []

    @property
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
    """
    classdocs
    """

    def __init__(self, ifc_filename):
        """
        Constructor
        """

        self.ifc_filename = ifc_filename
        self.ifcfile = ifcopenshell.open(self.ifc_filename)
        self.project = self.ifcfile.by_type("IfcProject")[0]
        self.metaModel = MetaModel(id=self.project.Name, project_id=self.project.GlobalId, type=self.project.is_a())
        self.metaObjects = []

    def extract_hierarchy(self, object_definition):

        parentObject = MetaObject(id=object_definition.GlobalId, name=object_definition.Name,
                                  type=object_definition.is_a(), parent=None)

        if str(object_definition.is_a()) != "IfcProject":
            self.metaObjects.append(parentObject)

        spatialElement = self.ifcfile.by_type("IfcSpatialStructureElement")

        for element in spatialElement:
            for cE in element.ContainsElements:
                for rE in cE.RelatedElements:
                    mo = MetaObject(id=rE.GlobalId, name=rE.Name,
                                    type=rE.is_a(), parent=element.GlobalId)
                    self.metaObjects.append(mo.__dict__)

        # if hasattr(object_definition, 'IsDecomposedBy'):
        #     relatedObjects = object_definition.IsDecomposedBy
        #     for rO in relatedObjects:
        #         children = self.extract_hierarchy(rO)
        #         self.metaObjects.append(children)
        #         # pprint(item.get_info(recursive=True))

        return list(self.metaObjects)

    def to_json(self):
        metaObjects = self.extract_hierarchy(self.project)
        self.metaModel.meta_objects = metaObjects
        f = open('metaModel.json', 'w')
        stored_info = jsonpickle.encode(self.metaModel.__dict__)
        f.write(stored_info)
        return self.metaModel


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process')
    parser.add_argument('--ifc_filename', metavar='ifc', help='ifc_filename')

    args = parser.parse_args()
    ifc_filename = args.ifc_filename

    projet = IfcParse(ifc_filename=ifc_filename)
    projet.to_json()
