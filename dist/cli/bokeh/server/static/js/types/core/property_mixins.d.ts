import * as p from "./properties";
import { Color } from "./types";
import { LineJoin, LineCap, LineDash, FontStyle, HatchPatternType, TextAlign, TextBaseline } from "./enums";
import { Texture } from "../models/textures/texture";
export declare type HatchPattern = HatchPatternType | string;
export declare type HatchExtra = {
    [key: string]: Texture;
};
export declare type Line = {
    line_color: p.Property<Color | null>;
    line_alpha: p.Property<number>;
    line_width: p.Property<number>;
    line_join: p.Property<LineJoin>;
    line_cap: p.Property<LineCap>;
    line_dash: p.Property<LineDash | number[]>;
    line_dash_offset: p.Property<number>;
};
export declare type Fill = {
    fill_color: p.Property<Color | null>;
    fill_alpha: p.Property<number>;
};
export declare type Hatch = {
    hatch_color: p.Property<Color | null>;
    hatch_alpha: p.Property<number>;
    hatch_scale: p.Property<number>;
    hatch_pattern: p.Property<HatchPattern | null>;
    hatch_weight: p.Property<number>;
    hatch_extra: p.Property<HatchExtra>;
};
export declare type Text = {
    text_color: p.Property<Color | null>;
    text_alpha: p.Property<number>;
    text_font: p.Property<string>;
    text_font_size: p.Property<string>;
    text_font_style: p.Property<FontStyle>;
    text_align: p.Property<TextAlign>;
    text_baseline: p.Property<TextBaseline>;
    text_line_height: p.Property<number>;
};
export declare const Line: p.DefineOf<Line>;
export declare const Fill: p.DefineOf<Fill>;
export declare const Hatch: p.DefineOf<Hatch>;
export declare const Text: p.DefineOf<Text>;
export declare type LineScalar = {
    line_color: p.ScalarSpec<Color | null>;
    line_alpha: p.ScalarSpec<number>;
    line_width: p.ScalarSpec<number>;
    line_join: p.ScalarSpec<LineJoin>;
    line_cap: p.ScalarSpec<LineCap>;
    line_dash: p.ScalarSpec<LineDash | number[]>;
    line_dash_offset: p.ScalarSpec<number>;
};
export declare type FillScalar = {
    fill_color: p.ScalarSpec<Color | null>;
    fill_alpha: p.ScalarSpec<number>;
};
export declare type HatchScalar = {
    hatch_color: p.ScalarSpec<Color | null>;
    hatch_alpha: p.ScalarSpec<number>;
    hatch_scale: p.ScalarSpec<number>;
    hatch_pattern: p.ScalarSpec<string | null>;
    hatch_weight: p.ScalarSpec<number>;
    hatch_extra: p.ScalarSpec<HatchExtra>;
};
export declare type TextScalar = {
    text_color: p.ScalarSpec<Color | null>;
    text_alpha: p.ScalarSpec<number>;
    text_font: p.ScalarSpec<string>;
    text_font_size: p.ScalarSpec<string>;
    text_font_style: p.ScalarSpec<FontStyle>;
    text_align: p.ScalarSpec<TextAlign>;
    text_baseline: p.ScalarSpec<TextBaseline>;
    text_line_height: p.ScalarSpec<number>;
};
export declare const LineScalar: p.DefineOf<LineScalar>;
export declare const FillScalar: p.DefineOf<FillScalar>;
export declare const HatchScalar: p.DefineOf<HatchScalar>;
export declare const TextScalar: p.DefineOf<TextScalar>;
export declare type LineVector = {
    line_color: p.ColorSpec;
    line_alpha: p.VectorSpec<number>;
    line_width: p.VectorSpec<number>;
    line_join: p.VectorSpec<LineJoin>;
    line_cap: p.VectorSpec<LineCap>;
    line_dash: p.VectorSpec<LineDash | number[]>;
    line_dash_offset: p.VectorSpec<number>;
};
export declare type FillVector = {
    fill_color: p.ColorSpec;
    fill_alpha: p.VectorSpec<number>;
};
export declare type HatchVector = {
    hatch_color: p.ColorSpec;
    hatch_alpha: p.VectorSpec<number>;
    hatch_scale: p.VectorSpec<number>;
    hatch_pattern: p.VectorSpec<HatchPattern | null>;
    hatch_weight: p.VectorSpec<number>;
    hatch_extra: p.ScalarSpec<HatchExtra>;
};
export declare type TextVector = {
    text_color: p.ColorSpec;
    text_alpha: p.VectorSpec<number>;
    text_font: p.VectorSpec<string>;
    text_font_size: p.VectorSpec<string>;
    text_font_style: p.VectorSpec<FontStyle>;
    text_align: p.VectorSpec<TextAlign>;
    text_baseline: p.VectorSpec<TextBaseline>;
    text_line_height: p.VectorSpec<number>;
};
export declare const LineVector: p.DefineOf<LineVector>;
export declare const FillVector: p.DefineOf<FillVector>;
export declare const HatchVector: p.DefineOf<HatchVector>;
export declare const TextVector: p.DefineOf<TextVector>;
export declare type Prefixed<P extends string, T> = {
    [key in keyof T & string as `${P}_${key}`]: T[key];
};
export declare type AxisLabelText = Prefixed<"axis_label", Text>;
export declare type AxisLine = Prefixed<"axis", Line>;
export declare type BackgroundFill = Prefixed<"background", Fill>;
export declare type BandFill = Prefixed<"band", Fill>;
export declare type BandHatch = Prefixed<"band", Hatch>;
export declare type BarLine = Prefixed<"bar", Line>;
export declare type BorderFill = Prefixed<"border", Fill>;
export declare type BorderLine = Prefixed<"border", Line>;
export declare type GridLine = Prefixed<"grid", Line>;
export declare type GroupText = Prefixed<"group", Text>;
export declare type InactiveFill = Prefixed<"inactive", Fill>;
export declare type LabelText = Prefixed<"label", Text>;
export declare type MajorLabelText = Prefixed<"major_label", Text>;
export declare type MajorTickLine = Prefixed<"major_tick", Line>;
export declare type MinorGridLine = Prefixed<"minor_grid", Line>;
export declare type MinorTickLine = Prefixed<"minor_tick", Line>;
export declare type OutlineLine = Prefixed<"outline", Line>;
export declare type SeparatorLine = Prefixed<"separator", Line>;
export declare type SubGroupText = Prefixed<"subgroup", Text>;
export declare type TitleText = Prefixed<"title", Text>;
declare type Mixins = Text | Line | Fill | Hatch;
export declare function attrs_of<P extends string, T extends Mixins>(model: any, prefix: P, mixin: p.DefineOf<T>, prefixed?: boolean): {
    [key: string]: any;
};
export {};
//# sourceMappingURL=property_mixins.d.ts.map