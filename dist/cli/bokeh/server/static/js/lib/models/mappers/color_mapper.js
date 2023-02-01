var _a;
import { Mapper } from "./mapper";
import { Signal0 } from "../../core/signaling";
import { ColorArray } from "../../core/types";
import { color2rgba, encode_rgba } from "../../core/util/color";
import { to_big_endian } from "../../core/util/platform";
// export for testing
export function _convert_color(color) {
    return encode_rgba(color2rgba(color));
}
// export for testing
export function _convert_palette(palette) {
    const new_palette = new Uint32Array(palette.length);
    for (let i = 0, end = palette.length; i < end; i++)
        new_palette[i] = _convert_color(palette[i]);
    return new_palette;
}
export class ColorMapper extends Mapper {
    constructor(attrs) {
        super(attrs);
    }
    initialize() {
        super.initialize();
        this.metrics_change = new Signal0(this, "metrics_change");
    }
    v_compute(xs) {
        const values = new Array(xs.length);
        this._v_compute(xs, values, this.palette, this._colors((c) => c));
        return values;
    }
    get rgba_mapper() {
        const self = this;
        const palette = _convert_palette(this.palette);
        const colors = this._colors(_convert_color);
        return {
            v_compute(xs) {
                const values = new ColorArray(xs.length);
                self._v_compute(xs, values, palette, colors);
                return new Uint8ClampedArray(to_big_endian(values).buffer);
            },
        };
    }
    _colors(conv) {
        return { nan_color: conv(this.nan_color) };
    }
}
_a = ColorMapper;
ColorMapper.__name__ = "ColorMapper";
(() => {
    _a.define(({ Color, Array }) => ({
        palette: [Array(Color)],
        nan_color: [Color, "gray"],
    }));
})();
//# sourceMappingURL=color_mapper.js.map