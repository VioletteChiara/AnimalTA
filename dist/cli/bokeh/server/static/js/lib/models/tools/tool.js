var _a;
import { View } from "../../core/view";
import { min, max } from "../../core/util/array";
import { Model } from "../../model";
export class ToolView extends View {
    get plot_view() {
        return this.parent;
    }
    get plot_model() {
        return this.parent.model;
    }
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.properties.active.change, () => {
            if (this.model.active)
                this.activate();
            else
                this.deactivate();
        });
    }
    // activate is triggered by toolbar ui actions
    activate() { }
    // deactivate is triggered by toolbar ui actions
    deactivate() { }
}
ToolView.__name__ = "ToolView";
export class Tool extends Model {
    constructor(attrs) {
        super(attrs);
    }
    get synthetic_renderers() {
        return [];
    }
    // utility function to get limits along both dimensions, given
    // optional dimensional constraints
    _get_dim_limits([sx0, sy0], [sx1, sy1], frame, dims) {
        const hr = frame.bbox.h_range;
        let sxlim;
        if (dims == "width" || dims == "both") {
            sxlim = [min([sx0, sx1]), max([sx0, sx1])];
            sxlim = [max([sxlim[0], hr.start]), min([sxlim[1], hr.end])];
        }
        else
            sxlim = [hr.start, hr.end];
        const vr = frame.bbox.v_range;
        let sylim;
        if (dims == "height" || dims == "both") {
            sylim = [min([sy0, sy1]), max([sy0, sy1])];
            sylim = [max([sylim[0], vr.start]), min([sylim[1], vr.end])];
        }
        else
            sylim = [vr.start, vr.end];
        return [sxlim, sylim];
    }
    static register_alias(name, fn) {
        this.prototype._known_aliases.set(name, fn);
    }
    static from_string(name) {
        const fn = this.prototype._known_aliases.get(name);
        if (fn != null)
            return fn();
        else {
            const names = [...this.prototype._known_aliases.keys()];
            throw new Error(`unexpected tool name '${name}', possible tools are ${names.join(", ")}`);
        }
    }
}
_a = Tool;
Tool.__name__ = "Tool";
(() => {
    _a.prototype._known_aliases = new Map();
    _a.define(({ String, Nullable }) => ({
        description: [Nullable(String), null],
    }));
    _a.internal(({ Boolean }) => ({
        active: [Boolean, false],
    }));
})();
//# sourceMappingURL=tool.js.map