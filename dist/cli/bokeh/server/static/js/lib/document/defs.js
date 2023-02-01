import { Model } from "../model";
import * as kinds from "../core/kinds";
import { isString } from "../core/util/types";
import { to_object } from "../core/util/object";
export function resolve_defs(defs, resolver) {
    var _a;
    function qualified(ref) {
        return ref.module != null ? `${ref.module}.${ref.name}` : ref.name;
    }
    function kind_of(ref) {
        if (isString(ref)) {
            switch (ref) {
                case "Any": return kinds.Any;
                case "Unknown": return kinds.Unknown;
                case "Boolean": return kinds.Boolean;
                case "Number": return kinds.Number;
                case "Int": return kinds.Int;
                case "String": return kinds.String;
                case "Null": return kinds.Null;
            }
        }
        else {
            switch (ref[0]) {
                case "Nullable": {
                    const [, subref] = ref;
                    return kinds.Nullable(kind_of(subref));
                }
                case "Or": {
                    const [, ...subrefs] = ref;
                    return kinds.Or(...subrefs.map(kind_of));
                }
                case "Tuple": {
                    const [, subref, ...subrefs] = ref;
                    return kinds.Tuple(kind_of(subref), ...subrefs.map(kind_of));
                }
                case "Array": {
                    const [, subref] = ref;
                    return kinds.Array(kind_of(subref));
                }
                case "Struct": {
                    const [, ...entryrefs] = ref;
                    const entries = entryrefs.map(([key, valref]) => [key, kind_of(valref)]);
                    return kinds.Struct(to_object(entries));
                }
                case "Dict": {
                    const [, valref] = ref;
                    return kinds.Dict(kind_of(valref));
                }
                case "Map": {
                    const [, keyref, valref] = ref;
                    return kinds.Map(kind_of(keyref), kind_of(valref));
                }
                case "Enum": {
                    const [, ...items] = ref;
                    return kinds.Enum(...items);
                }
                case "Ref": {
                    const [, modelref] = ref;
                    const model = resolver.get(qualified(modelref));
                    if (model != null)
                        return kinds.Ref(model);
                    else
                        throw new Error(`${qualified(modelref)} wasn't defined before referencing it`);
                }
                case "AnyRef": {
                    return kinds.AnyRef();
                }
            }
        }
    }
    for (const def of defs) {
        const base = (() => {
            if (def.extends == null)
                return Model;
            else {
                const base = resolver.get(qualified(def.extends));
                if (base != null)
                    return base;
                else
                    throw new Error(`base model ${qualified(def.extends)} of ${qualified(def)} is not defined`);
            }
        })();
        const model = (_a = class extends base {
            },
            _a.__name__ = def.name,
            _a.__module__ = def.module,
            _a);
        for (const prop of def.properties ?? []) {
            const kind = kind_of(prop.kind ?? "Unknown");
            model.define({ [prop.name]: [kind, prop.default] });
        }
        for (const prop of def.overrides ?? []) {
            model.override({ [prop.name]: prop.default });
        }
        resolver.register(model);
    }
}
//# sourceMappingURL=defs.js.map