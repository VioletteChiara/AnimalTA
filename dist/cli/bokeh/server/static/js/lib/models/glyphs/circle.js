var _a;
import { XYGlyph, XYGlyphView } from "./xy_glyph";
import { LineVector, FillVector, HatchVector } from "../../core/property_mixins";
import { ScreenArray, to_screen } from "../../core/types";
import { RadiusDimension } from "../../core/enums";
import * as hittest from "../../core/hittest";
import * as p from "../../core/properties";
import { range } from "../../core/util/array";
import { map, max } from "../../core/util/arrayable";
import { Selection } from "../selections/selection";
export class CircleView extends XYGlyphView {
    async lazy_initialize() {
        await super.lazy_initialize();
        const { webgl } = this.renderer.plot_view.canvas_view;
        if (webgl?.regl_wrapper.has_webgl) {
            const { MarkerGL } = await import("./webgl/markers");
            this.glglyph = new MarkerGL(webgl.regl_wrapper, this, "circle");
        }
    }
    get use_radius() {
        return !(this.radius.is_Scalar() && isNaN(this.radius.value));
    }
    _set_data(indices) {
        super._set_data(indices);
        const max_size = (() => {
            if (this.use_radius)
                return 2 * this.max_radius;
            else {
                const { size } = this;
                return size.is_Scalar() ? size.value : max(size.array);
            }
        })();
        this._configure("max_size", { value: max_size });
    }
    _map_data() {
        // XXX: Order is important here: size is always present (at least
        // a default), but radius is only present if a user specifies it.
        if (this.use_radius) {
            if (this.model.properties.radius.units == "data") {
                switch (this.model.radius_dimension) {
                    case "x": {
                        this.sradius = this.sdist(this.renderer.xscale, this._x, this.radius);
                        break;
                    }
                    case "y": {
                        this.sradius = this.sdist(this.renderer.yscale, this._y, this.radius);
                        break;
                    }
                    case "max": {
                        const sradius_x = this.sdist(this.renderer.xscale, this._x, this.radius);
                        const sradius_y = this.sdist(this.renderer.yscale, this._y, this.radius);
                        this.sradius = map(sradius_x, (s, i) => Math.max(s, sradius_y[i]));
                        break;
                    }
                    case "min": {
                        const sradius_x = this.sdist(this.renderer.xscale, this._x, this.radius);
                        const sradius_y = this.sdist(this.renderer.yscale, this._y, this.radius);
                        this.sradius = map(sradius_x, (s, i) => Math.min(s, sradius_y[i]));
                        break;
                    }
                }
            }
            else
                this.sradius = to_screen(this.radius);
        }
        else {
            const ssize = ScreenArray.from(this.size);
            this.sradius = map(ssize, (s) => s / 2);
        }
    }
    _mask_data() {
        const { frame } = this.renderer.plot_view;
        const shr = frame.x_target;
        const svr = frame.y_target;
        let hr;
        let vr;
        if (this.use_radius && this.model.properties.radius.units == "data") {
            hr = shr.map((x) => this.renderer.xscale.invert(x)).widen(this.max_radius);
            vr = svr.map((y) => this.renderer.yscale.invert(y)).widen(this.max_radius);
        }
        else {
            hr = shr.widen(this.max_size).map((x) => this.renderer.xscale.invert(x));
            vr = svr.widen(this.max_size).map((y) => this.renderer.yscale.invert(y));
        }
        return this.index.indices({
            x0: hr.start, x1: hr.end,
            y0: vr.start, y1: vr.end,
        });
    }
    _render(ctx, indices, data) {
        const { sx, sy, sradius } = data ?? this;
        for (const i of indices) {
            const sx_i = sx[i];
            const sy_i = sy[i];
            const sradius_i = sradius[i];
            if (!isFinite(sx_i + sy_i + sradius_i))
                continue;
            ctx.beginPath();
            ctx.arc(sx_i, sy_i, sradius_i, 0, 2 * Math.PI, false);
            this.visuals.fill.apply(ctx, i);
            this.visuals.hatch.apply(ctx, i);
            this.visuals.line.apply(ctx, i);
        }
    }
    _hit_point(geometry) {
        const { sx, sy } = geometry;
        const x = this.renderer.xscale.invert(sx);
        const y = this.renderer.yscale.invert(sy);
        const { hit_dilation } = this.model;
        let x0, x1, y0, y1;
        if (this.use_radius && this.model.properties.radius.units == "data") {
            x0 = x - this.max_radius * hit_dilation;
            x1 = x + this.max_radius * hit_dilation;
            y0 = y - this.max_radius * hit_dilation;
            y1 = y + this.max_radius * hit_dilation;
        }
        else {
            const sx0 = sx - this.max_size * hit_dilation;
            const sx1 = sx + this.max_size * hit_dilation;
            [x0, x1] = this.renderer.xscale.r_invert(sx0, sx1);
            const sy0 = sy - this.max_size * hit_dilation;
            const sy1 = sy + this.max_size * hit_dilation;
            [y0, y1] = this.renderer.yscale.r_invert(sy0, sy1);
        }
        const candidates = this.index.indices({ x0, x1, y0, y1 });
        const indices = [];
        if (this.use_radius && this.model.properties.radius.units == "data") {
            for (const i of candidates) {
                const r2 = (this.sradius[i] * hit_dilation) ** 2;
                const [sx0, sx1] = this.renderer.xscale.r_compute(x, this._x[i]);
                const [sy0, sy1] = this.renderer.yscale.r_compute(y, this._y[i]);
                const dist = (sx0 - sx1) ** 2 + (sy0 - sy1) ** 2;
                if (dist <= r2) {
                    indices.push(i);
                }
            }
        }
        else {
            for (const i of candidates) {
                const r2 = (this.sradius[i] * hit_dilation) ** 2;
                const dist = (this.sx[i] - sx) ** 2 + (this.sy[i] - sy) ** 2;
                if (dist <= r2) {
                    indices.push(i);
                }
            }
        }
        return new Selection({ indices });
    }
    _hit_span(geometry) {
        const { sx, sy } = geometry;
        const bounds = this.bounds();
        let x0, x1, y0, y1;
        if (geometry.direction == "h") {
            // use circle bounds instead of current pointer y coordinates
            let sx0, sx1;
            y0 = bounds.y0;
            y1 = bounds.y1;
            if (this.use_radius && this.model.properties.radius.units == "data") {
                sx0 = sx - this.max_radius;
                sx1 = sx + this.max_radius;
                [x0, x1] = this.renderer.xscale.r_invert(sx0, sx1);
            }
            else {
                const ms = this.max_size / 2;
                sx0 = sx - ms;
                sx1 = sx + ms;
                [x0, x1] = this.renderer.xscale.r_invert(sx0, sx1);
            }
        }
        else {
            // use circle bounds instead of current pointer x coordinates
            let sy0, sy1;
            x0 = bounds.x0;
            x1 = bounds.x1;
            if (this.use_radius && this.model.properties.radius.units == "data") {
                sy0 = sy - this.max_radius;
                sy1 = sy + this.max_radius;
                [y0, y1] = this.renderer.yscale.r_invert(sy0, sy1);
            }
            else {
                const ms = this.max_size / 2;
                sy0 = sy - ms;
                sy1 = sy + ms;
                [y0, y1] = this.renderer.yscale.r_invert(sy0, sy1);
            }
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
    // circle does not inherit from marker (since it also accepts radius) so we
    // must supply a draw_legend for it  here
    draw_legend_for_index(ctx, { x0, y0, x1, y1 }, index) {
        // using objects like this seems a little wonky, since the keys are coerced to
        // stings, but it works
        const len = index + 1;
        const sx = new Array(len);
        sx[index] = (x0 + x1) / 2;
        const sy = new Array(len);
        sy[index] = (y0 + y1) / 2;
        const sradius = new Array(len);
        sradius[index] = Math.min(Math.abs(x1 - x0), Math.abs(y1 - y0)) * 0.2;
        this._render(ctx, [index], { sx, sy, sradius }); // XXX
    }
}
CircleView.__name__ = "CircleView";
export class Circle extends XYGlyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Circle;
Circle.__name__ = "Circle";
(() => {
    _a.prototype.default_view = CircleView;
    _a.mixins([LineVector, FillVector, HatchVector]);
    _a.define(({ Number }) => ({
        angle: [p.AngleSpec, 0],
        size: [p.ScreenSizeSpec, { value: 4 }],
        radius: [p.NullDistanceSpec, null],
        radius_dimension: [RadiusDimension, "x"],
        hit_dilation: [Number, 1.0],
    }));
})();
//# sourceMappingURL=circle.js.map