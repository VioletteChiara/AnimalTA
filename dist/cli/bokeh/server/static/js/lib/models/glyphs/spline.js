var _a;
import { XYGlyph, XYGlyphView } from "./xy_glyph";
import * as mixins from "../../core/property_mixins";
import { catmullrom_spline } from "../../core/util/interpolation";
export class SplineView extends XYGlyphView {
    _set_data() {
        const { tension, closed } = this.model;
        [this._xt, this._yt] = catmullrom_spline(this._x, this._y, 20, tension, closed);
    }
    _map_data() {
        const { x_scale, y_scale } = this.renderer.coordinates;
        this.sxt = x_scale.v_compute(this._xt);
        this.syt = y_scale.v_compute(this._yt);
    }
    _render(ctx, _indices, data) {
        const { sxt: sx, syt: sy } = data ?? this;
        let move = true;
        ctx.beginPath();
        const n = sx.length;
        for (let j = 0; j < n; j++) {
            const sx_i = sx[j];
            const sy_i = sy[j];
            if (!isFinite(sx_i + sy_i))
                move = true;
            else {
                if (move) {
                    ctx.moveTo(sx_i, sy_i);
                    move = false;
                }
                else
                    ctx.lineTo(sx_i, sy_i);
            }
        }
        this.visuals.line.set_value(ctx);
        ctx.stroke();
    }
}
SplineView.__name__ = "SplineView";
export class Spline extends XYGlyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Spline;
Spline.__name__ = "Spline";
(() => {
    _a.prototype.default_view = SplineView;
    _a.mixins(mixins.LineScalar);
    _a.define(({ Boolean, Number }) => ({
        tension: [Number, 0.5],
        closed: [Boolean, false],
    }));
})();
//# sourceMappingURL=spline.js.map