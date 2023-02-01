var _a;
import { XYGlyph, XYGlyphView } from "./xy_glyph";
import { generic_line_vector_legend } from "./utils";
import { LineVector } from "../../core/property_mixins";
import { to_screen } from "../../core/types";
import * as p from "../../core/properties";
export class RayView extends XYGlyphView {
    _map_data() {
        if (this.model.properties.length.units == "data")
            this.slength = this.sdist(this.renderer.xscale, this._x, this.length);
        else
            this.slength = to_screen(this.length);
        const { width, height } = this.renderer.plot_view.frame.bbox;
        const inf_len = 2 * (width + height);
        const { slength } = this;
        for (let i = 0, end = slength.length; i < end; i++) {
            if (slength[i] == 0)
                slength[i] = inf_len;
        }
    }
    _render(ctx, indices, data) {
        const { sx, sy, slength, angle } = data ?? this;
        if (this.visuals.line.doit) {
            for (const i of indices) {
                const sx_i = sx[i];
                const sy_i = sy[i];
                const angle_i = angle.get(i);
                const slength_i = slength[i];
                if (!isFinite(sx_i + sy_i + angle_i + slength_i))
                    continue;
                ctx.translate(sx_i, sy_i);
                ctx.rotate(angle_i);
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(slength_i, 0);
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
                ctx.rotate(-angle_i);
                ctx.translate(-sx_i, -sy_i);
            }
        }
    }
    draw_legend_for_index(ctx, bbox, index) {
        generic_line_vector_legend(this.visuals, ctx, bbox, index);
    }
}
RayView.__name__ = "RayView";
export class Ray extends XYGlyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Ray;
Ray.__name__ = "Ray";
(() => {
    _a.prototype.default_view = RayView;
    _a.mixins(LineVector);
    _a.define(({}) => ({
        length: [p.DistanceSpec, 0],
        angle: [p.AngleSpec, 0],
    }));
})();
//# sourceMappingURL=ray.js.map