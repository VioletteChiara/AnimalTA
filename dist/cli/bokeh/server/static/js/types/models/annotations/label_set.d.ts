import { DataAnnotation, DataAnnotationView } from "./data_annotation";
import { ColumnarDataSource } from "../sources/columnar_data_source";
import * as mixins from "../../core/property_mixins";
import * as visuals from "../../core/visuals";
import { SpatialUnits, RenderMode } from "../../core/enums";
import * as p from "../../core/properties";
import { FloatArray, ScreenArray } from "../../core/types";
import { Context2d } from "../../core/util/canvas";
export declare class LabelSetView extends DataAnnotationView {
    model: LabelSet;
    visuals: LabelSet.Visuals;
    protected _x: FloatArray;
    protected _y: FloatArray;
    protected sx: ScreenArray;
    protected sy: ScreenArray;
    protected text: p.Uniform<string>;
    protected angle: p.Uniform<number>;
    protected x_offset: p.Uniform<number>;
    protected y_offset: p.Uniform<number>;
    protected els?: HTMLElement[];
    set_data(source: ColumnarDataSource): void;
    remove(): void;
    protected _rerender(): void;
    map_data(): void;
    paint(): void;
    protected _v_canvas_text(ctx: Context2d, i: number, text: string, sx: number, sy: number, angle: number): void;
    protected _v_css_text(ctx: Context2d, i: number, text: string, sx: number, sy: number, angle: number): void;
}
export declare namespace LabelSet {
    type Attrs = p.AttrsOf<Props>;
    type Props = DataAnnotation.Props & {
        x: p.XCoordinateSpec;
        y: p.YCoordinateSpec;
        x_units: p.Property<SpatialUnits>;
        y_units: p.Property<SpatialUnits>;
        text: p.StringSpec;
        angle: p.AngleSpec;
        x_offset: p.NumberSpec;
        y_offset: p.NumberSpec;
        /** @deprecated */
        render_mode: p.Property<RenderMode>;
    } & Mixins;
    type Mixins = mixins.TextVector & mixins.Prefixed<"border", mixins.LineVector> & mixins.Prefixed<"background", mixins.FillVector>;
    type Visuals = DataAnnotation.Visuals & {
        text: visuals.TextVector;
        border_line: visuals.LineVector;
        background_fill: visuals.FillVector;
    };
}
export interface LabelSet extends LabelSet.Attrs {
}
export declare class LabelSet extends DataAnnotation {
    properties: LabelSet.Props;
    __view_type__: LabelSetView;
    constructor(attrs?: Partial<LabelSet.Attrs>);
}
//# sourceMappingURL=label_set.d.ts.map