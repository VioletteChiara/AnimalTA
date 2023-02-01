var _a;
import { Annotation, AnnotationView } from "./annotation";
import * as mixins from "../../core/property_mixins";
import { SpatialUnits } from "../../core/enums";
export class PolyAnnotationView extends AnnotationView {
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.change, () => this.request_render());
    }
    _render() {
        const { xs, ys } = this.model;
        if (xs.length != ys.length)
            return;
        const n = xs.length;
        if (n < 3)
            return;
        const { frame } = this.plot_view;
        const { ctx } = this.layer;
        const xscale = this.coordinates.x_scale;
        const yscale = this.coordinates.y_scale;
        const { screen } = this.model;
        function _calc_dim(values, units, scale, view) {
            if (screen)
                return values;
            else
                return units == "data" ? scale.v_compute(values) : view.v_compute(values);
        }
        const sxs = _calc_dim(xs, this.model.xs_units, xscale, frame.bbox.xview);
        const sys = _calc_dim(ys, this.model.ys_units, yscale, frame.bbox.yview);
        ctx.beginPath();
        for (let i = 0; i < n; i++) {
            ctx.lineTo(sxs[i], sys[i]);
        }
        ctx.closePath();
        this.visuals.fill.apply(ctx);
        this.visuals.hatch.apply(ctx);
        this.visuals.line.apply(ctx);
    }
}
PolyAnnotationView.__name__ = "PolyAnnotationView";
export class PolyAnnotation extends Annotation {
    constructor(attrs) {
        super(attrs);
    }
    update({ xs, ys }) {
        this.setv({ xs, ys, screen: true }, { check_eq: false }); // XXX: because of inplace updates in tools
    }
}
_a = PolyAnnotation;
PolyAnnotation.__name__ = "PolyAnnotation";
(() => {
    _a.prototype.default_view = PolyAnnotationView;
    _a.mixins([mixins.Line, mixins.Fill, mixins.Hatch]);
    _a.define(({ Number, Array }) => ({
        xs: [Array(Number), []],
        xs_units: [SpatialUnits, "data"],
        ys: [Array(Number), []],
        ys_units: [SpatialUnits, "data"],
    }));
    _a.internal(({ Boolean }) => ({
        screen: [Boolean, false],
    }));
    _a.override({
        fill_color: "#fff9ba",
        fill_alpha: 0.4,
        line_color: "#cccccc",
        line_alpha: 0.3,
    });
})();
//# sourceMappingURL=poly_annotation.js.map