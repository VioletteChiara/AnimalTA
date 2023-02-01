import { Signal0 } from "./signaling";
import type { HasProps } from "./has_props";
import * as enums from "./enums";
import { Arrayable, IntArray, FloatArray, TypedArray, ColorArray, uint32 } from "./types";
import * as types from "./types";
import { Factor } from "../models/ranges/factor_range";
import { ColumnarDataSource } from "../models/sources/columnar_data_source";
import { Scalar, Vector, Dimensional, Transform, Expression } from "./vectorization";
import { Kind } from "./kinds";
import { NDArray } from "./util/ndarray";
import { Uniform, UniformScalar, UniformVector, ColorUniformVector } from "./uniforms";
export { Uniform, UniformScalar, UniformVector };
export declare function isSpec(obj: any): boolean;
export declare type Spec<T> = {
    readonly value?: T;
    readonly field?: string;
    readonly expr?: Expression<T>;
    readonly transform?: Transform<unknown, T>;
};
export declare type UniformsOf<M> = {
    [K in keyof M]: M[K] extends VectorSpec<infer T, any> ? Uniform<T> : M[K] extends ScalarSpec<infer T, any> ? UniformScalar<T> : M[K] extends Property<infer T> ? T : never;
};
export declare type AttrsOf<P> = {
    [K in keyof P]: P[K] extends Property<infer T> ? T : never;
};
export declare type DefineOf<P> = {
    [K in keyof P]: P[K] extends Property<infer T> ? [PropertyConstructor<T> | PropertyAlias | Kind<T>, (T | ((obj: HasProps) => T))?, PropertyOptions<T>?] : never;
};
export declare type DefaultsOf<P> = {
    [K in keyof P]: P[K] extends Property<infer T> ? T | ((obj: HasProps) => T) : never;
};
export declare type PropertyOptions<T> = {
    internal?: boolean;
    convert?(value: T): T | undefined;
    on_update?(value: T, obj: HasProps): void;
};
export interface PropertyConstructor<T> {
    new (obj: HasProps, attr: string, kind: Kind<T>, default_value?: (obj: HasProps) => T, initial_value?: T, options?: PropertyOptions<T>): Property<T>;
    readonly prototype: Property<T>;
}
export declare abstract class Property<T = unknown> {
    readonly obj: HasProps;
    readonly attr: string;
    readonly kind: Kind<T>;
    readonly default_value?: ((obj: HasProps) => T) | undefined;
    __value__: T;
    get is_value(): boolean;
    get syncable(): boolean;
    protected spec: Spec<T>;
    get_value(): T;
    set_value(val: T): void;
    _default_override(): T | undefined;
    private _dirty;
    get dirty(): boolean;
    readonly change: Signal0<HasProps>;
    internal: boolean;
    convert?(value: T): T | undefined;
    on_update?(value: T, obj: HasProps): void;
    constructor(obj: HasProps, attr: string, kind: Kind<T>, default_value?: ((obj: HasProps) => T) | undefined, initial_value?: T, options?: PropertyOptions<T>);
    protected _update(attr_value: T): void;
    toString(): string;
    normalize(values: any): any;
    validate(value: unknown): void;
    valid(value: unknown): boolean;
    _value(do_spec_transform?: boolean): any;
}
export declare class PropertyAlias {
    readonly attr: string;
    constructor(attr: string);
}
export declare function Alias(attr: string): PropertyAlias;
export declare class PrimitiveProperty<T> extends Property<T> {
}
/** @deprecated */
export declare class Any extends Property<any> {
}
/** @deprecated */
export declare class Array extends Property<any[]> {
    valid(value: unknown): boolean;
}
/** @deprecated */
export declare class Boolean extends Property<boolean> {
    valid(value: unknown): boolean;
}
/** @deprecated */
export declare class Color extends Property<types.Color> {
    valid(value: unknown): boolean;
}
/** @deprecated */
export declare class Instance extends Property<any> {
}
/** @deprecated */
export declare class Number extends Property<number> {
    valid(value: unknown): boolean;
}
/** @deprecated */
export declare class Int extends Number {
    valid(value: unknown): boolean;
}
/** @deprecated */
export declare class Angle extends Number {
}
/** @deprecated */
export declare class Percent extends Number {
    valid(value: unknown): boolean;
}
/** @deprecated */
export declare class String extends Property<string> {
    valid(value: unknown): boolean;
}
/** @deprecated */
export declare class NullString extends Property<string | null> {
    valid(value: unknown): boolean;
}
/** @deprecated */
export declare class FontSize extends String {
}
/** @deprecated */
export declare class Font extends String {
    _default_override(): string | undefined;
}
/** @deprecated */
export declare abstract class EnumProperty<T extends string> extends Property<T> {
    abstract get enum_values(): T[];
    valid(value: unknown): boolean;
}
/** @deprecated */
export declare function Enum<T extends string>(values: Iterable<T>): PropertyConstructor<T>;
export declare class Direction extends EnumProperty<enums.Direction> {
    get enum_values(): enums.Direction[];
    normalize(values: any): any;
}
/** @deprecated */ export declare const Anchor: PropertyConstructor<"center" | "top_left" | "top_center" | "top_right" | "center_left" | "center_center" | "center_right" | "bottom_left" | "bottom_center" | "bottom_right" | "top" | "left" | "right" | "bottom">;
/** @deprecated */ export declare const AngleUnits: PropertyConstructor<"deg" | "rad" | "grad" | "turn">;
/** @deprecated */ export declare const BoxOrigin: PropertyConstructor<"center" | "corner">;
/** @deprecated */ export declare const ButtonType: PropertyConstructor<"default" | "primary" | "success" | "warning" | "danger" | "light">;
/** @deprecated */ export declare const CalendarPosition: PropertyConstructor<"auto" | "above" | "below">;
/** @deprecated */ export declare const Dimension: PropertyConstructor<"width" | "height">;
/** @deprecated */ export declare const Dimensions: PropertyConstructor<"width" | "height" | "both">;
/** @deprecated */ export declare const Distribution: PropertyConstructor<"uniform" | "normal">;
/** @deprecated */ export declare const FontStyle: PropertyConstructor<"bold" | "normal" | "italic" | "bold italic">;
/** @deprecated */ export declare const HatchPatternType: PropertyConstructor<"blank" | "dot" | "ring" | "horizontal_line" | "vertical_line" | "cross" | "horizontal_dash" | "vertical_dash" | "spiral" | "right_diagonal_line" | "left_diagonal_line" | "diagonal_cross" | "right_diagonal_dash" | "left_diagonal_dash" | "horizontal_wave" | "vertical_wave" | "criss_cross" | " " | "." | "o" | "-" | "|" | "+" | "\"" | ":" | "@" | "/" | "\\" | "x" | "," | "`" | "v" | ">" | "*">;
/** @deprecated */ export declare const HTTPMethod: PropertyConstructor<"POST" | "GET">;
/** @deprecated */ export declare const HexTileOrientation: PropertyConstructor<"pointytop" | "flattop">;
/** @deprecated */ export declare const HoverMode: PropertyConstructor<"mouse" | "hline" | "vline">;
/** @deprecated */ export declare const LatLon: PropertyConstructor<"lat" | "lon">;
/** @deprecated */ export declare const LegendClickPolicy: PropertyConstructor<"none" | "hide" | "mute">;
/** @deprecated */ export declare const LegendLocation: PropertyConstructor<"center" | "top_left" | "top_center" | "top_right" | "center_left" | "center_center" | "center_right" | "bottom_left" | "bottom_center" | "bottom_right" | "top" | "left" | "right" | "bottom">;
/** @deprecated */ export declare const LineCap: PropertyConstructor<"round" | "butt" | "square">;
/** @deprecated */ export declare const LineJoin: PropertyConstructor<"round" | "miter" | "bevel">;
/** @deprecated */ export declare const LinePolicy: PropertyConstructor<"none" | "prev" | "next" | "nearest" | "interp">;
/** @deprecated */ export declare const Location: PropertyConstructor<"left" | "right" | "above" | "below">;
/** @deprecated */ export declare const Logo: PropertyConstructor<"grey" | "normal">;
/** @deprecated */ export declare const MarkerType: PropertyConstructor<"dot" | "cross" | "x" | "square" | "asterisk" | "circle" | "circle_cross" | "circle_dot" | "circle_x" | "circle_y" | "dash" | "diamond" | "diamond_cross" | "diamond_dot" | "hex" | "hex_dot" | "inverted_triangle" | "plus" | "square_cross" | "square_dot" | "square_pin" | "square_x" | "star" | "star_dot" | "triangle" | "triangle_dot" | "triangle_pin" | "y">;
/** @deprecated */ export declare const MutedPolicy: PropertyConstructor<"show" | "ignore">;
/** @deprecated */ export declare const Orientation: PropertyConstructor<"vertical" | "horizontal">;
/** @deprecated */ export declare const OutputBackend: PropertyConstructor<"canvas" | "svg" | "webgl">;
/** @deprecated */ export declare const PaddingUnits: PropertyConstructor<"percent" | "absolute">;
/** @deprecated */ export declare const Place: PropertyConstructor<"center" | "left" | "right" | "above" | "below">;
/** @deprecated */ export declare const PointPolicy: PropertyConstructor<"none" | "snap_to_data" | "follow_mouse">;
/** @deprecated */ export declare const RadiusDimension: PropertyConstructor<"x" | "y" | "max" | "min">;
/** @deprecated */ export declare const RenderLevel: PropertyConstructor<"image" | "underlay" | "glyph" | "guide" | "annotation" | "overlay">;
/** @deprecated */ export declare const RenderMode: PropertyConstructor<"canvas" | "css">;
/** @deprecated */ export declare const ResetPolicy: PropertyConstructor<"standard" | "event_only">;
/** @deprecated */ export declare const RoundingFunction: PropertyConstructor<"round" | "nearest" | "floor" | "rounddown" | "ceil" | "roundup">;
/** @deprecated */ export declare const Side: PropertyConstructor<"left" | "right" | "above" | "below">;
/** @deprecated */ export declare const SizingMode: PropertyConstructor<"fixed" | "stretch_width" | "stretch_height" | "stretch_both" | "scale_width" | "scale_height" | "scale_both">;
/** @deprecated */ export declare const Sort: PropertyConstructor<"ascending" | "descending">;
/** @deprecated */ export declare const SpatialUnits: PropertyConstructor<"data" | "screen">;
/** @deprecated */ export declare const StartEnd: PropertyConstructor<"start" | "end">;
/** @deprecated */ export declare const StepMode: PropertyConstructor<"center" | "after" | "before">;
/** @deprecated */ export declare const TapBehavior: PropertyConstructor<"select" | "inspect">;
/** @deprecated */ export declare const TextAlign: PropertyConstructor<"center" | "left" | "right">;
/** @deprecated */ export declare const TextBaseline: PropertyConstructor<"top" | "bottom" | "middle" | "alphabetic" | "hanging" | "ideographic">;
/** @deprecated */ export declare const TextureRepetition: PropertyConstructor<"repeat" | "repeat_x" | "repeat_y" | "no_repeat">;
/** @deprecated */ export declare const TickLabelOrientation: PropertyConstructor<"normal" | "vertical" | "horizontal" | "parallel">;
/** @deprecated */ export declare const TooltipAttachment: PropertyConstructor<"left" | "right" | "above" | "below" | "vertical" | "horizontal">;
/** @deprecated */ export declare const UpdateMode: PropertyConstructor<"replace" | "append">;
/** @deprecated */ export declare const VerticalAlign: PropertyConstructor<"top" | "bottom" | "middle">;
export declare class ScalarSpec<T, S extends Scalar<T> = Scalar<T>> extends Property<T | S> {
    __value__: T;
    __scalar__: S;
    get_value(): S;
    protected _update(attr_value: S | T): void;
    materialize(value: T): T;
    scalar(value: T, n: number): UniformScalar<T>;
    uniform(source: ColumnarDataSource): UniformScalar<T>;
}
export declare class AnyScalar extends ScalarSpec<any> {
}
export declare class ColorScalar extends ScalarSpec<types.Color | null> {
}
export declare class NumberScalar extends ScalarSpec<number> {
}
export declare class StringScalar extends ScalarSpec<string> {
}
export declare class NullStringScalar extends ScalarSpec<string | null> {
}
export declare class ArrayScalar extends ScalarSpec<any[]> {
}
export declare class LineJoinScalar extends ScalarSpec<enums.LineJoin> {
}
export declare class LineCapScalar extends ScalarSpec<enums.LineCap> {
}
export declare class LineDashScalar extends ScalarSpec<enums.LineDash | number[]> {
}
export declare class FontScalar extends ScalarSpec<string> {
    _default_override(): string | undefined;
}
export declare class FontSizeScalar extends ScalarSpec<string> {
}
export declare class FontStyleScalar extends ScalarSpec<enums.FontStyle> {
}
export declare class TextAlignScalar extends ScalarSpec<enums.TextAlign> {
}
export declare class TextBaselineScalar extends ScalarSpec<enums.TextBaseline> {
}
export declare abstract class VectorSpec<T, V extends Vector<T> = Vector<T>> extends Property<T | V> {
    __value__: T;
    __vector__: V;
    get_value(): V;
    protected _update(attr_value: V | T): void;
    materialize(value: T): T;
    v_materialize(values: Arrayable<T>): Arrayable<T>;
    scalar(value: T, n: number): UniformScalar<T>;
    vector(values: Arrayable<T>): UniformVector<T>;
    uniform(source: ColumnarDataSource): Uniform<T>;
    array(source: ColumnarDataSource): Arrayable<unknown>;
}
export declare abstract class DataSpec<T> extends VectorSpec<T> {
}
export declare abstract class UnitsSpec<T, Units> extends VectorSpec<T, Dimensional<Vector<T>, Units>> {
    abstract get default_units(): Units;
    abstract get valid_units(): Units[];
    spec: Spec<T> & {
        units?: Units;
    };
    _update(attr_value: any): void;
    get units(): Units;
    set units(units: Units);
}
export declare abstract class NumberUnitsSpec<Units> extends UnitsSpec<number, Units> {
    array(source: ColumnarDataSource): FloatArray;
}
export declare abstract class BaseCoordinateSpec<T> extends DataSpec<T> {
    abstract get dimension(): "x" | "y";
}
export declare abstract class CoordinateSpec extends BaseCoordinateSpec<number | Factor> {
}
export declare abstract class CoordinateSeqSpec extends BaseCoordinateSpec<Arrayable<number> | Arrayable<Factor>> {
}
export declare abstract class CoordinateSeqSeqSeqSpec extends BaseCoordinateSpec<number[][][] | Factor[][][]> {
}
export declare class XCoordinateSpec extends CoordinateSpec {
    readonly dimension = "x";
}
export declare class YCoordinateSpec extends CoordinateSpec {
    readonly dimension = "y";
}
export declare class XCoordinateSeqSpec extends CoordinateSeqSpec {
    readonly dimension = "x";
}
export declare class YCoordinateSeqSpec extends CoordinateSeqSpec {
    readonly dimension = "y";
}
export declare class XCoordinateSeqSeqSeqSpec extends CoordinateSeqSeqSeqSpec {
    readonly dimension = "x";
}
export declare class YCoordinateSeqSeqSeqSpec extends CoordinateSeqSeqSeqSpec {
    readonly dimension = "y";
}
export declare class AngleSpec extends NumberUnitsSpec<enums.AngleUnits> {
    get default_units(): enums.AngleUnits;
    get valid_units(): enums.AngleUnits[];
    materialize(value: number): number;
    v_materialize(values: Arrayable<number>): Float32Array;
    array(_source: ColumnarDataSource): Float32Array;
}
export declare class DistanceSpec extends NumberUnitsSpec<enums.SpatialUnits> {
    get default_units(): enums.SpatialUnits;
    get valid_units(): enums.SpatialUnits[];
}
export declare class NullDistanceSpec extends DistanceSpec {
    materialize(value: number | null): number;
}
export declare class BooleanSpec extends DataSpec<boolean> {
    v_materialize(values: Arrayable<boolean>): Arrayable<boolean>;
    array(source: ColumnarDataSource): Uint8Array;
}
export declare class IntSpec extends DataSpec<number> {
    v_materialize(values: Arrayable<number>): TypedArray;
    array(source: ColumnarDataSource): IntArray;
}
export declare class NumberSpec extends DataSpec<number> {
    v_materialize(values: Arrayable<number>): TypedArray;
    array(source: ColumnarDataSource): FloatArray;
}
export declare class ScreenSizeSpec extends NumberSpec {
    valid(value: unknown): boolean;
}
export declare class ColorSpec extends DataSpec<types.Color | null> {
    materialize(color: types.Color | null): uint32;
    v_materialize(colors: Arrayable<types.Color | null>): ColorArray;
    vector(values: ColorArray): ColorUniformVector;
}
export declare class NDArraySpec extends DataSpec<NDArray> {
}
export declare class AnySpec extends DataSpec<any> {
}
export declare class StringSpec extends DataSpec<string> {
}
export declare class NullStringSpec extends DataSpec<string | null> {
}
export declare class ArraySpec extends DataSpec<any[]> {
}
export declare class MarkerSpec extends DataSpec<enums.MarkerType> {
}
export declare class LineJoinSpec extends DataSpec<enums.LineJoin> {
}
export declare class LineCapSpec extends DataSpec<enums.LineCap> {
}
export declare class LineDashSpec extends DataSpec<enums.LineDash | number[]> {
}
export declare class FontSpec extends DataSpec<string> {
    _default_override(): string | undefined;
}
export declare class FontSizeSpec extends DataSpec<string> {
}
export declare class FontStyleSpec extends DataSpec<enums.FontStyle> {
}
export declare class TextAlignSpec extends DataSpec<enums.TextAlign> {
}
export declare class TextBaselineSpec extends DataSpec<enums.TextBaseline> {
}
//# sourceMappingURL=properties.d.ts.map