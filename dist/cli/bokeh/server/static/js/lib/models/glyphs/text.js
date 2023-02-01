var _a;
import { XYGlyph, XYGlyphView } from "./xy_glyph";
import { TextVector } from "../../core/property_mixins";
import * as hittest from "../../core/hittest";
import * as p from "../../core/properties";
import { font_metrics } from "../../core/util/text";
import { assert } from "../../core/util/assert";
import { Selection } from "../selections/selection";
export class TextView extends XYGlyphView {
    _rotate_point(x, y, xoff, yoff, angle) {
        const sxr = (x - xoff) * Math.cos(angle) - (y - yoff) * Math.sin(angle) + xoff;
        const syr = (x - xoff) * Math.sin(angle) + (y - yoff) * Math.cos(angle) + yoff;
        return [sxr, syr];
    }
    _text_bounds(x0, y0, width, height) {
        const xvals = [x0, x0 + width, x0 + width, x0, x0];
        const yvals = [y0, y0, y0 - height, y0 - height, y0];
        return [xvals, yvals];
    }
    _render(ctx, indices, data) {
        const { sx, sy, x_offset, y_offset, angle, text } = data ?? this;
        this._sys = [];
        this._sxs = [];
        for (const i of indices) {
            const sxs_i = this._sxs[i] = [];
            const sys_i = this._sys[i] = [];
            const sx_i = sx[i];
            const sy_i = sy[i];
            const x_offset_i = x_offset.get(i);
            const y_offset_i = y_offset.get(i);
            const angle_i = angle.get(i);
            const text_i = text.get(i);
            if (!isFinite(sx_i + sy_i + x_offset_i + y_offset_i + angle_i) || text_i == null)
                continue;
            if (this.visuals.text.doit) {
                const text = `${text_i}`;
                ctx.save();
                ctx.translate(sx_i + x_offset_i, sy_i + y_offset_i);
                ctx.rotate(angle_i);
                this.visuals.text.set_vectorize(ctx, i);
                const font = this.visuals.text.font_value(i);
                const { height } = font_metrics(font);
                const line_height = this.text_line_height.get(i) * height;
                if (text.indexOf("\n") == -1) {
                    ctx.fillText(text, 0, 0);
                    const x0 = sx_i + x_offset_i;
                    const y0 = sy_i + y_offset_i;
                    const width = ctx.measureText(text).width;
                    const [xvalues, yvalues] = this._text_bounds(x0, y0, width, line_height);
                    sxs_i.push(xvalues);
                    sys_i.push(yvalues);
                }
                else {
                    const lines = text.split("\n");
                    const block_height = line_height * lines.length;
                    const baseline = this.text_baseline.get(i);
                    let y;
                    switch (baseline) {
                        case "top": {
                            y = 0;
                            break;
                        }
                        case "middle": {
                            y = (-block_height / 2) + (line_height / 2);
                            break;
                        }
                        case "bottom": {
                            y = -block_height + line_height;
                            break;
                        }
                        default: {
                            y = 0;
                            console.warn(`'${baseline}' baseline not supported with multi line text`);
                        }
                    }
                    for (const line of lines) {
                        ctx.fillText(line, 0, y);
                        const x0 = sx_i + x_offset_i;
                        const y0 = y + sy_i + y_offset_i;
                        const width = ctx.measureText(line).width;
                        const [xvalues, yvalues] = this._text_bounds(x0, y0, width, line_height);
                        sxs_i.push(xvalues);
                        sys_i.push(yvalues);
                        y += line_height;
                    }
                }
                ctx.restore();
            }
        }
    }
    _hit_point(geometry) {
        const { sx, sy } = geometry;
        const indices = [];
        for (let i = 0; i < this._sxs.length; i++) {
            const sxs = this._sxs[i];
            const sys = this._sys[i];
            const n = sxs.length;
            for (let j = 0, endj = n; j < endj; j++) {
                const [sxr, syr] = this._rotate_point(sx, sy, sxs[n - 1][0], sys[n - 1][0], -this.angle.get(i));
                if (hittest.point_in_poly(sxr, syr, sxs[j], sys[j])) {
                    indices.push(i);
                }
            }
        }
        return new Selection({ indices });
    }
    scenterxy(i) {
        const sxs = this._sxs[i];
        const sys = this._sys[i];
        assert(sxs.length != 0 && sys.length != 0);
        const sx0 = sxs[0][0];
        const sy0 = sys[0][0];
        const sxc = (sxs[0][2] + sx0) / 2;
        const syc = (sys[0][2] + sy0) / 2;
        const [sxcr, sycr] = this._rotate_point(sxc, syc, sx0, sy0, this.angle.get(i));
        return [sxcr, sycr];
    }
}
TextView.__name__ = "TextView";
export class Text extends XYGlyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Text;
Text.__name__ = "Text";
(() => {
    _a.prototype.default_view = TextView;
    _a.mixins(TextVector);
    _a.define(({}) => ({
        text: [p.NullStringSpec, { field: "text" }],
        angle: [p.AngleSpec, 0],
        x_offset: [p.NumberSpec, 0],
        y_offset: [p.NumberSpec, 0],
    }));
})();
//# sourceMappingURL=text.js.map