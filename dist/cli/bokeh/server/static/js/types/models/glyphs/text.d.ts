import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { TextVector } from "../../core/property_mixins";
import { PointGeometry } from "../../core/geometry";
import * as visuals from "../../core/visuals";
import * as p from "../../core/properties";
import { Context2d } from "../../core/util/canvas";
import { Selection } from "../selections/selection";
export declare type TextData = XYGlyphData & p.UniformsOf<Text.Mixins> & {
    readonly text: p.Uniform<string>;
    readonly angle: p.Uniform<number>;
    readonly x_offset: p.Uniform<number>;
    readonly y_offset: p.Uniform<number>;
    _sxs: number[][][];
    _sys: number[][][];
};
export interface TextView extends TextData {
}
export declare class TextView extends XYGlyphView {
    model: Text;
    visuals: Text.Visuals;
    private _rotate_point;
    private _text_bounds;
    protected _render(ctx: Context2d, indices: number[], data?: TextData): void;
    protected _hit_point(geometry: PointGeometry): Selection;
    scenterxy(i: number): [number, number];
}
export declare namespace Text {
    type Attrs = p.AttrsOf<Props>;
    type Props = XYGlyph.Props & {
        text: p.NullStringSpec;
        angle: p.AngleSpec;
        x_offset: p.NumberSpec;
        y_offset: p.NumberSpec;
    } & Mixins;
    type Mixins = TextVector;
    type Visuals = XYGlyph.Visuals & {
        text: visuals.TextVector;
    };
}
export interface Text extends Text.Attrs {
}
export declare class Text extends XYGlyph {
    properties: Text.Props;
    __view_type__: TextView;
    constructor(attrs?: Partial<Text.Attrs>);
}
//# sourceMappingURL=text.d.ts.map