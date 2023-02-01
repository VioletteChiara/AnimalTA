var _a;
import { TextAnnotation, TextAnnotationView } from "./text_annotation";
import { VerticalAlign, TextAlign } from "../../core/enums";
import { TextBox } from "../../core/graphics";
import * as mixins from "../../core/property_mixins";
export class TitleView extends TextAnnotationView {
    _get_location() {
        const hmargin = this.model.offset;
        const vmargin = this.model.standoff / 2;
        let sx, sy;
        const { bbox } = this.layout;
        switch (this.panel.side) {
            case "above":
            case "below": {
                switch (this.model.vertical_align) {
                    case "top":
                        sy = bbox.top + vmargin;
                        break;
                    case "middle":
                        sy = bbox.vcenter;
                        break;
                    case "bottom":
                        sy = bbox.bottom - vmargin;
                        break;
                }
                switch (this.model.align) {
                    case "left":
                        sx = bbox.left + hmargin;
                        break;
                    case "center":
                        sx = bbox.hcenter;
                        break;
                    case "right":
                        sx = bbox.right - hmargin;
                        break;
                }
                break;
            }
            case "left": {
                switch (this.model.vertical_align) {
                    case "top":
                        sx = bbox.left + vmargin;
                        break;
                    case "middle":
                        sx = bbox.hcenter;
                        break;
                    case "bottom":
                        sx = bbox.right - vmargin;
                        break;
                }
                switch (this.model.align) {
                    case "left":
                        sy = bbox.bottom - hmargin;
                        break;
                    case "center":
                        sy = bbox.vcenter;
                        break;
                    case "right":
                        sy = bbox.top + hmargin;
                        break;
                }
                break;
            }
            case "right": {
                switch (this.model.vertical_align) {
                    case "top":
                        sx = bbox.right - vmargin;
                        break;
                    case "middle":
                        sx = bbox.hcenter;
                        break;
                    case "bottom":
                        sx = bbox.left + vmargin;
                        break;
                }
                switch (this.model.align) {
                    case "left":
                        sy = bbox.top + hmargin;
                        break;
                    case "center":
                        sy = bbox.vcenter;
                        break;
                    case "right":
                        sy = bbox.bottom - hmargin;
                        break;
                }
                break;
            }
        }
        return [sx, sy];
    }
    _render() {
        const { text } = this.model;
        if (text == null || text.length == 0)
            return;
        this.model.text_baseline = this.model.vertical_align;
        this.model.text_align = this.model.align;
        const [sx, sy] = this._get_location();
        const angle = this.panel.get_label_angle_heuristic("parallel");
        const draw = this.model.render_mode == "canvas" ? this._canvas_text.bind(this) : this._css_text.bind(this);
        draw(this.layer.ctx, text, sx, sy, angle);
    }
    _get_size() {
        const { text } = this.model;
        const graphics = new TextBox({ text });
        graphics.visuals = this.visuals.text.values();
        const { width, height } = graphics.size();
        // XXX: The magic 2px is for backwards compatibility. This will be removed at
        // some point, but currently there is no point breaking half of visual tests.
        return { width, height: height == 0 ? 0 : 2 + height + this.model.standoff };
    }
}
TitleView.__name__ = "TitleView";
export class Title extends TextAnnotation {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Title;
Title.__name__ = "Title";
(() => {
    _a.prototype.default_view = TitleView;
    _a.mixins([
        mixins.Text,
        ["border_", mixins.Line],
        ["background_", mixins.Fill],
    ]);
    _a.define(({ Number, String }) => ({
        text: [String, ""],
        vertical_align: [VerticalAlign, "bottom"],
        align: [TextAlign, "left"],
        offset: [Number, 0],
        standoff: [Number, 10],
    }));
    _a.prototype._props.text_align.options.internal = true;
    _a.prototype._props.text_baseline.options.internal = true;
    _a.override({
        text_font_size: "13px",
        text_font_style: "bold",
        text_line_height: 1.0,
        background_fill_color: null,
        border_line_color: null,
    });
})();
//# sourceMappingURL=title.js.map