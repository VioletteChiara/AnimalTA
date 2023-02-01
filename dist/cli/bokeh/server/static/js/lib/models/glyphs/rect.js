var _a;
import { CenterRotatable, CenterRotatableView } from "./center_rotatable";
import { generic_area_vector_legend } from "./utils";
import { ScreenArray, to_screen, infer_type } from "../../core/types";
import { max } from "../../core/util/arrayable";
import { Selection } from "../selections/selection";
export class RectView extends CenterRotatableView {
    async lazy_initialize() {
        await super.lazy_initialize();
        const { webgl } = this.renderer.plot_view.canvas_view;
        if (webgl?.regl_wrapper.has_webgl) {
            const { RectGL } = await import("./webgl/rect");
            this.glglyph = new RectGL(webgl.regl_wrapper, this);
        }
    }
    _map_data() {
        if (this.model.properties.width.units == "data")
            [this.sw, this.sx0] = this._map_dist_corner_for_data_side_length(this._x, this.width, this.renderer.xscale);
        else {
            this.sw = to_screen(this.width);
            const n = this.sx.length;
            this.sx0 = new ScreenArray(n);
            for (let i = 0; i < n; i++)
                this.sx0[i] = this.sx[i] - this.sw[i] / 2;
        }
        if (this.model.properties.height.units == "data")
            [this.sh, this.sy1] = this._map_dist_corner_for_data_side_length(this._y, this.height, this.renderer.yscale);
        else {
            this.sh = to_screen(this.height);
            const n = this.sy.length;
            this.sy1 = new ScreenArray(n);
            for (let i = 0; i < n; i++)
                this.sy1[i] = this.sy[i] - this.sh[i] / 2;
        }
        const n = this.sw.length;
        this.ssemi_diag = new ScreenArray(n);
        for (let i = 0; i < n; i++)
            this.ssemi_diag[i] = Math.sqrt((this.sw[i] / 2 * this.sw[i]) / 2 + (this.sh[i] / 2 * this.sh[i]) / 2);
    }
    _render(ctx, indices, data) {
        const { sx, sy, sx0, sy1, sw, sh, angle } = data ?? this;
        for (const i of indices) {
            const sx_i = sx[i];
            const sy_i = sy[i];
            const sx0_i = sx0[i];
            const sy1_i = sy1[i];
            const sw_i = sw[i];
            const sh_i = sh[i];
            const angle_i = angle.get(i);
            if (!isFinite(sx_i + sy_i + sx0_i + sy1_i + sw_i + sh_i + angle_i))
                continue;
            if (sw_i == 0 || sh_i == 0)
                continue;
            ctx.beginPath();
            if (angle_i) {
                ctx.translate(sx_i, sy_i);
                ctx.rotate(angle_i);
                ctx.rect(-sw_i / 2, -sh_i / 2, sw_i, sh_i);
                ctx.rotate(-angle_i);
                ctx.translate(-sx_i, -sy_i);
            }
            else
                ctx.rect(sx0_i, sy1_i, sw_i, sh_i);
            this.visuals.fill.apply(ctx, i);
            this.visuals.hatch.apply(ctx, i);
            this.visuals.line.apply(ctx, i);
        }
    }
    _hit_rect(geometry) {
        return this._hit_rect_against_index(geometry);
    }
    _hit_point(geometry) {
        let { sx, sy } = geometry;
        const x = this.renderer.xscale.invert(sx);
        const y = this.renderer.yscale.invert(sy);
        const n = this.sx0.length;
        const scenter_x = new ScreenArray(n);
        for (let i = 0; i < n; i++) {
            scenter_x[i] = this.sx0[i] + this.sw[i] / 2;
        }
        const scenter_y = new ScreenArray(n);
        for (let i = 0; i < n; i++) {
            scenter_y[i] = this.sy1[i] + this.sh[i] / 2;
        }
        const max_x2_ddist = max(this._ddist(0, scenter_x, this.ssemi_diag));
        const max_y2_ddist = max(this._ddist(1, scenter_y, this.ssemi_diag));
        const x0 = x - max_x2_ddist;
        const x1 = x + max_x2_ddist;
        const y0 = y - max_y2_ddist;
        const y1 = y + max_y2_ddist;
        let width_in;
        let height_in;
        const indices = [];
        for (const i of this.index.indices({ x0, x1, y0, y1 })) {
            const angle_i = this.angle.get(i);
            if (angle_i) {
                const s = Math.sin(-angle_i);
                const c = Math.cos(-angle_i);
                const px = c * (sx - this.sx[i]) - s * (sy - this.sy[i]) + this.sx[i];
                const py = s * (sx - this.sx[i]) + c * (sy - this.sy[i]) + this.sy[i];
                sx = px;
                sy = py;
                width_in = Math.abs(this.sx[i] - sx) <= this.sw[i] / 2;
                height_in = Math.abs(this.sy[i] - sy) <= this.sh[i] / 2;
            }
            else {
                const dx = sx - this.sx0[i];
                const dy = sy - this.sy1[i];
                width_in = 0 <= dx && dx <= this.sw[i];
                height_in = 0 <= dy && dy <= this.sh[i];
            }
            if (width_in && height_in) {
                indices.push(i);
            }
        }
        return new Selection({ indices });
    }
    _map_dist_corner_for_data_side_length(coord, side_length, scale) {
        const n = coord.length;
        const pt0 = new Float64Array(n);
        const pt1 = new Float64Array(n);
        for (let i = 0; i < n; i++) {
            const coord_i = coord[i];
            const half_side_length_i = side_length.get(i) / 2;
            pt0[i] = coord_i - half_side_length_i;
            pt1[i] = coord_i + half_side_length_i;
        }
        const spt0 = scale.v_compute(pt0);
        const spt1 = scale.v_compute(pt1);
        const sside_length = this.sdist(scale, pt0, side_length, "edge", this.model.dilate);
        let spt_corner = spt0;
        for (let i = 0; i < n; i++) {
            const spt0i = spt0[i];
            const spt1i = spt1[i];
            if (!isNaN(spt0i + spt1i) && spt0i != spt1i) {
                spt_corner = spt0i < spt1i ? spt0 : spt1;
                break;
            }
        }
        return [sside_length, spt_corner];
    }
    _ddist(dim, spts, spans) {
        const ArrayType = infer_type(spts, spans);
        const scale = dim == 0 ? this.renderer.xscale : this.renderer.yscale;
        const spt0 = spts;
        const m = spt0.length;
        const spt1 = new ArrayType(m);
        for (let i = 0; i < m; i++)
            spt1[i] = spt0[i] + spans[i];
        const pt0 = scale.v_invert(spt0);
        const pt1 = scale.v_invert(spt1);
        const n = pt0.length;
        const ddist = new ArrayType(n);
        for (let i = 0; i < n; i++)
            ddist[i] = Math.abs(pt1[i] - pt0[i]);
        return ddist;
    }
    draw_legend_for_index(ctx, bbox, index) {
        generic_area_vector_legend(this.visuals, ctx, bbox, index);
    }
}
RectView.__name__ = "RectView";
export class Rect extends CenterRotatable {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Rect;
Rect.__name__ = "Rect";
(() => {
    _a.prototype.default_view = RectView;
    _a.define(({ Boolean }) => ({
        dilate: [Boolean, false],
    }));
})();
//# sourceMappingURL=rect.js.map