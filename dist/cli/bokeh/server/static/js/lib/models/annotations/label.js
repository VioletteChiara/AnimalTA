var _a;
import { TextAnnotation, TextAnnotationView } from "./text_annotation";
import { resolve_angle } from "../../core/util/math";
import { SpatialUnits, AngleUnits } from "../../core/enums";
import { TextBox } from "../../core/graphics";
import { SideLayout } from "../../core/layout/side_panel";
import * as mixins from "../../core/property_mixins";
export class LabelView extends TextAnnotationView {
    update_layout() {
        const { panel } = this;
        if (panel != null)
            this.layout = new SideLayout(panel, () => this.get_size(), false);
        else
            this.layout = undefined;
    }
    _get_size() {
        const { text } = this.model;
        const graphics = new TextBox({ text });
        const { angle, angle_units } = this.model;
        graphics.angle = resolve_angle(angle, angle_units);
        graphics.visuals = this.visuals.text.values();
        const { width, height } = graphics.size();
        return { width, height };
    }
    _render() {
        const { angle, angle_units } = this.model;
        const rotation = resolve_angle(angle, angle_units);
        const panel = this.layout != null ? this.layout : this.plot_view.frame;
        const xscale = this.coordinates.x_scale;
        const yscale = this.coordinates.y_scale;
        let sx = this.model.x_units == "data" ? xscale.compute(this.model.x) : panel.bbox.xview.compute(this.model.x);
        let sy = this.model.y_units == "data" ? yscale.compute(this.model.y) : panel.bbox.yview.compute(this.model.y);
        sx += this.model.x_offset;
        sy -= this.model.y_offset;
        const draw = this.model.render_mode == "canvas" ? this._canvas_text.bind(this) : this._css_text.bind(this);
        draw(this.layer.ctx, this.model.text, sx, sy, rotation);
    }
}
LabelView.__name__ = "LabelView";
export class Label extends TextAnnotation {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Label;
Label.__name__ = "Label";
(() => {
    _a.prototype.default_view = LabelView;
    _a.mixins([
        mixins.Text,
        ["border_", mixins.Line],
        ["background_", mixins.Fill],
    ]);
    _a.define(({ Number, String, Angle }) => ({
        x: [Number],
        x_units: [SpatialUnits, "data"],
        y: [Number],
        y_units: [SpatialUnits, "data"],
        text: [String, ""],
        angle: [Angle, 0],
        angle_units: [AngleUnits, "rad"],
        x_offset: [Number, 0],
        y_offset: [Number, 0],
    }));
    _a.override({
        background_fill_color: null,
        border_line_color: null,
    });
})();
//# sourceMappingURL=label.js.map