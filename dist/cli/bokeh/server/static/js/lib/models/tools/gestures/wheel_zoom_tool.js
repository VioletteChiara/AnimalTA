var _a;
import { GestureTool, GestureToolView } from "./gesture_tool";
import { scale_range } from "../../../core/util/zoom";
import { Dimensions } from "../../../core/enums";
import { is_mobile } from "../../../core/util/platform";
import { tool_icon_wheel_zoom } from "../../../styles/icons.css";
export class WheelZoomToolView extends GestureToolView {
    _pinch(ev) {
        // TODO (bev) this can probably be done much better
        const { sx, sy, scale, ctrlKey, shiftKey } = ev;
        let delta;
        if (scale >= 1)
            delta = (scale - 1) * 20.0;
        else
            delta = -20.0 / scale;
        this._scroll({ type: "wheel", sx, sy, delta, ctrlKey, shiftKey });
    }
    _scroll(ev) {
        const { frame } = this.plot_view;
        const hr = frame.bbox.h_range;
        const vr = frame.bbox.v_range;
        const { sx, sy } = ev;
        const dims = this.model.dimensions;
        // restrict to axis configured in tool's dimensions property and if
        // zoom origin is inside of frame range/domain
        const h_axis = (dims == "width" || dims == "both") && hr.start < sx && sx < hr.end;
        const v_axis = (dims == "height" || dims == "both") && vr.start < sy && sy < vr.end;
        if ((!h_axis || !v_axis) && !this.model.zoom_on_axis) {
            return;
        }
        const factor = this.model.speed * ev.delta;
        const zoom_info = scale_range(frame, factor, h_axis, v_axis, { x: sx, y: sy });
        this.plot_view.state.push("wheel_zoom", { range: zoom_info });
        const { maintain_focus } = this.model;
        this.plot_view.update_range(zoom_info, { scrolling: true, maintain_focus });
        this.model.document?.interactive_start(this.plot_model, () => this.plot_view.trigger_ranges_update_event());
    }
}
WheelZoomToolView.__name__ = "WheelZoomToolView";
export class WheelZoomTool extends GestureTool {
    constructor(attrs) {
        super(attrs);
        this.tool_name = "Wheel Zoom";
        this.icon = tool_icon_wheel_zoom;
        this.event_type = is_mobile ? "pinch" : "scroll";
        this.default_order = 10;
    }
    get tooltip() {
        return this._get_dim_tooltip(this.dimensions);
    }
}
_a = WheelZoomTool;
WheelZoomTool.__name__ = "WheelZoomTool";
(() => {
    _a.prototype.default_view = WheelZoomToolView;
    _a.define(({ Boolean, Number }) => ({
        dimensions: [Dimensions, "both"],
        maintain_focus: [Boolean, true],
        zoom_on_axis: [Boolean, true],
        speed: [Number, 1 / 600],
    }));
    _a.register_alias("wheel_zoom", () => new WheelZoomTool({ dimensions: "both" }));
    _a.register_alias("xwheel_zoom", () => new WheelZoomTool({ dimensions: "width" }));
    _a.register_alias("ywheel_zoom", () => new WheelZoomTool({ dimensions: "height" }));
})();
//# sourceMappingURL=wheel_zoom_tool.js.map