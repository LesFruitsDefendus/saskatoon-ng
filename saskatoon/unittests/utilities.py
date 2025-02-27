from typing import List
from harvest.models import TreeType, Property, Harvest


def create_tree_type(name: str, fruit_name: str) -> TreeType:
    return TreeType.objects.create(name=name, fruit_name=fruit_name)


def create_property(trees: List[TreeType]) -> Property:
    harvest_property = Property.objects.create()
    for tree in trees:
        harvest_property.trees.add(tree)
    return harvest_property


def create_harvest(harvest_property: Property, harvest_trees: List[TreeType]) -> Harvest:
    harvest = Harvest.objects.create(property=harvest_property)
    for tree in harvest_trees:
        harvest.trees.add(tree)
    return harvest
