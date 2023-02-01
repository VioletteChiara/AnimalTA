import { BaseGLGlyph, Transform } from "./base";
import { LineView } from "../line";
import { ReglWrapper } from "./regl_wrap";
import { Texture2D } from "regl";
import { Float32Buffer } from "./buffer";
export declare class LineGL extends BaseGLGlyph {
    readonly glyph: LineView;
    protected _nsegments: number;
    protected _points: Float32Buffer;
    protected _antialias: number;
    protected _color: number[];
    protected _linewidth: number;
    protected _miter_limit: number;
    protected _line_dash: number[];
    protected _is_closed: boolean;
    protected _length_so_far?: Float32Buffer;
    protected _dash_tex?: Texture2D;
    protected _dash_tex_info?: number[];
    protected _dash_scale?: number;
    protected _dash_offset?: number;
    constructor(regl_wrapper: ReglWrapper, glyph: LineView);
    draw(_indices: number[], mainGlyph: LineView, transform: Transform): void;
    protected _is_dashed(): boolean;
    protected _set_data(): void;
    protected _set_visuals(): void;
}
//# sourceMappingURL=line_gl.d.ts.map