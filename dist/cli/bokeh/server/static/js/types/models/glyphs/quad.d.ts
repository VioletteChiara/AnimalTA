import { Box, BoxView, BoxData } from "./box";
import { FloatArray, ScreenArray } from "../../core/types";
import * as p from "../../core/properties";
export declare type QuadData = BoxData & {
    _right: FloatArray;
    _bottom: FloatArray;
    _left: FloatArray;
    _top: FloatArray;
    sright: ScreenArray;
    sbottom: ScreenArray;
    sleft: ScreenArray;
    stop: ScreenArray;
};
export interface QuadView extends QuadData {
}
export declare class QuadView extends BoxView {
    model: Quad;
    visuals: Quad.Visuals;
    scenterxy(i: number): [number, number];
    protected _lrtb(i: number): [number, number, number, number];
}
export declare namespace Quad {
    type Attrs = p.AttrsOf<Props>;
    type Props = Box.Props & {
        right: p.CoordinateSpec;
        bottom: p.CoordinateSpec;
        left: p.CoordinateSpec;
        top: p.CoordinateSpec;
    };
    type Visuals = Box.Visuals;
}
export interface Quad extends Quad.Attrs {
}
export declare class Quad extends Box {
    properties: Quad.Props;
    __view_type__: QuadView;
    constructor(attrs?: Partial<Quad.Attrs>);
}
//# sourceMappingURL=quad.d.ts.map