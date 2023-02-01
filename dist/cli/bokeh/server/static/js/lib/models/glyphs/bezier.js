var _a;
import { LineVector } from "../../core/property_mixins";
import { Glyph, GlyphView } from "./glyph";
import { generic_line_vector_legend } from "./utils";
import { inplace } from "../../core/util/projections";
import * as p from "../../core/properties";
// algorithm adapted from http://stackoverflow.com/a/14429749/3406693
function _cbb(x0, y0, x1, y1, x2, y2, x3, y3) {
    const tvalues = [];
    const bounds = [[], []];
    for (let i = 0; i <= 2; i++) {
        let a, b, c;
        if (i === 0) {
            b = ((6 * x0) - (12 * x1)) + (6 * x2);
            a = (((-3 * x0) + (9 * x1)) - (9 * x2)) + (3 * x3);
            c = (3 * x1) - (3 * x0);
        }
        else {
            b = ((6 * y0) - (12 * y1)) + (6 * y2);
            a = (((-3 * y0) + (9 * y1)) - (9 * y2)) + (3 * y3);
            c = (3 * y1) - (3 * y0);
        }
        if (Math.abs(a) < 1e-12) { // Numerical robustness
            if (Math.abs(b) < 1e-12) // Numerical robustness
                continue;
            const t = -c / b;
            if (0 < t && t < 1)
                tvalues.push(t);
            continue;
        }
        const b2ac = (b * b) - (4 * c * a);
        const sqrtb2ac = Math.sqrt(b2ac);
        if (b2ac < 0)
            continue;
        const t1 = (-b + sqrtb2ac) / (2 * a);
        if (0 < t1 && t1 < 1)
            tvalues.push(t1);
        const t2 = (-b - sqrtb2ac) / (2 * a);
        if (0 < t2 && t2 < 1)
            tvalues.push(t2);
    }
    let j = tvalues.length;
    const jlen = j;
    while (j--) {
        const t = tvalues[j];
        const mt = 1 - t;
        const x = (mt * mt * mt * x0) + (3 * mt * mt * t * x1) + (3 * mt * t * t * x2) + (t * t * t * x3);
        bounds[0][j] = x;
        const y = (mt * mt * mt * y0) + (3 * mt * mt * t * y1) + (3 * mt * t * t * y2) + (t * t * t * y3);
        bounds[1][j] = y;
    }
    bounds[0][jlen] = x0;
    bounds[1][jlen] = y0;
    bounds[0][jlen + 1] = x3;
    bounds[1][jlen + 1] = y3;
    return [
        Math.min(...bounds[0]),
        Math.max(...bounds[1]),
        Math.max(...bounds[0]),
        Math.min(...bounds[1]),
    ];
}
export class BezierView extends GlyphView {
    _project_data() {
        inplace.project_xy(this._x0, this._y0);
        inplace.project_xy(this._x1, this._y1);
    }
    _index_data(index) {
        const { data_size, _x0, _y0, _x1, _y1, _cx0, _cy0, _cx1, _cy1 } = this;
        for (let i = 0; i < data_size; i++) {
            const x0_i = _x0[i];
            const y0_i = _y0[i];
            const x1_i = _x1[i];
            const y1_i = _y1[i];
            const cx0_i = _cx0[i];
            const cy0_i = _cy0[i];
            const cx1_i = _cx1[i];
            const cy1_i = _cy1[i];
            if (!isFinite(x0_i + x1_i + y0_i + y1_i + cx0_i + cy0_i + cx1_i + cy1_i))
                index.add_empty();
            else {
                const [x0, y0, x1, y1] = _cbb(x0_i, y0_i, x1_i, y1_i, cx0_i, cy0_i, cx1_i, cy1_i);
                index.add_rect(x0, y0, x1, y1);
            }
        }
    }
    _render(ctx, indices, data) {
        if (this.visuals.line.doit) {
            const { sx0, sy0, sx1, sy1, scx0, scy0, scx1, scy1 } = data ?? this;
            for (const i of indices) {
                const sx0_i = sx0[i];
                const sy0_i = sy0[i];
                const sx1_i = sx1[i];
                const sy1_i = sy1[i];
                const scx0_i = scx0[i];
                const scy0_i = scy0[i];
                const scx1_i = scx1[i];
                const scy1_i = scy1[i];
                if (!isFinite(sx0_i + sy0_i + sx1_i + sy1_i + scx0_i + scy0_i + scx1_i + scy1_i))
                    continue;
                ctx.beginPath();
                ctx.moveTo(sx0_i, sy0_i);
                ctx.bezierCurveTo(scx0_i, scy0_i, scx1_i, scy1_i, sx1_i, sy1_i);
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
BezierView.__name__ = "BezierView";
export class Bezier extends Glyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Bezier;
Bezier.__name__ = "Bezier";
(() => {
    _a.prototype.default_view = BezierView;
    _a.define(({}) => ({
        x0: [p.XCoordinateSpec, { field: "x0" }],
        y0: [p.YCoordinateSpec, { field: "y0" }],
        x1: [p.XCoordinateSpec, { field: "x1" }],
        y1: [p.YCoordinateSpec, { field: "y1" }],
        cx0: [p.XCoordinateSpec, { field: "cx0" }],
        cy0: [p.YCoordinateSpec, { field: "cy0" }],
        cx1: [p.XCoordinateSpec, { field: "cx1" }],
        cy1: [p.YCoordinateSpec, { field: "cy1" }],
    }));
    _a.mixins(LineVector);
})();
//# sourceMappingURL=bezier.js.map