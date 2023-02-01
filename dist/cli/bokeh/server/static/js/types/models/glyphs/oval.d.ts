import { EllipseOval, EllipseOvalView, EllipseOvalData } from "./ellipse_oval";
import * as p from "../../core/properties";
export declare type OvalData = EllipseOvalData;
export interface OvalView extends OvalData {
}
export declare class OvalView extends EllipseOvalView {
    model: Oval;
    visuals: Oval.Visuals;
    protected _map_data(): void;
}
export declare namespace Oval {
    type Attrs = p.AttrsOf<Props>;
    type Props = EllipseOval.Props;
    type Visuals = EllipseOval.Visuals;
}
export interface Oval extends Oval.Attrs {
}
export declare class Oval extends EllipseOval {
    properties: Oval.Props;
    __view_type__: OvalView;
    constructor(attrs?: Partial<Oval.Attrs>);
}
//# sourceMappingURL=oval.d.ts.map