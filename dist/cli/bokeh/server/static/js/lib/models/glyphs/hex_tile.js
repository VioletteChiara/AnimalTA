var _a;
import { Glyph, GlyphView } from "./glyph";
import * as hittest from "../../core/hittest";
import * as p from "../../core/properties";
import { LineVector, FillVector, HatchVector } from "../../core/property_mixins";
import { HexTileOrientation } from "../../core/enums";
import { inplace } from "../../core/util/projections";
import { generic_area_vector_legend } from "./utils";
import { Selection } from "../selections/selection";
export class HexTileView extends GlyphView {
    scenterxy(i) {
        const scx = this.sx[i];
        const scy = this.sy[i];
        return [scx, scy];
    }
    _set_data() {
        const { orientation, size, aspect_scale } = this.model;
        const { q, r } = this;
        const n = this.q.length;
        this._x = new Float64Array(n);
        this._y = new Float64Array(n);
        const { _x, _y } = this;
        const sqrt3 = Math.sqrt(3);
        if (orientation == "pointytop") {
            for (let i = 0; i < n; i++) {
                const q_i = q.get(i);
                const r2_i = r.get(i) / 2;
                _x[i] = size * sqrt3 * (q_i + r2_i) / aspect_scale;
                _y[i] = -3 * size * r2_i;
            }
        }
        else {
            for (let i = 0; i < n; i++) {
                const q2_i = q.get(i) / 2;
                const r_i = r.get(i);
                _x[i] = 3 * size * q2_i;
                _y[i] = -size * sqrt3 * (r_i + q2_i) * aspect_scale;
            }
        }
    }
    _project_data() {
        inplace.project_xy(this._x, this._y);
    }
    _index_data(index) {
        let ysize = this.model.size;
        let xsize = Math.sqrt(3) * ysize / 2;
        if (this.model.orientation == "flattop") {
            [xsize, ysize] = [ysize, xsize];
            ysize *= this.model.aspect_scale;
        }
        else
            xsize /= this.model.aspect_scale;
        const { data_size } = this;
        for (let i = 0; i < data_size; i++) {
            const x = this._x[i];
            const y = this._y[i];
            index.add_rect(x - xsize, y - ysize, x + xsize, y + ysize);
        }
    }
    // overriding map_data instead of _map_data because the default automatic mappings
    // for other glyphs (with cartesian coordinates) is not useful
    map_data() {
        [this.sx, this.sy] = this.renderer.coordinates.map_to_screen(this._x, this._y);
        [this.svx, this.svy] = this._get_unscaled_vertices();
    }
    _get_unscaled_vertices() {
        const size = this.model.size;
        const aspect_scale = this.model.aspect_scale;
        if (this.model.orientation == "pointytop") {
            const rscale = this.renderer.yscale;
            const hscale = this.renderer.xscale;
            const r = Math.abs(rscale.compute(0) - rscale.compute(size)); // assumes linear scale
            const h = Math.sqrt(3) / 2 * Math.abs(hscale.compute(0) - hscale.compute(size)) / aspect_scale; // assumes linear scale
            const r2 = r / 2.0;
            const svx = [0, -h, -h, 0, h, h];
            const svy = [r, r2, -r2, -r, -r2, r2];
            return [svx, svy];
        }
        else {
            const rscale = this.renderer.xscale;
            const hscale = this.renderer.yscale;
            const r = Math.abs(rscale.compute(0) - rscale.compute(size)); // assumes linear scale
            const h = Math.sqrt(3) / 2 * Math.abs(hscale.compute(0) - hscale.compute(size)) * aspect_scale; // assumes linear scale
            const r2 = r / 2.0;
            const svx = [r, r2, -r2, -r, -r2, r2];
            const svy = [0, -h, -h, 0, h, h];
            return [svx, svy];
        }
    }
    _render(ctx, indices, data) {
        const { sx, sy, svx, svy, scale } = data ?? this;
        for (const i of indices) {
            const sx_i = sx[i];
            const sy_i = sy[i];
            const scale_i = scale.get(i);
            if (!isFinite(sx_i + sy_i + scale_i))
                continue;
            ctx.translate(sx_i, sy_i);
            ctx.beginPath();
            for (let j = 0; j < 6; j++) {
                ctx.lineTo(svx[j] * scale_i, svy[j] * scale_i);
            }
            ctx.closePath();
            ctx.translate(-sx_i, -sy_i);
            this.visuals.fill.apply(ctx, i);
            this.visuals.hatch.apply(ctx, i);
            this.visuals.line.apply(ctx, i);
        }
    }
    _hit_point(geometry) {
        const { sx, sy } = geometry;
        const x = this.renderer.xscale.invert(sx);
        const y = this.renderer.yscale.invert(sy);
        const candidates = this.index.indices({ x0: x, y0: y, x1: x, y1: y });
        const indices = [];
        for (const i of candidates) {
            if (hittest.point_in_poly(sx - this.sx[i], sy - this.sy[i], this.svx, this.svy)) {
                indices.push(i);
            }
        }
        return new Selection({ indices });
    }
    _hit_span(geometry) {
        const { sx, sy } = geometry;
        let indices;
        if (geometry.direction == "v") {
            const y = this.renderer.yscale.invert(sy);
            const hr = this.renderer.plot_view.frame.bbox.h_range;
            const [x0, x1] = this.renderer.xscale.r_invert(hr.start, hr.end);
            indices = [...this.index.indices({ x0, y0: y, x1, y1: y })];
        }
        else {
            const x = this.renderer.xscale.invert(sx);
            const vr = this.renderer.plot_view.frame.bbox.v_range;
            const [y0, y1] = this.renderer.yscale.r_invert(vr.start, vr.end);
            indices = [...this.index.indices({ x0: x, y0, x1: x, y1 })];
        }
        return new Selection({ indices });
    }
    _hit_rect(geometry) {
        const { sx0, sx1, sy0, sy1 } = geometry;
        const [x0, x1] = this.renderer.xscale.r_invert(sx0, sx1);
        const [y0, y1] = this.renderer.yscale.r_invert(sy0, sy1);
        const indices = [...this.index.indices({ x0, x1, y0, y1 })];
        return new Selection({ indices });
    }
    draw_legend_for_index(ctx, bbox, index) {
        generic_area_vector_legend(this.visuals, ctx, bbox, index);
    }
}
HexTileView.__name__ = "HexTileView";
export class HexTile extends Glyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = HexTile;
HexTile.__name__ = "HexTile";
(() => {
    _a.prototype.default_view = HexTileView;
    _a.mixins([LineVector, FillVector, HatchVector]);
    _a.define(({ Number }) => ({
        r: [p.NumberSpec, { field: "r" }],
        q: [p.NumberSpec, { field: "q" }],
        scale: [p.NumberSpec, 1.0],
        size: [Number, 1.0],
        aspect_scale: [Number, 1.0],
        orientation: [HexTileOrientation, "pointytop"],
    }));
    _a.override({ line_color: null });
})();
//# sourceMappingURL=hex_tile.js.map