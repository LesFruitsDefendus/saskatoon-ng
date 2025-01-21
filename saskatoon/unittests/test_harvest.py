import pytest
from utilities import create_tree_type, TreeType, create_property, Property, create_harvest, Harvest


@pytest.fixture
def tree_apple(db) -> TreeType:
    return create_tree_type(name="apple", fruit_name="apple")


@pytest.fixture
def tree_pear(db) -> TreeType:
    return create_tree_type(name="pear", fruit_name="pear")


@pytest.fixture
def property_with_apple_pear(db, tree_apple: TreeType, tree_pear: TreeType) -> Property:
    return create_property(trees=[tree_apple, tree_pear])


@pytest.fixture
def harvest_apple(db, property_with_apple_pear: Property, tree_apple: TreeType) -> Harvest:
    return create_harvest(harvest_property=property_with_apple_pear, harvest_trees=[tree_apple])


def test_create_tree_type_apple(tree_apple: TreeType) -> None:
    assert tree_apple.name == "apple"


def test_create_property_with_2_tree_types(property_with_apple_pear: Property) -> None:
    trees = property_with_apple_pear.trees
    assert trees.count() == 2


def test_create_harvest_apple(harvest_apple: Harvest, tree_apple: TreeType) -> None:
    assert harvest_apple.trees.filter(pk=tree_apple.pk).exists()
    assert harvest_apple.property.trees.filter(pk=tree_apple.pk).exists()
