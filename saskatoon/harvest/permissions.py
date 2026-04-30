from member.models import Role

ModelName = str
Action = str
Permissions = dict[ModelName, dict[Action, set[Role]]]

CORE = Role.CORE
PICKLEADER = Role.PICKLEADER

PERMISSIONS: Permissions = {  # pytype: disable=annotation-type-mismatch
    "harvest": {
        "add":    {CORE, PICKLEADER},
        "change": {CORE, PICKLEADER},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "property": {
        "add":    {CORE},
        "change": {CORE, PICKLEADER},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "requestforparticipation": {
        "add":    {CORE, PICKLEADER},
        "change": {CORE, PICKLEADER},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "harvestyield": {
        "add":    {CORE, PICKLEADER},
        "change": {CORE, PICKLEADER},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE, PICKLEADER},
    },
    "comment": {
        "add":    {CORE, PICKLEADER},
        "change": {CORE, PICKLEADER},
        "view":   {CORE, PICKLEADER},
        "delete": set(),
    },
    "equipment": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "treetype": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "equipmenttype": {
        "add":    {CORE},
        "change": {CORE},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "propertyimage": {
        "add":    {CORE, PICKLEADER},
        "change": {CORE, PICKLEADER},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
    "harvestimage": {
        "add":    {CORE, PICKLEADER},
        "change": {CORE, PICKLEADER},
        "view":   {CORE, PICKLEADER},
        "delete": {CORE},
    },
}
