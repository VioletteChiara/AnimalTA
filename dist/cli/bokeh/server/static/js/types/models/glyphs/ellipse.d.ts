import { EllipseOval, EllipseOvalView, EllipseOvalData } from "./ellipse_oval";
import * as p from "../../core/properties";
export declare type EllipseData = EllipseOvalData;
export interface EllipseView extends EllipseData {
}
export declare class EllipseView extends EllipseOvalView {
    model: Ellipse;
    visuals: Ellipse.Visuals;
}
export declare namespace Ellipse {
    type Attrs = p.AttrsOf<Props>;
    type Props = EllipseOval.Props;
    type Visuals = EllipseOval.Visuals;
}
export interface Ellipse extends Ellipse.Attrs {
}
export declare class Ellipse extends EllipseOval {
    properties: Ellipse.Props;
    __view_type__: EllipseView;
    constructor(attrs?: Partial<Ellipse.Attrs>);
}
//# sourceMappingURL=ellipse.d.ts.map