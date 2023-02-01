import { XYGlyph, XYGlyphView, XYGlyphData } from "./xy_glyph";
import { Arrayable, ScreenArray } from "../../core/types";
import * as p from "../../core/properties";
import { Context2d } from "../../core/util/canvas";
import { Selection, ImageIndex } from "../selections/selection";
import { PointGeometry } from "../../core/geometry";
import { SpatialIndex } from "../../core/util/spatial";
import { NDArray } from "../../core/util/ndarray";
export declare type ImageDataBase = XYGlyphData & {
    image_data: HTMLCanvasElement[];
    readonly image: p.Uniform<NDArray | number[][]>;
    readonly dw: p.Uniform<number>;
    readonly dh: p.Uniform<number>;
    readonly global_alpha: p.Uniform<number>;
    sw: ScreenArray;
    sh: ScreenArray;
};
export interface ImageBaseView extends ImageDataBase {
}
export declare abstract class ImageBaseView extends XYGlyphView {
    model: ImageBase;
    visuals: ImageBase.Visuals;
    protected _width: Uint32Array;
    protected _height: Uint32Array;
    connect_signals(): void;
    protected _render(ctx: Context2d, indices: number[], data?: ImageDataBase): void;
    protected abstract _flat_img_to_buf8(img: Arrayable<number>): Uint8ClampedArray;
    protected _set_data(indices: number[] | null): void;
    protected _index_data(index: SpatialIndex): void;
    _lrtb(i: number): [number, number, number, number];
    protected _set_width_heigh_data(): void;
    protected _get_or_create_canvas(i: number): HTMLCanvasElement;
    protected _set_image_data_from_buffer(i: number, buf8: Uint8ClampedArray): void;
    protected _map_data(): void;
    _image_index(index: number, x: number, y: number): ImageIndex;
    _hit_point(geometry: PointGeometry): Selection;
}
export declare namespace ImageBase {
    type Attrs = p.AttrsOf<Props>;
    type Props = XYGlyph.Props & {
        image: p.NDArraySpec;
        dw: p.DistanceSpec;
        dh: p.DistanceSpec;
        global_alpha: p.NumberSpec;
        dilate: p.Property<boolean>;
    };
    type Visuals = XYGlyph.Visuals;
}
export interface ImageBase extends ImageBase.Attrs {
}
export declare abstract class ImageBase extends XYGlyph {
    properties: ImageBase.Props;
    __view_type__: ImageBaseView;
    constructor(attrs?: Partial<ImageBase.Attrs>);
}
//# sourceMappingURL=image_base.d.ts.map