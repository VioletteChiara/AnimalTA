var _a;
import { DataAnnotation, DataAnnotationView } from "./data_annotation";
import * as mixins from "../../core/property_mixins";
import { SpatialUnits, RenderMode } from "../../core/enums";
import { div, display, remove } from "../../core/dom";
import { TextBox } from "../../core/graphics";
import * as p from "../../core/properties";
import { assert } from "../../core/util/assert";
export class LabelSetView extends DataAnnotationView {
    set_data(source) {
        super.set_data(source);
        this.els?.forEach((el) => remove(el));
        if (this.model.render_mode == "css") {
            const els = this.els = [...this.text].map(() => div({ style: { display: "none" } }));
            for (const el of els) {
                this.plot_view.canvas_view.add_overlay(el);
            }
        }
        else
            delete this.els;
    }
    remove() {
        this.els?.forEach((el) => remove(el));
        super.remove();
    }
    _rerender() {
        if (this.model.render_mode == "css")
            this.render();
        else
            this.request_render();
    }
    map_data() {
        const { x_scale, y_scale } = this.coordinates;
        const panel = this.layout != null ? this.layout : this.plot_view.frame;
        this.sx = this.model.x_units == "data" ? x_scale.v_compute(this._x) : panel.bbox.xview.v_compute(this._x);
        this.sy = this.model.y_units == "data" ? y_scale.v_compute(this._y) : panel.bbox.yview.v_compute(this._y);
    }
    paint() {
        const draw = this.model.render_mode == "canvas" ? this._v_canvas_text.bind(this) : this._v_css_text.bind(this);
        const { ctx } = this.layer;
        for (let i = 0, end = this.text.length; i < end; i++) {
            const x_offset_i = this.x_offset.get(i);
            const y_offset_i = this.y_offset.get(i);
            const sx_i = this.sx[i] + x_offset_i;
            const sy_i = this.sy[i] - y_offset_i;
            const angle_i = this.angle.get(i);
            const text_i = this.text.get(i);
            draw(ctx, i, text_i, sx_i, sy_i, angle_i);
        }
    }
    _v_canvas_text(ctx, i, text, sx, sy, angle) {
        const graphics = new TextBox({ text });
        graphics.angle = angle;
        graphics.position = { sx, sy };
        graphics.visuals = this.visuals.text.values(i);
        const { background_fill, border_line } = this.visuals;
        if (background_fill.doit || border_line.doit) {
            const { p0, p1, p2, p3 } = graphics.rect();
            ctx.beginPath();
            ctx.moveTo(p0.x, p0.y);
            ctx.lineTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.lineTo(p3.x, p3.y);
            ctx.closePath();
            this.visuals.background_fill.apply(ctx, i);
            this.visuals.border_line.apply(ctx, i);
        }
        if (this.visuals.text.doit)
            graphics.paint(ctx);
    }
    _v_css_text(ctx, i, text, sx, sy, angle) {
        assert(this.els != null);
        const el = this.els[i];
        el.textContent = text;
        this.visuals.text.set_vectorize(ctx, i);
        el.style.position = "absolute";
        el.style.left = `${sx}px`;
        el.style.top = `${sy}px`;
        el.style.color = ctx.fillStyle;
        el.style.font = ctx.font;
        el.style.lineHeight = "normal"; // needed to prevent ipynb css override
        el.style.whiteSpace = "pre";
        const [x_anchor, x_t] = (() => {
            switch (this.visuals.text.text_align.get(i)) {
                case "left": return ["left", "0%"];
                case "center": return ["center", "-50%"];
                case "right": return ["right", "-100%"];
            }
        })();
        const [y_anchor, y_t] = (() => {
            switch (this.visuals.text.text_baseline.get(i)) {
                case "top": return ["top", "0%"];
                case "middle": return ["center", "-50%"];
                case "bottom": return ["bottom", "-100%"];
                default: return ["center", "-50%"]; // "baseline"
            }
        })();
        let transform = `translate(${x_t}, ${y_t})`;
        if (angle) {
            transform += `rotate(${angle}rad)`;
        }
        el.style.transformOrigin = `${x_anchor} ${y_anchor}`;
        el.style.transform = transform;
        if (this.layout == null) {
            // const {bbox} = this.plot_view.frame
            // const {left, right, top, bottom} = bbox
            // el.style.clipPath = ???
        }
        if (this.visuals.background_fill.doit) {
            this.visuals.background_fill.set_vectorize(ctx, i);
            el.style.backgroundColor = ctx.fillStyle;
        }
        if (this.visuals.border_line.doit) {
            this.visuals.border_line.set_vectorize(ctx, i);
            // attempt to support vector-style ("8 4 8") line dashing for css mode
            el.style.borderStyle = ctx.lineDash.length < 2 ? "solid" : "dashed";
            el.style.borderWidth = `${ctx.lineWidth}px`;
            el.style.borderColor = ctx.strokeStyle;
        }
        display(el);
    }
}
LabelSetView.__name__ = "LabelSetView";
export class LabelSet extends DataAnnotation {
    constructor(attrs) {
        super(attrs);
    }
}
_a = LabelSet;
LabelSet.__name__ = "LabelSet";
(() => {
    _a.prototype.default_view = LabelSetView;
    _a.mixins([
        mixins.TextVector,
        ["border_", mixins.LineVector],
        ["background_", mixins.FillVector],
    ]);
    _a.define(() => ({
        x: [p.XCoordinateSpec, { field: "x" }],
        y: [p.YCoordinateSpec, { field: "y" }],
        x_units: [SpatialUnits, "data"],
        y_units: [SpatialUnits, "data"],
        text: [p.StringSpec, { field: "text" }],
        angle: [p.AngleSpec, 0],
        x_offset: [p.NumberSpec, { value: 0 }],
        y_offset: [p.NumberSpec, { value: 0 }],
        /** @deprecated */
        render_mode: [RenderMode, "canvas"],
    }));
    _a.override({
        background_fill_color: null,
        border_line_color: null,
    });
})();
//# sourceMappingURL=label_set.js.map