var _a, _b, _c, _d, _e, _f;
import tz from "timezone";
import * as Numbro from "@bokeh/numbro";
import { _ } from "underscore.template";
import { div, i } from "../../../core/dom";
import { FontStyle, TextAlign, RoundingFunction } from "../../../core/enums";
import { isString } from "../../../core/util/types";
import { to_fixed } from "../../../core/util/string";
import { color2css } from "../../../core/util/color";
import { Model } from "../../../model";
export class CellFormatter extends Model {
    constructor(attrs) {
        super(attrs);
    }
    doFormat(_row, _cell, value, _columnDef, _dataContext) {
        if (value == null)
            return "";
        else
            return `${value}`.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }
}
CellFormatter.__name__ = "CellFormatter";
export class StringFormatter extends CellFormatter {
    constructor(attrs) {
        super(attrs);
    }
    doFormat(_row, _cell, value, _columnDef, _dataContext) {
        const { font_style, text_align, text_color } = this;
        const text = div(value == null ? "" : `${value}`);
        switch (font_style) {
            case "bold":
                text.style.fontWeight = "bold";
                break;
            case "italic":
                text.style.fontStyle = "italic";
                break;
        }
        if (text_align != null)
            text.style.textAlign = text_align;
        if (text_color != null)
            text.style.color = color2css(text_color);
        return text.outerHTML;
    }
}
_a = StringFormatter;
StringFormatter.__name__ = "StringFormatter";
(() => {
    _a.define(({ Color, Nullable }) => ({
        font_style: [FontStyle, "normal"],
        text_align: [TextAlign, "left"],
        text_color: [Nullable(Color), null],
    }));
})();
export class ScientificFormatter extends StringFormatter {
    constructor(attrs) {
        super(attrs);
    }
    get scientific_limit_low() {
        return 10.0 ** this.power_limit_low;
    }
    get scientific_limit_high() {
        return 10.0 ** this.power_limit_high;
    }
    doFormat(row, cell, value, columnDef, dataContext) {
        const need_sci = Math.abs(value) <= this.scientific_limit_low || Math.abs(value) >= this.scientific_limit_high;
        let precision = this.precision;
        // toExponential does not handle precision values < 0 correctly
        if (precision < 1) {
            precision = 1;
        }
        if ((value == null || isNaN(value)) && this.nan_format != null)
            value = this.nan_format;
        else if (value == 0)
            value = to_fixed(value, 1);
        else if (need_sci)
            value = value.toExponential(precision);
        else
            value = to_fixed(value, precision);
        // add StringFormatter formatting
        return super.doFormat(row, cell, value, columnDef, dataContext);
    }
}
_b = ScientificFormatter;
ScientificFormatter.__name__ = "ScientificFormatter";
(() => {
    _b.define(({ Number, String, Nullable }) => ({
        nan_format: [Nullable(String), null],
        precision: [Number, 10],
        power_limit_high: [Number, 5],
        power_limit_low: [Number, -3],
    }));
})();
export class NumberFormatter extends StringFormatter {
    constructor(attrs) {
        super(attrs);
    }
    doFormat(row, cell, value, columnDef, dataContext) {
        const { format, language, nan_format } = this;
        const rounding = (() => {
            switch (this.rounding) {
                case "round":
                case "nearest": return Math.round;
                case "floor":
                case "rounddown": return Math.floor;
                case "ceil":
                case "roundup": return Math.ceil;
            }
        })();
        if ((value == null || isNaN(value)) && nan_format != null)
            value = nan_format;
        else
            value = Numbro.format(value, format, language, rounding);
        return super.doFormat(row, cell, value, columnDef, dataContext);
    }
}
_c = NumberFormatter;
NumberFormatter.__name__ = "NumberFormatter";
(() => {
    _c.define(({ String, Nullable }) => ({
        format: [String, "0,0"],
        language: [String, "en"],
        rounding: [RoundingFunction, "round"],
        nan_format: [Nullable(String), null],
    }));
})();
export class BooleanFormatter extends CellFormatter {
    constructor(attrs) {
        super(attrs);
    }
    doFormat(_row, _cell, value, _columnDef, _dataContext) {
        return !!value ? i({ class: this.icon }).outerHTML : "";
    }
}
_d = BooleanFormatter;
BooleanFormatter.__name__ = "BooleanFormatter";
(() => {
    _d.define(({ String }) => ({
        icon: [String, "check"],
    }));
})();
export class DateFormatter extends StringFormatter {
    constructor(attrs) {
        super(attrs);
    }
    getFormat() {
        // using definitions provided here: https://api.jqueryui.com/datepicker/
        // except not implementing TICKS
        switch (this.format) {
            case "ATOM":
            case "W3C":
            case "RFC-3339":
            case "ISO-8601":
                return "%Y-%m-%d";
            case "COOKIE":
                return "%a, %d %b %Y";
            case "RFC-850":
                return "%A, %d-%b-%y";
            case "RFC-1123":
            case "RFC-2822":
                return "%a, %e %b %Y";
            case "RSS":
            case "RFC-822":
            case "RFC-1036":
                return "%a, %e %b %y";
            case "TIMESTAMP":
                return undefined;
            default:
                return this.format;
        }
    }
    doFormat(row, cell, value, columnDef, dataContext) {
        const { nan_format } = this;
        value = isString(value) ? parseInt(value, 10) : value;
        let date;
        // Handle null, NaN and NaT
        if ((value == null || isNaN(value) || value === -9223372036854776) && nan_format != null)
            date = nan_format;
        else
            date = value == null ? "" : tz(value, this.getFormat());
        return super.doFormat(row, cell, date, columnDef, dataContext);
    }
}
_e = DateFormatter;
DateFormatter.__name__ = "DateFormatter";
(() => {
    _e.define(({ String, Nullable }) => ({
        format: [String, "ISO-8601"],
        nan_format: [Nullable(String), null],
    }));
})();
export class HTMLTemplateFormatter extends CellFormatter {
    constructor(attrs) {
        super(attrs);
    }
    doFormat(_row, _cell, value, _columnDef, dataContext) {
        const { template } = this;
        if (value == null)
            return "";
        else {
            const compiled_template = _.template(template);
            const context = { ...dataContext, value };
            return compiled_template(context);
        }
    }
}
_f = HTMLTemplateFormatter;
HTMLTemplateFormatter.__name__ = "HTMLTemplateFormatter";
(() => {
    _f.define(({ String }) => ({
        template: [String, "<%= value %>"],
    }));
})();
//# sourceMappingURL=cell_formatters.js.map