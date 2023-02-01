import { Float32Buffer, NormalizedUint8Buffer, Uint8Buffer } from "./buffer";
import { AttributeConfig, BoundingBox, Texture2D, Vec2, Vec4 } from "regl";
declare type CommonProps = {
    scissor: BoundingBox;
    viewport: BoundingBox;
    canvas_size: Vec2;
    pixel_ratio: number;
    antialias: number;
};
declare type LineProps = {
    linewidth: Float32Buffer;
    line_color: NormalizedUint8Buffer;
    line_join: Uint8Buffer;
};
declare type LinePropsNoJoin = {
    linewidth: Float32Buffer;
    line_color: NormalizedUint8Buffer;
};
declare type FillProps = {
    fill_color: NormalizedUint8Buffer;
};
declare type DashProps = {
    length_so_far: Float32Buffer;
    dash_tex: Texture2D;
    dash_tex_info: number[];
    dash_scale: number;
    dash_offset: number;
};
declare type HatchProps = {
    hatch_pattern: Uint8Buffer;
    hatch_scale: Float32Buffer;
    hatch_weight: Float32Buffer;
    hatch_color: NormalizedUint8Buffer;
};
export declare type LineGlyphProps = CommonProps & {
    line_color: number[];
    linewidth: number;
    miter_limit: number;
    points: Float32Buffer;
    nsegments: number;
    line_cap: number;
    line_join: number;
};
export declare type LineDashGlyphProps = LineGlyphProps & DashProps;
export declare type MarkerGlyphProps = CommonProps & LinePropsNoJoin & FillProps & {
    center: Float32Buffer;
    nmarkers: number;
    size: Float32Buffer;
    angle: Float32Buffer;
    show: Uint8Buffer;
};
export declare type RectGlyphProps = CommonProps & LineProps & FillProps & {
    center: Float32Buffer;
    nmarkers: number;
    width: Float32Buffer;
    height: Float32Buffer;
    angle: Float32Buffer;
    show: Uint8Buffer;
};
export declare type RectHatchGlyphProps = RectGlyphProps & HatchProps;
export declare type CommonUniforms = {
    u_canvas_size: Vec2;
    u_pixel_ratio: number;
    u_antialias: number;
};
export declare type DashUniforms = {
    u_dash_tex: Texture2D;
    u_dash_tex_info: Vec4;
    u_dash_scale: number;
    u_dash_offset: number;
};
export declare type LineGlyphUniforms = CommonUniforms & {
    u_line_color: Vec4;
    u_linewidth: number;
    u_miter_limit: number;
    u_line_join: number;
    u_line_cap: number;
};
export declare type LineDashGlyphUniforms = LineGlyphUniforms & DashUniforms;
declare type LineAttributes = {
    a_linewidth: AttributeConfig;
    a_line_color: AttributeConfig;
    a_line_join: AttributeConfig;
};
declare type LineAttributesNoJoin = {
    a_linewidth: AttributeConfig;
    a_line_color: AttributeConfig;
};
declare type FillAttributes = {
    a_fill_color: AttributeConfig;
};
declare type HatchAttributes = {
    a_hatch_pattern: AttributeConfig;
    a_hatch_scale: AttributeConfig;
    a_hatch_weight: AttributeConfig;
    a_hatch_color: AttributeConfig;
};
export declare type LineGlyphAttributes = {
    a_position: AttributeConfig;
    a_point_prev: AttributeConfig;
    a_point_start: AttributeConfig;
    a_point_end: AttributeConfig;
    a_point_next: AttributeConfig;
};
export declare type LineDashGlyphAttributes = LineGlyphAttributes & {
    a_length_so_far: AttributeConfig;
};
export declare type MarkerGlyphAttributes = LineAttributesNoJoin & FillAttributes & {
    a_position: AttributeConfig;
    a_center: AttributeConfig;
    a_size: AttributeConfig;
    a_angle: AttributeConfig;
    a_show: AttributeConfig;
};
export declare type RectGlyphAttributes = LineAttributes & FillAttributes & {
    a_center: AttributeConfig;
    a_show: AttributeConfig;
    a_position: AttributeConfig;
    a_width: AttributeConfig;
    a_height: AttributeConfig;
    a_angle: AttributeConfig;
};
export declare type RectHatchGlyphAttributes = RectGlyphAttributes & HatchAttributes;
export {};
//# sourceMappingURL=types.d.ts.map