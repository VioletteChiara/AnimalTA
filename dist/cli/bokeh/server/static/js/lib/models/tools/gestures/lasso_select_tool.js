var _a;
import { SelectTool, SelectToolView } from "./select_tool";
import { PolyAnnotation } from "../../annotations/poly_annotation";
import { DEFAULT_POLY_OVERLAY } from "./poly_select_tool";
import { Keys } from "../../../core/dom";
import { tool_icon_lasso_select } from "../../../styles/icons.css";
export class LassoSelectToolView extends SelectToolView {
    constructor() {
        super(...arguments);
        this.sxs = [];
        this.sys = [];
    }
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.properties.active.change, () => this._active_change());
    }
    _active_change() {
        if (!this.model.active)
            this._clear_overlay();
    }
    _keyup(ev) {
        if (ev.keyCode == Keys.Enter)
            this._clear_overlay();
    }
    _pan_start(ev) {
        this.sxs = [];
        this.sys = [];
        const { sx, sy } = ev;
        this._append_overlay(sx, sy);
    }
    _pan(ev) {
        const [sx, sy] = this.plot_view.frame.bbox.clip(ev.sx, ev.sy);
        this._append_overlay(sx, sy);
        if (this.model.select_every_mousemove) {
            this._do_select(this.sxs, this.sys, false, this._select_mode(ev));
        }
    }
    _pan_end(ev) {
        const { sxs, sys } = this;
        this._clear_overlay();
        this._do_select(sxs, sys, true, this._select_mode(ev));
        this.plot_view.state.push("lasso_select", { selection: this.plot_view.get_selection() });
    }
    _append_overlay(sx, sy) {
        const { sxs, sys } = this;
        sxs.push(sx);
        sys.push(sy);
        this.model.overlay.update({ xs: sxs, ys: sys });
    }
    _clear_overlay() {
        this.sxs = [];
        this.sys = [];
        this.model.overlay.update({ xs: this.sxs, ys: this.sys });
    }
    _do_select(sx, sy, final, mode) {
        const geometry = { type: "poly", sx, sy };
        this._select(geometry, final, mode);
    }
}
LassoSelectToolView.__name__ = "LassoSelectToolView";
export class LassoSelectTool extends SelectTool {
    constructor(attrs) {
        super(attrs);
        this.tool_name = "Lasso Select";
        this.icon = tool_icon_lasso_select;
        this.event_type = "pan";
        this.default_order = 12;
    }
}
_a = LassoSelectTool;
LassoSelectTool.__name__ = "LassoSelectTool";
(() => {
    _a.prototype.default_view = LassoSelectToolView;
    _a.define(({ Boolean, Ref }) => ({
        select_every_mousemove: [Boolean, true],
        overlay: [Ref(PolyAnnotation), DEFAULT_POLY_OVERLAY],
    }));
    _a.register_alias("lasso_select", () => new LassoSelectTool());
})();
//# sourceMappingURL=lasso_select_tool.js.map