import { Annotation, AnnotationView } from "./annotation";
import { Title } from "./title";
import { CartesianFrame } from "../canvas/cartesian_frame";
import { Axis } from "../axes";
import { Ticker } from "../tickers/ticker";
import { TickFormatter } from "../formatters/tick_formatter";
import { LabelingPolicy } from "../policies/labeling";
import { ColorMapper } from "../mappers/color_mapper";
import { Scale } from "../scales";
import { Range } from "../ranges";
import { BaseText } from "../text/base_text";
import { Anchor, Orientation } from "../../core/enums";
import * as visuals from "../../core/visuals";
import * as mixins from "../../core/property_mixins";
import * as p from "../../core/properties";
import { Context2d } from "../../core/util/canvas";
import { Layoutable } from "../../core/layout";
import { BorderLayout } from "../../core/layout/border";
import { BBox } from "../../core/util/bbox";
import { SerializableState } from "../../core/view";
export declare class ColorBarView extends AnnotationView {
    model: ColorBar;
    visuals: ColorBar.Visuals;
    layout: Layoutable;
    protected _image: HTMLCanvasElement;
    protected _frame: CartesianFrame;
    protected _axis: Axis;
    protected _axis_view: Axis["__view_type__"];
    protected _title?: Title;
    protected _title_view?: Title["__view_type__"];
    protected _ticker: Ticker;
    protected _formatter: TickFormatter;
    protected _inner_layout: BorderLayout;
    protected _major_range: Range;
    protected _major_scale: Scale;
    protected _minor_range: Range;
    protected _minor_scale: Scale;
    private _orientation;
    get orientation(): Orientation;
    initialize(): void;
    lazy_initialize(): Promise<void>;
    remove(): void;
    connect_signals(): void;
    protected _set_canvas_image(): void;
    update_layout(): void;
    protected _render(): void;
    protected _paint_bbox(ctx: Context2d, bbox: BBox): void;
    protected _paint_image(ctx: Context2d, bbox: BBox): void;
    serializable_state(): SerializableState;
}
export declare namespace ColorBar {
    type Attrs = p.AttrsOf<Props>;
    type Props = Annotation.Props & {
        location: p.Property<Anchor | [number, number]>;
        orientation: p.Property<Orientation | "auto">;
        title: p.Property<string | null>;
        title_standoff: p.Property<number>;
        width: p.Property<number | "auto">;
        height: p.Property<number | "auto">;
        scale_alpha: p.Property<number>;
        ticker: p.Property<Ticker | "auto">;
        formatter: p.Property<TickFormatter | "auto">;
        major_label_overrides: p.Property<{
            [key: string]: string | BaseText;
        }>;
        major_label_policy: p.Property<LabelingPolicy>;
        color_mapper: p.Property<ColorMapper>;
        label_standoff: p.Property<number>;
        margin: p.Property<number>;
        padding: p.Property<number>;
        major_tick_in: p.Property<number>;
        major_tick_out: p.Property<number>;
        minor_tick_in: p.Property<number>;
        minor_tick_out: p.Property<number>;
    } & Mixins;
    type Mixins = mixins.MajorLabelText & mixins.TitleText & mixins.MajorTickLine & mixins.MinorTickLine & mixins.BorderLine & mixins.BarLine & mixins.BackgroundFill;
    type Visuals = Annotation.Visuals & {
        major_label_text: visuals.Text;
        title_text: visuals.Text;
        major_tick_line: visuals.Line;
        minor_tick_line: visuals.Line;
        border_line: visuals.Line;
        bar_line: visuals.Line;
        background_fill: visuals.Fill;
    };
}
export interface ColorBar extends ColorBar.Attrs {
}
export declare class ColorBar extends Annotation {
    properties: ColorBar.Props;
    __view_type__: ColorBarView;
    constructor(attrs?: Partial<ColorBar.Attrs>);
}
//# sourceMappingURL=color_bar.d.ts.map