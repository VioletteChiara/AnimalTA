var _a;
import { XYGlyph, XYGlyphView } from "./xy_glyph";
import { generic_line_vector_legend } from "./utils";
import { LineVector } from "../../core/property_mixins";
import { to_screen } from "../../core/types";
import { Direction } from "../../core/enums";
import * as p from "../../core/properties";
export class ArcView extends XYGlyphView {
    _map_data() {
        if (this.model.properties.radius.units == "data")
            this.sradius = this.sdist(this.renderer.xscale, this._x, this.radius);
        else
            this.sradius = to_screen(this.radius);
    }
    _render(ctx, indices, data) {
        if (this.visuals.line.doit) {
            const { sx, sy, sradius, start_angle, end_angle } = data ?? this;
            const anticlock = this.model.direction == "anticlock";
            for (const i of indices) {
                const sx_i = sx[i];
                const sy_i = sy[i];
                const sradius_i = sradius[i];
                const start_angle_i = start_angle.get(i);
                const end_angle_i = end_angle.get(i);
                if (!isFinite(sx_i + sy_i + sradius_i + start_angle_i + end_angle_i))
                    continue;
                ctx.beginPath();
                ctx.arc(sx_i, sy_i, sradius_i, start_angle_i, end_angle_i, anticlock);
                this.visuals.line.set_vectorize(ctx, i);
                ctx.stroke();
            }
        }
    }
    draw_legend_for_index(ctx, bbox, index) {
        generic_line_vector_legend(this.visuals, ctx, bbox, index);
    }
}
ArcView.__name__ = "ArcView";
export class Arc extends XYGlyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Arc;
Arc.__name__ = "Arc";
(() => {
    _a.prototype.default_view = ArcView;
    _a.mixins(LineVector);
    _a.define(({}) => ({
        direction: [Direction, "anticlock"],
        radius: [p.DistanceSpec, { field: "radius" }],
        start_angle: [p.AngleSpec, { field: "start_angle" }],
        end_angle: [p.AngleSpec, { field: "end_angle" }],
    }));
})();
//# sourceMappingURL=arc.js.map