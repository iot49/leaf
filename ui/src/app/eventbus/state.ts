export type State = Map<string, any>;

function wildcard_match(str, rule) {
  /* fnmatch *-only implementation

    Examples:
        wildcard_match("hello.world", "hello.*") -> true
        wildcard_match("hello.world", "Hello*") -> false
  */
  if (!rule.includes(".")) rule = "*." + rule;
  var escapeRegex = (str) => str.replace(/([.*+?^=!:${}()|\[\]\/\\])/g, "\\$1");
  return new RegExp(
    "^" + rule.split("*").map(escapeRegex).join(".*") + "$",
  ).test(str);
}

function did(eid) {
  /* Get device id from eid

    Examples:
        did("#earth.counter.count") -> "#earth.counter"
        did("tree_id.branch_id.light.living_room") -> "tree_id.branch_id.light"
   */
  const cfg = globalThis.leaf.config;
  const d = eid.substring(0, eid.lastIndexOf(":")); // split off attribute_id
  if (d in (cfg.devices || {})) return d;
  for (const [k, v] of Object.entries(cfg.devices || {})) {
    if ((v as any).alias == d) return k;
  }
  return d;
}

function entity_name(eid) {
  /* Look up entity name in configuration */
  // check entities.yaml
  const cfg = globalThis.leaf.config;
  const n = attr(eid, "name");
  if (n) return n;

  // check devices.yaml
  try {
    const n = cfg.devices[this.device_id(cfg, eid)].name;
    if (n) return n;
  } catch {}

  // default: entity name capitalized
  const a = eid.substring(eid.lastIndexOf(":") + 1);
  return a.charAt(0).toUpperCase() + a.slice(1);
}

function attr(eid, attribute) {
  const cfg = globalThis.leaf.config;
  for (const [pattern, fields] of Object.entries(cfg.entities || {})) {
    if (wildcard_match(eid, pattern)) {
      try {
        const a = fields[attribute];
        if (a) return a;
      } catch {}
    }
  }
  return undefined;
}

export function sort_state(state: State): State {
  const sortStringValues = ([, a], [, b]) =>
    String(a.name).localeCompare(b.name);
  return new Map([...state].sort(sortStringValues));
}

export const state_handler = {
  get(target, prop, _) {
    /* get_attr for states */
    const eid = target.eid;
    switch (prop) {
      case "eid":
        return eid;
      case "did":
        return did(eid);
      case "name":
        return entity_name(eid);
      case "value":
        return target.value;
      case "timestamp":
        return target.timestamp;
      default:
        return attr(eid, prop); // unit, format, icon, ...
    }
  },
};
