var _a;
import { ZoomBaseTool, ZoomBaseToolView } from "./zoom_base_tool";
import { tool_icon_zoom_in } from "../../../styles/icons.css";
export class ZoomInToolView extends ZoomBaseToolView {
}
ZoomInToolView.__name__ = "ZoomInToolView";
export class ZoomInTool extends ZoomBaseTool {
    constructor(attrs) {
        super(attrs);
        this.sign = 1;
        this.tool_name = "Zoom In";
        this.icon = tool_icon_zoom_in;
    }
}
_a = ZoomInTool;
ZoomInTool.__name__ = "ZoomInTool";
(() => {
    _a.prototype.default_view = ZoomInToolView;
    _a.register_alias("zoom_in", () => new ZoomInTool({ dimensions: "both" }));
    _a.register_alias("xzoom_in", () => new ZoomInTool({ dimensions: "width" }));
    _a.register_alias("yzoom_in", () => new ZoomInTool({ dimensions: "height" }));
})();
//# sourceMappingURL=zoom_in_tool.js.map