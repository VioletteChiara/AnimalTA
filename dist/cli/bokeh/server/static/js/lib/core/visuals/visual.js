export class VisualProperties {
    constructor(obj, prefix = "") {
        this.obj = obj;
        this.prefix = prefix;
        const self = this;
        this._props = [];
        for (const attr of this.attrs) {
            const prop = obj.model.properties[prefix + attr];
            prop.change.connect(() => this.update());
            self[attr] = prop;
            this._props.push(prop);
        }
    }
    *[Symbol.iterator]() {
        yield* this._props;
    }
    update() { }
}
VisualProperties.__name__ = "VisualProperties";
export class VisualUniforms {
    constructor(obj, prefix = "") {
        this.obj = obj;
        this.prefix = prefix;
        for (const attr of this.attrs) {
            Object.defineProperty(this, attr, {
                get() {
                    return obj[prefix + attr];
                },
            });
        }
    }
    *[Symbol.iterator]() {
        for (const attr of this.attrs) {
            yield this.obj.model.properties[this.prefix + attr];
        }
    }
    update() { }
}
VisualUniforms.__name__ = "VisualUniforms";
//# sourceMappingURL=visual.js.map