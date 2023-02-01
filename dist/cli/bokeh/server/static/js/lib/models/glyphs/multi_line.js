var _a;
import { inplace } from "../../core/util/projections";
import { LineVector } from "../../core/property_mixins";
import * as hittest from "../../core/hittest";
import * as p from "../../core/properties";
import { minmax2 } from "../../core/util/arrayable";
import { to_object } from "../../core/util/object";
import { Glyph, GlyphView } from "./glyph";
import { generic_line_vector_legend, line_interpolation } from "./utils";
import { Selection } from "../selections/selection";
export class MultiLineView extends GlyphView {
    _project_data() {
        inplace.project_xy(this._xs.array, this._ys.array);
    }
    _index_data(index) {
        const { data_size } = this;
        for (let i = 0; i < data_size; i++) {
            const xsi = this._xs.get(i);
            const ysi = this._ys.get(i);
            const [x0, x1, y0, y1] = minmax2(xsi, ysi);
            index.add_rect(x0, y0, x1, y1);
        }
    }
    _render(ctx, indices, data) {
        const { sxs, sys } = data ?? this;
        for (const i of indices) {
            const sx = sxs.get(i);
            const sy = sys.get(i);
            const n = Math.min(sx.length, sy.length);
            let move = true;
            ctx.beginPath();
            for (let j = 0; j < n; j++) {
                const sx_j = sx[j];
                const sy_j = sy[j];
                if (!isFinite(sx_j + sy_j))
                    move = true;
                else {
                    if (move) {
                        ctx.moveTo(sx_j, sy_j);
                        move = false;
                    }
                    else
                        ctx.lineTo(sx_j, sy_j);
                }
            }
            this.visuals.line.set_vectorize(ctx, i);
            ctx.stroke();
        }
    }
    _hit_point(geometry) {
        const point = { x: geometry.sx, y: geometry.sy };
        let shortest = 9999;
        const hits = new Map();
        for (let i = 0, end = this.sxs.length; i < end; i++) {
            const threshold = Math.max(2, this.line_width.get(i) / 2);
            const sxsi = this.sxs.get(i);
            const sysi = this.sys.get(i);
            let points = null;
            for (let j = 0, endj = sxsi.length - 1; j < endj; j++) {
                const p0 = { x: sxsi[j], y: sysi[j] };
                const p1 = { x: sxsi[j + 1], y: sysi[j + 1] };
                const dist = hittest.dist_to_segment(point, p0, p1);
                if (dist < threshold && dist < shortest) {
                    shortest = dist;
                    points = [j];
                }
            }
            if (points != null) {
                hits.set(i, points);
            }
        }
        return new Selection({
            indices: [...hits.keys()],
            multiline_indices: to_object(hits), // TODO: remove to_object()
        });
    }
    _hit_span(geometry) {
        const { sx, sy } = geometry;
        let val;
        let vs;
        if (geometry.direction == "v") {
            val = this.renderer.yscale.invert(sy);
            vs = this._ys;
        }
        else {
            val = this.renderer.xscale.invert(sx);
            vs = this._xs;
        }
        const hits = new Map();
        for (let i = 0, end = vs.length; i < end; i++) {
            const vsi = vs.get(i);
            const points = [];
            for (let j = 0, endj = vsi.length - 1; j < endj; j++) {
                if (vsi[j] <= val && val <= vsi[j + 1])
                    points.push(j);
            }
            if (points.length > 0) {
                hits.set(i, points);
            }
        }
        return new Selection({
            indices: [...hits.keys()],
            multiline_indices: to_object(hits), // TODO: remove to_object()
        });
    }
    get_interpolation_hit(i, point_i, geometry) {
        const xsi = this._xs.get(i);
        const ysi = this._ys.get(i);
        const x2 = xsi[point_i];
        const y2 = ysi[point_i];
        const x3 = xsi[point_i + 1];
        const y3 = ysi[point_i + 1];
        return line_interpolation(this.renderer, geometry, x2, y2, x3, y3);
    }
    draw_legend_for_index(ctx, bbox, index) {
        generic_line_vector_legend(this.visuals, ctx, bbox, index);
    }
    scenterxy() {
        throw new Error(`${this}.scenterxy() is not implemented`);
    }
}
MultiLineView.__name__ = "MultiLineView";
export class MultiLine extends Glyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = MultiLine;
MultiLine.__name__ = "MultiLine";
(() => {
    _a.prototype.default_view = MultiLineView;
    _a.define(({}) => ({
        xs: [p.XCoordinateSeqSpec, { field: "xs" }],
        ys: [p.YCoordinateSeqSpec, { field: "ys" }],
    }));
    _a.mixins(LineVector);
})();
//# sourceMappingURL=multi_line.js.map