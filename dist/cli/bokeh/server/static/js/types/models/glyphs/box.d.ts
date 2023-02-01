import { LineVector, FillVector, HatchVector } from "../../core/property_mixins";
import { Rect, FloatArray, ScreenArray } from "../../core/types";
import { Anchor } from "../../core/enums";
import * as visuals from "../../core/visuals";
import { SpatialIndex } from "../../core/util/spatial";
import { Context2d } from "../../core/util/canvas";
import { Glyph, GlyphView, GlyphData } from "./glyph";
import { PointGeometry, SpanGeometry, RectGeometry } from "../../core/geometry";
import { Selection } from "../selections/selection";
import * as p from "../../core/properties";
export declare type BoxData = GlyphData & p.UniformsOf<Box.Mixins> & {
    _right: FloatArray;
    _bottom: FloatArray;
    _left: FloatArray;
    _top: FloatArray;
    sright: ScreenArray;
    sbottom: ScreenArray;
    sleft: ScreenArray;
    stop: ScreenArray;
};
export interface BoxView extends BoxData {
}
export declare abstract class BoxView extends GlyphView {
    model: Box;
    visuals: Box.Visuals;
    get_anchor_point(anchor: Anchor, i: number, _spt: [number, number]): {
        x: number;
        y: number;
    } | null;
    protected abstract _lrtb(i: number): [number, number, number, number];
    protected _index_data(index: SpatialIndex): void;
    protected _render(ctx: Context2d, indices: number[], data?: BoxData): void;
    protected _clamp_viewport(): void;
    protected _hit_rect(geometry: RectGeometry): Selection;
    protected _hit_point(geometry: PointGeometry): Selection;
    protected _hit_span(geometry: SpanGeometry): Selection;
    draw_legend_for_index(ctx: Context2d, bbox: Rect, index: number): void;
}
export declare namespace Box {
    type Attrs = p.AttrsOf<Props>;
    type Props = Glyph.Props & Mixins;
    type Mixins = LineVector & FillVector & HatchVector;
    type Visuals = Glyph.Visuals & {
        line: visuals.LineVector;
        fill: visuals.FillVector;
        hatch: visuals.HatchVector;
    };
}
export interface Box extends Box.Attrs {
}
export declare abstract class Box extends Glyph {
    properties: Box.Props;
    __view_type__: BoxView;
    constructor(attrs?: Partial<Box.Attrs>);
}
//# sourceMappingURL=box.d.ts.map