import { ZoomBaseTool, ZoomBaseToolView } from "./zoom_base_tool";
import * as p from "../../../core/properties";
export declare class ZoomOutToolView extends ZoomBaseToolView {
    model: ZoomBaseTool;
}
export declare namespace ZoomOutTool {
    type Attrs = p.AttrsOf<Props>;
    type Props = ZoomBaseTool.Props & {
        maintain_focus: p.Property<boolean>;
    };
}
export interface ZoomOutTool extends ZoomBaseTool.Attrs {
}
export declare class ZoomOutTool extends ZoomBaseTool {
    properties: ZoomOutTool.Props;
    __view_type__: ZoomBaseToolView;
    constructor(attrs?: Partial<ZoomBaseTool.Attrs>);
    sign: -1;
    tool_name: string;
    icon: string;
}
//# sourceMappingURL=zoom_out_tool.d.ts.map