import { BaseGLGlyph, Transform } from "./base";
import { Float32Buffer, NormalizedUint8Buffer, Uint8Buffer } from "./buffer";
import { ReglWrapper } from "./regl_wrap";
import type { ScatterView } from "../scatter";
import type { CircleView } from "../circle";
import { MarkerType } from "../../../core/enums";
declare type MarkerLikeView = ScatterView | CircleView;
export declare class MarkerGL extends BaseGLGlyph {
    readonly glyph: MarkerLikeView;
    readonly marker_type: MarkerType;
    protected _marker_type: MarkerType;
    protected _antialias: number;
    protected _centers: Float32Buffer;
    protected _sizes: Float32Buffer;
    protected _angles: Float32Buffer;
    protected _linewidths: Float32Buffer;
    protected _line_rgba: NormalizedUint8Buffer;
    protected _fill_rgba: NormalizedUint8Buffer;
    protected _show: Uint8Buffer;
    protected _show_all: boolean;
    static is_supported(marker_type: MarkerType): boolean;
    constructor(regl_wrapper: ReglWrapper, glyph: MarkerLikeView, marker_type: MarkerType);
    draw(indices: number[], main_glyph: MarkerLikeView, transform: Transform): void;
    protected _set_data(): void;
    protected _set_visuals(): void;
}
export {};
//# sourceMappingURL=markers.d.ts.map