"""eid

Examples:

<tree_id>.<branch_id>:<leaf_id>.<attribute_id>
tree_1.branch_1:gps.latitude

#earth:climate.temperature

"""


def eid2eid(eid):
    """Pad if needed. Returns <SRC_ADDR>:<leaf_id>.<attribute_id>"""
    if ":" not in eid:
        from eventbus.event import get_src_addr

        return f"{get_src_addr()}:{eid}"
    return eid


def eid2lid(eid):
    """<addr>:<leaf_id>"""
    return eid.rsplit(".", 1)[0]


def eid2addr(eid):
    """<addr>"""
    return eid.split(":")[0]
