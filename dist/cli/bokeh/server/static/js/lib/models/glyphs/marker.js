var _a;
import { XYGlyph, XYGlyphView } from "./xy_glyph";
import { LineVector, FillVector, HatchVector } from "../../core/property_mixins";
import * as hittest from "../../core/hittest";
import * as p from "../../core/properties";
import { range } from "../../core/util/array";
import { Selection } from "../selections/selection";
export class MarkerView extends XYGlyphView {
    _render(ctx, indices, data) {
        const { sx, sy, size, angle } = data ?? this;
        for (const i of indices) {
            const sx_i = sx[i];
            const sy_i = sy[i];
            const size_i = size.get(i);
            const angle_i = angle.get(i);
            if (!isFinite(sx_i + sy_i + size_i + angle_i))
                continue;
            const r = size_i / 2;
            ctx.beginPath();
            ctx.translate(sx_i, sy_i);
            if (angle_i)
                ctx.rotate(angle_i);
            this._render_one(ctx, i, r, this.visuals);
            if (angle_i)
                ctx.rotate(-angle_i);
            ctx.translate(-sx_i, -sy_i);
        }
    }
    _mask_data() {
        // dilate the inner screen region by max_size and map back to data space for use in spatial query
        const { x_target, y_target } = this.renderer.plot_view.frame;
        const hr = x_target.widen(this.max_size).map((x) => this.renderer.xscale.invert(x));
        const vr = y_target.widen(this.max_size).map((y) => this.renderer.yscale.invert(y));
        return this.index.indices({
            x0: hr.start, x1: hr.end,
            y0: vr.start, y1: vr.end,
        });
    }
    _hit_point(geometry) {
        const { sx, sy } = geometry;
        const { max_size } = this;
        const { hit_dilation } = this.model;
        const sx0 = sx - max_size * hit_dilation;
        const sx1 = sx + max_size * hit_dilation;
        const [x0, x1] = this.renderer.xscale.r_invert(sx0, sx1);
        const sy0 = sy - max_size * hit_dilation;
        const sy1 = sy + max_size * hit_dilation;
        const [y0, y1] = this.renderer.yscale.r_invert(sy0, sy1);
        const candidates = this.index.indices({ x0, x1, y0, y1 });
        const indices = [];
        for (const i of candidates) {
            const s2 = this.size.get(i) / 2 * hit_dilation;
            if (Math.abs(this.sx[i] - sx) <= s2 && Math.abs(this.sy[i] - sy) <= s2) {
                indices.push(i);
            }
        }
        return new Selection({ indices });
    }
    _hit_span(geometry) {
        const { sx, sy } = geometry;
        const bounds = this.bounds();
        const ms = this.max_size / 2;
        let x0, x1, y0, y1;
        if (geometry.direction == "h") {
            y0 = bounds.y0;
            y1 = bounds.y1;
            const sx0 = sx - ms;
            const sx1 = sx + ms;
            [x0, x1] = this.renderer.xscale.r_invert(sx0, sx1);
        }
        else {
            x0 = bounds.x0;
            x1 = bounds.x1;
            const sy0 = sy - ms;
            const sy1 = sy + ms;
            [y0, y1] = this.renderer.yscale.r_invert(sy0, sy1);
        }
        const indices = [...this.index.indices({ x0, x1, y0, y1 })];
        return new Selection({ indices });
    }
    _hit_rect(geometry) {
        const { sx0, sx1, sy0, sy1 } = geometry;
        const [x0, x1] = this.renderer.xscale.r_invert(sx0, sx1);
        const [y0, y1] = this.renderer.yscale.r_invert(sy0, sy1);
        const indices = [...this.index.indices({ x0, x1, y0, y1 })];
        return new Selection({ indices });
    }
    _hit_poly(geometry) {
        const { sx, sy } = geometry;
        // TODO (bev) use spatial index to pare candidate list
        const candidates = range(0, this.sx.length);
        const indices = [];
        for (let i = 0, end = candidates.length; i < end; i++) {
            const index = candidates[i];
            if (hittest.point_in_poly(this.sx[i], this.sy[i], sx, sy)) {
                indices.push(index);
            }
        }
        return new Selection({ indices });
    }
    _get_legend_args({ x0, x1, y0, y1 }, index) {
        // using objects like this seems a little wonky, since the keys are coerced to strings, but it works
        const n = index + 1;
        const sx = new Array(n);
        const sy = new Array(n);
        sx[index] = (x0 + x1) / 2;
        sy[index] = (y0 + y1) / 2;
        const vsize = Math.min(Math.abs(x1 - x0), Math.abs(y1 - y0)) * 0.4;
        const size = new p.UniformScalar(vsize, n);
        const angle = new p.UniformScalar(0, n); // don't attempt to match glyph angle
        return { sx, sy, size, angle };
    }
    draw_legend_for_index(ctx, { x0, x1, y0, y1 }, index) {
        const args = this._get_legend_args({ x0, x1, y0, y1 }, index);
        this._render(ctx, [index], args); // XXX
    }
}
MarkerView.__name__ = "MarkerView";
export class Marker extends XYGlyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Marker;
Marker.__name__ = "Marker";
(() => {
    _a.mixins([LineVector, FillVector, HatchVector]);
    _a.define(({ Number }) => ({
        size: [p.ScreenSizeSpec, { value: 4 }],
        angle: [p.AngleSpec, 0],
        hit_dilation: [Number, 1.0],
    }));
})();
//# sourceMappingURL=marker.js.map