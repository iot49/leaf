from . import src_addr

"""eid

Examples:

<tree_id>:<branch_id>:<leaf_id>:<attribute_id>

"""


def eid2eid(eid):
    """Pad if needed. Returns <tree_id>:<branch_id>:<leaf_id>:<attribute_id>"""
    if eid.count(":") < 2:
        tb = "earth:server" if src_addr == "#earth" else src_addr
        return f"{tb}:{eid}"
    return eid


def eid2lid(eid):
    """<tree_id>:<branch_id>:<leaf_id>"""
    return ":".join(eid.split(":")[:3])


def eid2addr(eid):
    """<tree_id>:<branch_id>"""
    return ":".join(eid.split(":")[:2])
