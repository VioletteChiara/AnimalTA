import { BaseGLGlyph, Transform } from "./base";
import { Float32Buffer, NormalizedUint8Buffer, Uint8Buffer } from "./buffer";
import { ReglWrapper } from "./regl_wrap";
import type { RectView } from "../rect";
export declare class RectGL extends BaseGLGlyph {
    readonly glyph: RectView;
    protected _antialias: number;
    protected _centers: Float32Buffer;
    protected _widths: Float32Buffer;
    protected _heights: Float32Buffer;
    protected _angles: Float32Buffer;
    protected _linewidths: Float32Buffer;
    protected _line_rgba: NormalizedUint8Buffer;
    protected _fill_rgba: NormalizedUint8Buffer;
    protected _line_joins: Uint8Buffer;
    protected _show: Uint8Buffer;
    protected _show_all: boolean;
    protected _have_hatch: boolean;
    protected _hatch_patterns?: Uint8Buffer;
    protected _hatch_scales?: Float32Buffer;
    protected _hatch_weights?: Float32Buffer;
    protected _hatch_rgba?: NormalizedUint8Buffer;
    constructor(regl_wrapper: ReglWrapper, glyph: RectView);
    draw(indices: number[], main_glyph: RectView, transform: Transform): void;
    protected _set_data(): void;
    protected _set_visuals(): void;
}
//# sourceMappingURL=rect.d.ts.map