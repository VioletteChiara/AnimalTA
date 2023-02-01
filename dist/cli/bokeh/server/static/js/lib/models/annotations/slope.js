var _a;
import { Annotation, AnnotationView } from "./annotation";
import * as mixins from "../../core/property_mixins";
export class SlopeView extends AnnotationView {
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.change, () => this.request_render());
    }
    _render() {
        const { gradient, y_intercept } = this.model;
        if (gradient == null || y_intercept == null)
            return;
        const { frame } = this.plot_view;
        const xscale = this.coordinates.x_scale;
        const yscale = this.coordinates.y_scale;
        let sy_start, sy_end, sx_start, sx_end;
        if (gradient == 0) {
            sy_start = yscale.compute(y_intercept);
            sy_end = sy_start;
            sx_start = frame.bbox.left;
            sx_end = sx_start + frame.bbox.width;
        }
        else {
            sy_start = frame.bbox.top;
            sy_end = sy_start + frame.bbox.height;
            const y_start = yscale.invert(sy_start);
            const y_end = yscale.invert(sy_end);
            const x_start = (y_start - y_intercept) / gradient;
            const x_end = (y_end - y_intercept) / gradient;
            sx_start = xscale.compute(x_start);
            sx_end = xscale.compute(x_end);
        }
        const { ctx } = this.layer;
        ctx.save();
        ctx.beginPath();
        this.visuals.line.set_value(ctx);
        ctx.moveTo(sx_start, sy_start);
        ctx.lineTo(sx_end, sy_end);
        ctx.stroke();
        ctx.restore();
    }
}
SlopeView.__name__ = "SlopeView";
export class Slope extends Annotation {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Slope;
Slope.__name__ = "Slope";
(() => {
    _a.prototype.default_view = SlopeView;
    _a.mixins(mixins.Line);
    _a.define(({ Number, Nullable }) => ({
        gradient: [Nullable(Number), null],
        y_intercept: [Nullable(Number), null],
    }));
    _a.override({
        line_color: "black",
    });
})();
//# sourceMappingURL=slope.js.map