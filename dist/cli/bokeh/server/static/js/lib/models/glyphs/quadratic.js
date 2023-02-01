var _a;
import { LineVector } from "../../core/property_mixins";
import { inplace } from "../../core/util/projections";
import { Glyph, GlyphView } from "./glyph";
import { generic_line_vector_legend } from "./utils";
import * as p from "../../core/properties";
// Formula from: http://pomax.nihongoresources.com/pages/bezier/
//
// if segment is quadratic bezier do:
//   for both directions do:
//     if control between start and end, compute linear bounding box
//     otherwise, compute
//       bound = u(1-t)^2 + 2v(1-t)t + wt^2
//         (with t = ((u-v) / (u-2v+w)), with {u = start, v = control, w = end})
//       if control precedes start, min = bound, otherwise max = bound
function _qbb(u, v, w) {
    if (v == (u + w) / 2)
        return [u, w];
    else {
        const t = (u - v) / ((u - (2 * v)) + w);
        const bd = (u * (1 - t) ** 2) + (2 * v * (1 - t) * t) + (w * t ** 2);
        return [Math.min(u, w, bd), Math.max(u, w, bd)];
    }
}
export class QuadraticView extends GlyphView {
    _project_data() {
        inplace.project_xy(this._x0, this._y0);
        inplace.project_xy(this._x1, this._y1);
    }
    _index_data(index) {
        const { _x0, _x1, _y0, _y1, _cx, _cy, data_size } = this;
        for (let i = 0; i < data_size; i++) {
            const x0_i = _x0[i];
            const x1_i = _x1[i];
            const y0_i = _y0[i];
            const y1_i = _y1[i];
            const cx_i = _cx[i];
            const cy_i = _cy[i];
            if (!isFinite(x0_i + x1_i + y0_i + y1_i + cx_i + cy_i))
                index.add_empty();
            else {
                const [x0, x1] = _qbb(x0_i, cx_i, x1_i);
                const [y0, y1] = _qbb(y0_i, cy_i, y1_i);
                index.add_rect(x0, y0, x1, y1);
            }
        }
    }
    _render(ctx, indices, data) {
        if (this.visuals.line.doit) {
            const { sx0, sy0, sx1, sy1, scx, scy } = data ?? this;
            for (const i of indices) {
                const sx0_i = sx0[i];
                const sy0_i = sy0[i];
                const sx1_i = sx1[i];
                const sy1_i = sy1[i];
                const scx_i = scx[i];
                const scy_i = scy[i];
                if (!isFinite(sx0_i + sy0_i + sx1_i + sy1_i + scx_i + scy_i))
                    continue;
                ctx.beginPath();
                ctx.moveTo(sx0_i, sy0_i);
                ctx.quadraticCurveTo(scx_i, scy_i, sx1_i, sy1_i);
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
            }
        }
    }
    draw_legend_for_index(ctx, bbox, index) {
        generic_line_vector_legend(this.visuals, ctx, bbox, index);
    }
    scenterxy() {
        throw new Error(`${this}.scenterxy() is not implemented`);
    }
}
QuadraticView.__name__ = "QuadraticView";
export class Quadratic extends Glyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Quadratic;
Quadratic.__name__ = "Quadratic";
(() => {
    _a.prototype.default_view = QuadraticView;
    _a.define(({}) => ({
        x0: [p.XCoordinateSpec, { field: "x0" }],
        y0: [p.YCoordinateSpec, { field: "y0" }],
        x1: [p.XCoordinateSpec, { field: "x1" }],
        y1: [p.YCoordinateSpec, { field: "y1" }],
        cx: [p.XCoordinateSpec, { field: "cx" }],
        cy: [p.YCoordinateSpec, { field: "cy" }],
    }));
    _a.mixins(LineVector);
})();
//# sourceMappingURL=quadratic.js.map