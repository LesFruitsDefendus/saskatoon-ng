from member.models import Role

ModelName = str
Action = str
Permissions = dict[ModelName, dict[Action, set[Role]]]

PERMISSIONS: Permissions = {
    "pagecontent": {
        "add":    set(),
        "change": set(),
        "delete": set(),
    },
    "faqitem": {
        "add":    set(),
        "change": set(),
        "delete": set(),
    },
    "faqlist": {
        "add":    set(),
        "change": set(),
        "delete": set(),
    },
    "emailcontent": {
        "add":    set(),
        "change": set(),
        "delete": set(),
    },
    "email": {
        "add":    set(),
        "change": set(),
        "delete": set(),
    },
}
