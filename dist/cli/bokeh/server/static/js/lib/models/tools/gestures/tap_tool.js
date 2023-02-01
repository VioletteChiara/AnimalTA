var _a;
import { SelectTool, SelectToolView } from "./select_tool";
import { TapBehavior } from "../../../core/enums";
import { tool_icon_tap_select } from "../../../styles/icons.css";
export class TapToolView extends SelectToolView {
    _tap(ev) {
        if (this.model.gesture == "tap")
            this._handle_tap(ev);
    }
    _doubletap(ev) {
        if (this.model.gesture == "doubletap")
            this._handle_tap(ev);
    }
    _handle_tap(ev) {
        const { sx, sy } = ev;
        const geometry = { type: "point", sx, sy };
        this._select(geometry, true, this._select_mode(ev));
    }
    _select(geometry, final, mode) {
        const { callback } = this.model;
        if (this.model.behavior == "select") {
            const renderers_by_source = this._computed_renderers_by_data_source();
            for (const [, renderers] of renderers_by_source) {
                const sm = renderers[0].get_selection_manager();
                const r_views = renderers
                    .map((r) => this.plot_view.renderer_view(r))
                    .filter((rv) => rv != null);
                const did_hit = sm.select(r_views, geometry, final, mode);
                if (did_hit && callback != null) {
                    const x = r_views[0].coordinates.x_scale.invert(geometry.sx);
                    const y = r_views[0].coordinates.y_scale.invert(geometry.sy);
                    const data = { geometries: { ...geometry, x, y }, source: sm.source };
                    callback.execute(this.model, data);
                }
            }
            this._emit_selection_event(geometry);
            this.plot_view.state.push("tap", { selection: this.plot_view.get_selection() });
        }
        else {
            for (const r of this.computed_renderers) {
                const rv = this.plot_view.renderer_view(r);
                if (rv == null)
                    continue;
                const sm = r.get_selection_manager();
                const did_hit = sm.inspect(rv, geometry);
                if (did_hit && callback != null) {
                    const x = rv.coordinates.x_scale.invert(geometry.sx);
                    const y = rv.coordinates.y_scale.invert(geometry.sy);
                    const data = { geometries: { ...geometry, x, y }, source: sm.source };
                    callback.execute(this.model, data);
                }
            }
        }
    }
}
TapToolView.__name__ = "TapToolView";
export class TapTool extends SelectTool {
    constructor(attrs) {
        super(attrs);
        this.tool_name = "Tap";
        this.icon = tool_icon_tap_select;
        this.event_type = "tap";
        this.default_order = 10;
    }
}
_a = TapTool;
TapTool.__name__ = "TapTool";
(() => {
    _a.prototype.default_view = TapToolView;
    _a.define(({ Any, Enum, Nullable }) => ({
        behavior: [TapBehavior, "select"],
        gesture: [Enum("tap", "doubletap"), "tap"],
        callback: [Nullable(Any /*TODO*/)],
    }));
    _a.register_alias("click", () => new TapTool({ behavior: "inspect" }));
    _a.register_alias("tap", () => new TapTool());
    _a.register_alias("doubletap", () => new TapTool({ gesture: "doubletap" }));
})();
//# sourceMappingURL=tap_tool.js.map