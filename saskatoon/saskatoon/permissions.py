from harvest import permissions as harvest
from member import permissions as member
from sitebase import permissions as sitebase

ALL_PERMISSIONS = {
    "harvest": harvest.PERMISSIONS,
    "member": member.PERMISSIONS,
    "sitebase": sitebase.PERMISSIONS,
}
