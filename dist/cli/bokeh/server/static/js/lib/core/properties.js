import { Signal0 } from "./signaling";
import { logger } from "./logging";
import * as enums from "./enums";
import { RGBAArray, ColorArray } from "./types";
import { includes, repeat } from "./util/array";
import { mul } from "./util/arrayable";
import { to_radians_coeff } from "./util/math";
import { is_Color, color2rgba, encode_rgba } from "./util/color";
import { to_big_endian } from "./util/platform";
import { isBoolean, isNumber, isString, isArray, isTypedArray, isPlainObject } from "./util/types";
import { settings } from "./settings";
import { is_NDArray } from "./util/ndarray";
import { Uniform, UniformScalar, UniformVector, ColorUniformVector } from "./uniforms";
export { Uniform, UniformScalar, UniformVector };
function valueToString(value) {
    try {
        return JSON.stringify(value);
    }
    catch {
        return value.toString();
    }
}
export function isSpec(obj) {
    return isPlainObject(obj) &&
        ((obj.value === undefined ? 0 : 1) +
            (obj.field === undefined ? 0 : 1) +
            (obj.expr === undefined ? 0 : 1) == 1); // garbage JS XOR
}
export class Property {
    constructor(obj, attr, kind, default_value, initial_value, options = {}) {
        this.obj = obj;
        this.attr = attr;
        this.kind = kind;
        this.default_value = default_value;
        this._dirty = false;
        this.change = new Signal0(this.obj, "change");
        this.internal = options.internal ?? false;
        this.convert = options.convert;
        this.on_update = options.on_update;
        let attr_value;
        if (initial_value !== undefined) {
            attr_value = initial_value;
            this._dirty = true;
        }
        else {
            const value = this._default_override();
            if (value !== undefined)
                attr_value = value;
            else if (default_value !== undefined)
                attr_value = default_value(obj);
            else {
                // XXX: temporary and super sketchy, but affects only "readonly" and a few internal properties
                // console.warn(`${this.obj}.${this.attr} has no value nor default`)
                this.spec = { value: null };
                return;
            }
        }
        this._update(attr_value);
    }
    get is_value() {
        return this.spec.value !== undefined;
    }
    get syncable() {
        return !this.internal;
    }
    get_value() {
        return this.spec.value;
    }
    set_value(val) {
        this._update(val);
        this._dirty = true;
    }
    // abstract _intrinsic_default(): T
    _default_override() {
        return undefined;
    }
    get dirty() {
        return this._dirty;
    }
    //protected abstract _update(attr_value: T): void
    _update(attr_value) {
        this.validate(attr_value);
        if (this.convert != null) {
            const converted = this.convert(attr_value);
            if (converted !== undefined)
                attr_value = converted;
        }
        this.spec = { value: attr_value };
        this.on_update?.(attr_value, this.obj);
    }
    toString() {
        /*${this.name}*/
        return `Prop(${this.obj}.${this.attr}, spec: ${valueToString(this.spec)})`;
    }
    // ----- customizable policies
    normalize(values) {
        return values;
    }
    validate(value) {
        if (!this.valid(value))
            throw new Error(`${this.obj}.${this.attr} given invalid value: ${valueToString(value)}`);
    }
    valid(value) {
        return this.kind.valid(value);
    }
    // ----- property accessors
    _value(do_spec_transform = true) {
        if (!this.is_value)
            throw new Error("attempted to retrieve property value for property without value specification");
        let ret = this.normalize([this.spec.value])[0];
        if (this.spec.transform != null && do_spec_transform)
            ret = this.spec.transform.compute(ret);
        return ret;
    }
}
Property.__name__ = "Property";
export class PropertyAlias {
    constructor(attr) {
        this.attr = attr;
    }
}
PropertyAlias.__name__ = "PropertyAlias";
export function Alias(attr) {
    return new PropertyAlias(attr);
}
//
// Primitive Properties
//
export class PrimitiveProperty extends Property {
}
PrimitiveProperty.__name__ = "PrimitiveProperty";
/** @deprecated */
export class Any extends Property {
}
Any.__name__ = "Any";
/** @deprecated */
export class Array extends Property {
    valid(value) {
        return isArray(value) || isTypedArray(value);
    }
}
Array.__name__ = "Array";
/** @deprecated */
export class Boolean extends Property {
    valid(value) {
        return isBoolean(value);
    }
}
Boolean.__name__ = "Boolean";
/** @deprecated */
export class Color extends Property {
    valid(value) {
        return is_Color(value);
    }
}
Color.__name__ = "Color";
/** @deprecated */
export class Instance extends Property {
}
Instance.__name__ = "Instance";
/** @deprecated */
export class Number extends Property {
    valid(value) {
        return isNumber(value);
    }
}
Number.__name__ = "Number";
/** @deprecated */
export class Int extends Number {
    valid(value) {
        return isNumber(value) && (value | 0) == value;
    }
}
Int.__name__ = "Int";
/** @deprecated */
export class Angle extends Number {
}
Angle.__name__ = "Angle";
/** @deprecated */
export class Percent extends Number {
    valid(value) {
        return isNumber(value) && 0 <= value && value <= 1.0;
    }
}
Percent.__name__ = "Percent";
/** @deprecated */
export class String extends Property {
    valid(value) {
        return isString(value);
    }
}
String.__name__ = "String";
/** @deprecated */
export class NullString extends Property {
    valid(value) {
        return value === null || isString(value);
    }
}
NullString.__name__ = "NullString";
/** @deprecated */
export class FontSize extends String {
}
FontSize.__name__ = "FontSize";
/** @deprecated */
export class Font extends String {
    _default_override() {
        return settings.dev ? "Bokeh" : undefined;
    }
}
Font.__name__ = "Font";
//
// Enum properties
//
/** @deprecated */
export class EnumProperty extends Property {
    valid(value) {
        return isString(value) && includes(this.enum_values, value);
    }
}
EnumProperty.__name__ = "EnumProperty";
/** @deprecated */
export function Enum(values) {
    return class extends EnumProperty {
        get enum_values() {
            return [...values];
        }
    };
}
export class Direction extends EnumProperty {
    get enum_values() {
        return [...enums.Direction];
    }
    normalize(values) {
        const result = new Uint8Array(values.length);
        for (let i = 0; i < values.length; i++) {
            switch (values[i]) {
                case "clock":
                    result[i] = 0;
                    break;
                case "anticlock":
                    result[i] = 1;
                    break;
            }
        }
        return result;
    }
}
Direction.__name__ = "Direction";
/** @deprecated */ export const Anchor = Enum(enums.Anchor);
/** @deprecated */ export const AngleUnits = Enum(enums.AngleUnits);
/** @deprecated */ export const BoxOrigin = Enum(enums.BoxOrigin);
/** @deprecated */ export const ButtonType = Enum(enums.ButtonType);
/** @deprecated */ export const CalendarPosition = Enum(enums.CalendarPosition);
/** @deprecated */ export const Dimension = Enum(enums.Dimension);
/** @deprecated */ export const Dimensions = Enum(enums.Dimensions);
/** @deprecated */ export const Distribution = Enum(enums.Distribution);
/** @deprecated */ export const FontStyle = Enum(enums.FontStyle);
/** @deprecated */ export const HatchPatternType = Enum(enums.HatchPatternType);
/** @deprecated */ export const HTTPMethod = Enum(enums.HTTPMethod);
/** @deprecated */ export const HexTileOrientation = Enum(enums.HexTileOrientation);
/** @deprecated */ export const HoverMode = Enum(enums.HoverMode);
/** @deprecated */ export const LatLon = Enum(enums.LatLon);
/** @deprecated */ export const LegendClickPolicy = Enum(enums.LegendClickPolicy);
/** @deprecated */ export const LegendLocation = Enum(enums.LegendLocation);
/** @deprecated */ export const LineCap = Enum(enums.LineCap);
/** @deprecated */ export const LineJoin = Enum(enums.LineJoin);
/** @deprecated */ export const LinePolicy = Enum(enums.LinePolicy);
/** @deprecated */ export const Location = Enum(enums.Location);
/** @deprecated */ export const Logo = Enum(enums.Logo);
/** @deprecated */ export const MarkerType = Enum(enums.MarkerType);
/** @deprecated */ export const MutedPolicy = Enum(enums.MutedPolicy);
/** @deprecated */ export const Orientation = Enum(enums.Orientation);
/** @deprecated */ export const OutputBackend = Enum(enums.OutputBackend);
/** @deprecated */ export const PaddingUnits = Enum(enums.PaddingUnits);
/** @deprecated */ export const Place = Enum(enums.Place);
/** @deprecated */ export const PointPolicy = Enum(enums.PointPolicy);
/** @deprecated */ export const RadiusDimension = Enum(enums.RadiusDimension);
/** @deprecated */ export const RenderLevel = Enum(enums.RenderLevel);
/** @deprecated */ export const RenderMode = Enum(enums.RenderMode);
/** @deprecated */ export const ResetPolicy = Enum(enums.ResetPolicy);
/** @deprecated */ export const RoundingFunction = Enum(enums.RoundingFunction);
/** @deprecated */ export const Side = Enum(enums.Side);
/** @deprecated */ export const SizingMode = Enum(enums.SizingMode);
/** @deprecated */ export const Sort = Enum(enums.Sort);
/** @deprecated */ export const SpatialUnits = Enum(enums.SpatialUnits);
/** @deprecated */ export const StartEnd = Enum(enums.StartEnd);
/** @deprecated */ export const StepMode = Enum(enums.StepMode);
/** @deprecated */ export const TapBehavior = Enum(enums.TapBehavior);
/** @deprecated */ export const TextAlign = Enum(enums.TextAlign);
/** @deprecated */ export const TextBaseline = Enum(enums.TextBaseline);
/** @deprecated */ export const TextureRepetition = Enum(enums.TextureRepetition);
/** @deprecated */ export const TickLabelOrientation = Enum(enums.TickLabelOrientation);
/** @deprecated */ export const TooltipAttachment = Enum(enums.TooltipAttachment);
/** @deprecated */ export const UpdateMode = Enum(enums.UpdateMode);
/** @deprecated */ export const VerticalAlign = Enum(enums.VerticalAlign);
//
// DataSpec properties
//
export class ScalarSpec extends Property {
    get_value() {
        // XXX: denormalize value for serialization, because bokeh doens't support scalar properties
        const { value, expr, transform } = this.spec;
        return (expr != null || transform != null ? this.spec : value);
        // XXX: allow obj.x = null; obj.x == null
        // return this.spec.value === null ? null : this.spec as any
    }
    _update(attr_value) {
        if (isSpec(attr_value))
            this.spec = attr_value;
        else
            this.spec = { value: attr_value };
        if (this.spec.value != null)
            this.validate(this.spec.value);
    }
    materialize(value) {
        return value;
    }
    scalar(value, n) {
        return new UniformScalar(value, n);
    }
    uniform(source) {
        const { expr, value, transform } = this.spec;
        const n = source.get_length() ?? 1;
        if (expr != null) {
            let result = expr.compute(source);
            if (transform != null)
                result = transform.compute(result);
            result = this.materialize(result);
            return this.scalar(result, n);
        }
        else {
            let result = value;
            if (transform != null)
                result = transform.compute(result);
            result = this.materialize(result);
            return this.scalar(result, n);
        }
    }
}
ScalarSpec.__name__ = "ScalarSpec";
export class AnyScalar extends ScalarSpec {
}
AnyScalar.__name__ = "AnyScalar";
export class ColorScalar extends ScalarSpec {
}
ColorScalar.__name__ = "ColorScalar";
export class NumberScalar extends ScalarSpec {
}
NumberScalar.__name__ = "NumberScalar";
export class StringScalar extends ScalarSpec {
}
StringScalar.__name__ = "StringScalar";
export class NullStringScalar extends ScalarSpec {
}
NullStringScalar.__name__ = "NullStringScalar";
export class ArrayScalar extends ScalarSpec {
}
ArrayScalar.__name__ = "ArrayScalar";
export class LineJoinScalar extends ScalarSpec {
}
LineJoinScalar.__name__ = "LineJoinScalar";
export class LineCapScalar extends ScalarSpec {
}
LineCapScalar.__name__ = "LineCapScalar";
export class LineDashScalar extends ScalarSpec {
}
LineDashScalar.__name__ = "LineDashScalar";
export class FontScalar extends ScalarSpec {
    _default_override() {
        return settings.dev ? "Bokeh" : undefined;
    }
}
FontScalar.__name__ = "FontScalar";
export class FontSizeScalar extends ScalarSpec {
}
FontSizeScalar.__name__ = "FontSizeScalar";
export class FontStyleScalar extends ScalarSpec {
}
FontStyleScalar.__name__ = "FontStyleScalar";
export class TextAlignScalar extends ScalarSpec {
}
TextAlignScalar.__name__ = "TextAlignScalar";
export class TextBaselineScalar extends ScalarSpec {
}
TextBaselineScalar.__name__ = "TextBaselineScalar";
export class VectorSpec extends Property {
    get_value() {
        // XXX: allow obj.x = null; obj.x == null
        return this.spec.value === null ? null : this.spec;
    }
    _update(attr_value) {
        if (isSpec(attr_value))
            this.spec = attr_value;
        else
            this.spec = { value: attr_value };
        if (this.spec.value != null)
            this.validate(this.spec.value);
    }
    materialize(value) {
        return value;
    }
    v_materialize(values) {
        return values;
    }
    scalar(value, n) {
        return new UniformScalar(value, n);
    }
    vector(values) {
        return new UniformVector(values);
    }
    uniform(source) {
        const { field, expr, value, transform } = this.spec;
        const n = source.get_length() ?? 1;
        if (field != null) {
            let array = source.get_column(field);
            if (array != null) {
                if (transform != null)
                    array = transform.v_compute(array);
                array = this.v_materialize(array);
                return this.vector(array);
            }
            else {
                logger.warn(`attempted to retrieve property array for nonexistent field '${field}'`);
                return this.scalar(null, n);
            }
        }
        else if (expr != null) {
            let array = expr.v_compute(source);
            if (transform != null)
                array = transform.v_compute(array);
            array = this.v_materialize(array);
            return this.vector(array);
        }
        else {
            let result = value;
            if (transform != null)
                result = transform.compute(result);
            result = this.materialize(result);
            return this.scalar(result, n);
        }
    }
    array(source) {
        let array;
        const length = source.get_length() ?? 1;
        if (this.spec.field != null) {
            const column = source.get_column(this.spec.field);
            if (column != null)
                array = this.normalize(column);
            else {
                logger.warn(`attempted to retrieve property array for nonexistent field '${this.spec.field}'`);
                const missing = new Float64Array(length);
                missing.fill(NaN);
                array = missing;
            }
        }
        else if (this.spec.expr != null) {
            array = this.normalize(this.spec.expr.v_compute(source));
        }
        else {
            const value = this._value(false); // don't apply any spec transform
            if (isNumber(value)) {
                const values = new Float64Array(length);
                values.fill(value);
                array = values;
            }
            else
                array = repeat(value, length);
        }
        if (this.spec.transform != null)
            array = this.spec.transform.v_compute(array);
        return array;
    }
}
VectorSpec.__name__ = "VectorSpec";
export class DataSpec extends VectorSpec {
}
DataSpec.__name__ = "DataSpec";
export class UnitsSpec extends VectorSpec {
    _update(attr_value) {
        super._update(attr_value);
        const { units } = this.spec;
        if (units != null && !includes(this.valid_units, units)) {
            throw new Error(`units must be one of ${this.valid_units.join(", ")}; got: ${units}`);
        }
    }
    get units() {
        return this.spec.units ?? this.default_units;
    }
    set units(units) {
        if (units != this.default_units)
            this.spec.units = units;
        else
            delete this.spec.units;
    }
}
UnitsSpec.__name__ = "UnitsSpec";
export class NumberUnitsSpec extends UnitsSpec {
    array(source) {
        return new Float64Array(super.array(source));
    }
}
NumberUnitsSpec.__name__ = "NumberUnitsSpec";
export class BaseCoordinateSpec extends DataSpec {
}
BaseCoordinateSpec.__name__ = "BaseCoordinateSpec";
export class CoordinateSpec extends BaseCoordinateSpec {
}
CoordinateSpec.__name__ = "CoordinateSpec";
export class CoordinateSeqSpec extends BaseCoordinateSpec {
}
CoordinateSeqSpec.__name__ = "CoordinateSeqSpec";
export class CoordinateSeqSeqSeqSpec extends BaseCoordinateSpec {
}
CoordinateSeqSeqSeqSpec.__name__ = "CoordinateSeqSeqSeqSpec";
export class XCoordinateSpec extends CoordinateSpec {
    constructor() {
        super(...arguments);
        this.dimension = "x";
    }
}
XCoordinateSpec.__name__ = "XCoordinateSpec";
export class YCoordinateSpec extends CoordinateSpec {
    constructor() {
        super(...arguments);
        this.dimension = "y";
    }
}
YCoordinateSpec.__name__ = "YCoordinateSpec";
export class XCoordinateSeqSpec extends CoordinateSeqSpec {
    constructor() {
        super(...arguments);
        this.dimension = "x";
    }
}
XCoordinateSeqSpec.__name__ = "XCoordinateSeqSpec";
export class YCoordinateSeqSpec extends CoordinateSeqSpec {
    constructor() {
        super(...arguments);
        this.dimension = "y";
    }
}
YCoordinateSeqSpec.__name__ = "YCoordinateSeqSpec";
export class XCoordinateSeqSeqSeqSpec extends CoordinateSeqSeqSeqSpec {
    constructor() {
        super(...arguments);
        this.dimension = "x";
    }
}
XCoordinateSeqSeqSeqSpec.__name__ = "XCoordinateSeqSeqSeqSpec";
export class YCoordinateSeqSeqSeqSpec extends CoordinateSeqSeqSeqSpec {
    constructor() {
        super(...arguments);
        this.dimension = "y";
    }
}
YCoordinateSeqSeqSeqSpec.__name__ = "YCoordinateSeqSeqSeqSpec";
export class AngleSpec extends NumberUnitsSpec {
    get default_units() { return "rad"; }
    get valid_units() { return [...enums.AngleUnits]; }
    materialize(value) {
        const coeff = -to_radians_coeff(this.units);
        return value * coeff;
    }
    v_materialize(values) {
        const coeff = -to_radians_coeff(this.units);
        const result = new Float32Array(values.length);
        mul(values, coeff, result); // TODO: in-place?
        return result;
    }
    array(_source) {
        throw new Error("not supported");
    }
}
AngleSpec.__name__ = "AngleSpec";
export class DistanceSpec extends NumberUnitsSpec {
    get default_units() { return "data"; }
    get valid_units() { return [...enums.SpatialUnits]; }
}
DistanceSpec.__name__ = "DistanceSpec";
export class NullDistanceSpec extends DistanceSpec {
    materialize(value) {
        return value ?? NaN;
    }
}
NullDistanceSpec.__name__ = "NullDistanceSpec";
export class BooleanSpec extends DataSpec {
    v_materialize(values) {
        return new Uint8Array(values);
    }
    array(source) {
        return new Uint8Array(super.array(source));
    }
}
BooleanSpec.__name__ = "BooleanSpec";
export class IntSpec extends DataSpec {
    v_materialize(values) {
        return isTypedArray(values) ? values : new Int32Array(values);
    }
    array(source) {
        return new Int32Array(super.array(source));
    }
}
IntSpec.__name__ = "IntSpec";
export class NumberSpec extends DataSpec {
    v_materialize(values) {
        return isTypedArray(values) ? values : new Float64Array(values);
    }
    array(source) {
        return new Float64Array(super.array(source));
    }
}
NumberSpec.__name__ = "NumberSpec";
export class ScreenSizeSpec extends NumberSpec {
    valid(value) {
        return isNumber(value) && value >= 0;
    }
}
ScreenSizeSpec.__name__ = "ScreenSizeSpec";
export class ColorSpec extends DataSpec {
    materialize(color) {
        return encode_rgba(color2rgba(color));
    }
    v_materialize(colors) {
        if (is_NDArray(colors)) {
            if (colors.dtype == "uint32" && colors.dimension == 1) {
                return to_big_endian(colors);
            }
            else if (colors.dtype == "uint8" && colors.dimension == 1) {
                const [n] = colors.shape;
                const array = new RGBAArray(4 * n);
                let j = 0;
                for (const gray of colors) {
                    array[j++] = gray;
                    array[j++] = gray;
                    array[j++] = gray;
                    array[j++] = 255;
                }
                return new ColorArray(array.buffer);
            }
            else if (colors.dtype == "uint8" && colors.dimension == 2) {
                const [n, d] = colors.shape;
                if (d == 4) {
                    return new ColorArray(colors.buffer);
                }
                else if (d == 3) {
                    const array = new RGBAArray(4 * n);
                    for (let i = 0, j = 0; i < d * n;) {
                        array[j++] = colors[i++];
                        array[j++] = colors[i++];
                        array[j++] = colors[i++];
                        array[j++] = 255;
                    }
                    return new ColorArray(array.buffer);
                }
            }
            else if ((colors.dtype == "float32" || colors.dtype == "float64") && colors.dimension == 2) {
                const [n, d] = colors.shape;
                if (d == 3 || d == 4) {
                    const array = new RGBAArray(4 * n);
                    for (let i = 0, j = 0; i < d * n;) {
                        array[j++] = colors[i++] * 255;
                        array[j++] = colors[i++] * 255;
                        array[j++] = colors[i++] * 255;
                        array[j++] = (d == 3 ? 1 : colors[i++]) * 255;
                    }
                    return new ColorArray(array.buffer);
                }
            }
        }
        else {
            const n = colors.length;
            const array = new RGBAArray(4 * n);
            let j = 0;
            for (const color of colors) {
                const [r, g, b, a] = color2rgba(color);
                array[j++] = r;
                array[j++] = g;
                array[j++] = b;
                array[j++] = a;
            }
            return new ColorArray(array.buffer);
        }
        throw new Error("invalid color array");
    }
    vector(values) {
        return new ColorUniformVector(values);
    }
}
ColorSpec.__name__ = "ColorSpec";
export class NDArraySpec extends DataSpec {
}
NDArraySpec.__name__ = "NDArraySpec";
export class AnySpec extends DataSpec {
}
AnySpec.__name__ = "AnySpec";
export class StringSpec extends DataSpec {
}
StringSpec.__name__ = "StringSpec";
export class NullStringSpec extends DataSpec {
}
NullStringSpec.__name__ = "NullStringSpec";
export class ArraySpec extends DataSpec {
}
ArraySpec.__name__ = "ArraySpec";
export class MarkerSpec extends DataSpec {
}
MarkerSpec.__name__ = "MarkerSpec";
export class LineJoinSpec extends DataSpec {
}
LineJoinSpec.__name__ = "LineJoinSpec";
export class LineCapSpec extends DataSpec {
}
LineCapSpec.__name__ = "LineCapSpec";
export class LineDashSpec extends DataSpec {
}
LineDashSpec.__name__ = "LineDashSpec";
export class FontSpec extends DataSpec {
    _default_override() {
        return settings.dev ? "Bokeh" : undefined;
    }
}
FontSpec.__name__ = "FontSpec";
export class FontSizeSpec extends DataSpec {
}
FontSizeSpec.__name__ = "FontSizeSpec";
export class FontStyleSpec extends DataSpec {
}
FontStyleSpec.__name__ = "FontStyleSpec";
export class TextAlignSpec extends DataSpec {
}
TextAlignSpec.__name__ = "TextAlignSpec";
export class TextBaselineSpec extends DataSpec {
}
TextBaselineSpec.__name__ = "TextBaselineSpec";
//# sourceMappingURL=properties.js.map