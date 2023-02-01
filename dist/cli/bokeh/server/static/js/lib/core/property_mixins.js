import * as p from "./properties";
import { LineJoin, LineCap, LineDash, FontStyle, HatchPatternType, TextAlign, TextBaseline } from "./enums";
import * as k from "./kinds";
import { keys } from "./util/object";
export const Line = {
    line_color: [k.Nullable(k.Color), "black"],
    line_alpha: [k.Alpha, 1.0],
    line_width: [k.Number, 1],
    line_join: [LineJoin, "bevel"],
    line_cap: [LineCap, "butt"],
    line_dash: [k.Or(LineDash, k.Array(k.Number)), []],
    line_dash_offset: [k.Number, 0],
};
export const Fill = {
    fill_color: [k.Nullable(k.Color), "gray"],
    fill_alpha: [k.Alpha, 1.0],
};
export const Hatch = {
    hatch_color: [k.Nullable(k.Color), "black"],
    hatch_alpha: [k.Alpha, 1.0],
    hatch_scale: [k.Number, 12.0],
    hatch_pattern: [k.Nullable(k.Or(HatchPatternType, k.String)), null],
    hatch_weight: [k.Number, 1.0],
    hatch_extra: [k.Dict(k.AnyRef()), {}], // XXX: recursive imports
};
export const Text = {
    text_color: [k.Nullable(k.Color), "#444444"],
    text_alpha: [k.Alpha, 1.0],
    text_font: [p.Font, "helvetica"],
    text_font_size: [k.FontSize, "16px"],
    text_font_style: [FontStyle, "normal"],
    text_align: [TextAlign, "left"],
    text_baseline: [TextBaseline, "bottom"],
    text_line_height: [k.Number, 1.2],
};
export const LineScalar = {
    line_color: [p.ColorScalar, "black"],
    line_alpha: [p.NumberScalar, 1.0],
    line_width: [p.NumberScalar, 1],
    line_join: [p.LineJoinScalar, "bevel"],
    line_cap: [p.LineCapScalar, "butt"],
    line_dash: [p.LineDashScalar, []],
    line_dash_offset: [p.NumberScalar, 0],
};
export const FillScalar = {
    fill_color: [p.ColorScalar, "gray"],
    fill_alpha: [p.NumberScalar, 1.0],
};
export const HatchScalar = {
    hatch_color: [p.ColorScalar, "black"],
    hatch_alpha: [p.NumberScalar, 1.0],
    hatch_scale: [p.NumberScalar, 12.0],
    hatch_pattern: [p.NullStringScalar, null],
    hatch_weight: [p.NumberScalar, 1.0],
    hatch_extra: [p.AnyScalar, {}],
};
export const TextScalar = {
    text_color: [p.ColorScalar, "#444444"],
    text_alpha: [p.NumberScalar, 1.0],
    text_font: [p.FontScalar, "helvetica"],
    text_font_size: [p.FontSizeScalar, "16px"],
    text_font_style: [p.FontStyleScalar, "normal"],
    text_align: [p.TextAlignScalar, "left"],
    text_baseline: [p.TextBaselineScalar, "bottom"],
    text_line_height: [p.NumberScalar, 1.2],
};
export const LineVector = {
    line_color: [p.ColorSpec, "black"],
    line_alpha: [p.NumberSpec, 1.0],
    line_width: [p.NumberSpec, 1],
    line_join: [p.LineJoinSpec, "bevel"],
    line_cap: [p.LineCapSpec, "butt"],
    line_dash: [p.LineDashSpec, []],
    line_dash_offset: [p.NumberSpec, 0],
};
export const FillVector = {
    fill_color: [p.ColorSpec, "gray"],
    fill_alpha: [p.NumberSpec, 1.0],
};
export const HatchVector = {
    hatch_color: [p.ColorSpec, "black"],
    hatch_alpha: [p.NumberSpec, 1.0],
    hatch_scale: [p.NumberSpec, 12.0],
    hatch_pattern: [p.NullStringSpec, null],
    hatch_weight: [p.NumberSpec, 1.0],
    hatch_extra: [p.AnyScalar, {}],
};
export const TextVector = {
    text_color: [p.ColorSpec, "#444444"],
    text_alpha: [p.NumberSpec, 1.0],
    text_font: [p.FontSpec, "helvetica"],
    text_font_size: [p.FontSizeSpec, "16px"],
    text_font_style: [p.FontStyleSpec, "normal"],
    text_align: [p.TextAlignSpec, "left"],
    text_baseline: [p.TextBaselineSpec, "bottom"],
    text_line_height: [p.NumberSpec, 1.2],
};
export function attrs_of(model, prefix, mixin, prefixed = false) {
    const attrs = {};
    for (const attr of keys(mixin)) {
        const prefixed_attr = `${prefix}${attr}`;
        const value = model[prefixed_attr];
        attrs[prefixed ? prefixed_attr : attr] = value;
    }
    return attrs;
}
//# sourceMappingURL=property_mixins.js.map