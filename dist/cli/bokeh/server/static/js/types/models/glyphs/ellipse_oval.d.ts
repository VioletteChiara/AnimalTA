import { CenterRotatable, CenterRotatableView, CenterRotatableData } from "./center_rotatable";
import { PointGeometry } from "../../core/geometry";
import { Rect } from "../../core/types";
import { Context2d } from "../../core/util/canvas";
import { Selection } from "../selections/selection";
import * as p from "../../core/properties";
export declare type EllipseOvalData = CenterRotatableData;
export interface EllipseOvalView extends EllipseOvalData {
}
export declare abstract class EllipseOvalView extends CenterRotatableView {
    model: EllipseOval;
    visuals: EllipseOval.Visuals;
    protected _map_data(): void;
    protected _render(ctx: Context2d, indices: number[], data?: EllipseOvalData): void;
    protected _hit_point(geometry: PointGeometry): Selection;
    draw_legend_for_index(ctx: Context2d, { x0, y0, x1, y1 }: Rect, index: number): void;
}
export declare namespace EllipseOval {
    type Attrs = p.AttrsOf<Props>;
    type Props = CenterRotatable.Props;
    type Visuals = CenterRotatable.Visuals;
}
export interface EllipseOval extends EllipseOval.Attrs {
}
export declare abstract class EllipseOval extends CenterRotatable {
    properties: EllipseOval.Props;
    __view_type__: EllipseOvalView;
    constructor(attrs?: Partial<EllipseOval.Attrs>);
}
//# sourceMappingURL=ellipse_oval.d.ts.map