var _a;
import { InspectTool, InspectToolView } from "./inspect_tool";
import { Span } from "../../annotations/span";
import { Dimensions } from "../../../core/enums";
import { values } from "../../../core/util/object";
import { tool_icon_crosshair } from "../../../styles/icons.css";
export class CrosshairToolView extends InspectToolView {
    _move(ev) {
        if (!this.model.active)
            return;
        const { sx, sy } = ev;
        if (!this.plot_view.frame.bbox.contains(sx, sy))
            this._update_spans(null, null);
        else
            this._update_spans(sx, sy);
    }
    _move_exit(_e) {
        this._update_spans(null, null);
    }
    _update_spans(x, y) {
        const dims = this.model.dimensions;
        if (dims == "width" || dims == "both")
            this.model.spans.width.location = y;
        if (dims == "height" || dims == "both")
            this.model.spans.height.location = x;
    }
}
CrosshairToolView.__name__ = "CrosshairToolView";
export class CrosshairTool extends InspectTool {
    constructor(attrs) {
        super(attrs);
        this.tool_name = "Crosshair";
        this.icon = tool_icon_crosshair;
    }
    get tooltip() {
        return this._get_dim_tooltip(this.dimensions);
    }
    get synthetic_renderers() {
        return values(this.spans);
    }
}
_a = CrosshairTool;
CrosshairTool.__name__ = "CrosshairTool";
(() => {
    _a.prototype.default_view = CrosshairToolView;
    _a.define(({ Alpha, Number, Color }) => ({
        dimensions: [Dimensions, "both"],
        line_color: [Color, "black"],
        line_width: [Number, 1],
        line_alpha: [Alpha, 1],
    }));
    function span(self, dimension) {
        return new Span({
            for_hover: true,
            dimension,
            location_units: "screen",
            level: "overlay",
            line_color: self.line_color,
            line_width: self.line_width,
            line_alpha: self.line_alpha,
        });
    }
    _a.internal(({ Struct, Ref }) => ({
        spans: [
            Struct({ width: Ref(Span), height: Ref(Span) }),
            (self) => ({
                width: span(self, "width"),
                height: span(self, "height"),
            }),
        ],
    }));
    _a.register_alias("crosshair", () => new CrosshairTool());
})();
//# sourceMappingURL=crosshair_tool.js.map