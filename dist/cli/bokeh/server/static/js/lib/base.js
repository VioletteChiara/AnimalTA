import { isObject, isArray } from "./core/util/types";
import { values } from "./core/util/object";
import { HasProps } from "./core/has_props";
export const overrides = {};
const _all_models = new Map();
export const Models = ((name) => {
    const model = Models.get(name);
    if (model != null)
        return model;
    else
        throw new Error(`Model '${name}' does not exist. This could be due to a widget or a custom model not being registered before first usage.`);
});
Models.get = (name) => {
    return overrides[name] ?? _all_models.get(name);
};
Models.register = (name, model) => {
    overrides[name] = model;
};
Models.unregister = (name) => {
    delete overrides[name];
};
function is_HasProps(obj) {
    return isObject(obj) && obj.prototype instanceof HasProps;
}
Models.register_models = (models, force = false, errorFn) => {
    if (models == null)
        return;
    for (const model of isArray(models) ? models : values(models)) {
        if (is_HasProps(model)) {
            const qualified = model.__qualified__;
            if (force || !_all_models.has(qualified))
                _all_models.set(qualified, model);
            else if (errorFn != null)
                errorFn(qualified);
            else
                console.warn(`Model '${qualified}' was already registered`);
        }
    }
};
export const register_models = Models.register_models;
Models.registered_names = () => [..._all_models.keys()];
export class ModelResolver {
    constructor() {
        this._known_models = new Map();
    }
    get(name, or_else) {
        const model = Models.get(name) ?? this._known_models.get(name);
        if (model != null)
            return model;
        else if (or_else !== undefined)
            return or_else;
        else
            throw new Error(`Model '${name}' does not exist. This could be due to a widget or a custom model not being registered before first usage.`);
    }
    register(model) {
        const name = model.__qualified__;
        if (this.get(name, null) == null)
            this._known_models.set(name, model);
        else
            console.warn(`Model '${name}' was already registered with this resolver`);
    }
}
ModelResolver.__name__ = "ModelResolver";
// TODO: this doesn't belong here, but it's easier this way for backwards compatibility
import * as AllModels from "./models";
register_models(AllModels);
import * as DOMModels from "./models/dom";
register_models(DOMModels);
//# sourceMappingURL=base.js.map