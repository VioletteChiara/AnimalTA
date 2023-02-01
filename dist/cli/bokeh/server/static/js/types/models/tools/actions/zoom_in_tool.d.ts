import { ZoomBaseTool, ZoomBaseToolView } from "./zoom_base_tool";
export declare class ZoomInToolView extends ZoomBaseToolView {
    model: ZoomBaseTool;
}
export interface ZoomInTool extends ZoomBaseTool.Attrs {
}
export declare class ZoomInTool extends ZoomBaseTool {
    properties: ZoomBaseTool.Props;
    __view_type__: ZoomBaseToolView;
    constructor(attrs?: Partial<ZoomBaseTool.Attrs>);
    sign: 1;
    tool_name: string;
    icon: string;
}
//# sourceMappingURL=zoom_in_tool.d.ts.map