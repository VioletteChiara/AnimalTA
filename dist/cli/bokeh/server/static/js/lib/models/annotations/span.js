var _a;
import { Annotation, AnnotationView } from "./annotation";
import * as mixins from "../../core/property_mixins";
import { SpatialUnits, RenderMode, Dimension } from "../../core/enums";
export class SpanView extends AnnotationView {
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.change, () => this.plot_view.request_paint(this));
    }
    _render() {
        const { location } = this.model;
        if (location == null) {
            return;
        }
        const { frame } = this.plot_view;
        const xscale = this.coordinates.x_scale;
        const yscale = this.coordinates.y_scale;
        const _calc_dim = (scale, view) => {
            if (this.model.location_units == "data")
                return scale.compute(location);
            else
                return this.model.for_hover ? location : view.compute(location);
        };
        let height, sleft, stop, width;
        if (this.model.dimension == "width") {
            stop = _calc_dim(yscale, frame.bbox.yview);
            sleft = frame.bbox.left;
            width = frame.bbox.width;
            height = this.model.line_width;
        }
        else {
            stop = frame.bbox.top;
            sleft = _calc_dim(xscale, frame.bbox.xview);
            width = this.model.line_width;
            height = frame.bbox.height;
        }
        const { ctx } = this.layer;
        ctx.save();
        ctx.beginPath();
        this.visuals.line.set_value(ctx);
        ctx.moveTo(sleft, stop);
        if (this.model.dimension == "width") {
            ctx.lineTo(sleft + width, stop);
        }
        else {
            ctx.lineTo(sleft, stop + height);
        }
        ctx.stroke();
        ctx.restore();
    }
}
SpanView.__name__ = "SpanView";
export class Span extends Annotation {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Span;
Span.__name__ = "Span";
(() => {
    _a.prototype.default_view = SpanView;
    _a.mixins(mixins.Line);
    _a.define(({ Number, Nullable }) => ({
        render_mode: [RenderMode, "canvas"],
        location: [Nullable(Number), null],
        location_units: [SpatialUnits, "data"],
        dimension: [Dimension, "width"],
    }));
    _a.internal(({ Boolean }) => ({
        for_hover: [Boolean, false],
    }));
    _a.override({
        line_color: "black",
    });
})();
//# sourceMappingURL=span.js.map