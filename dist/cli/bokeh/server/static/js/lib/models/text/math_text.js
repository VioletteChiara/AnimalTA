var _a, _b, _c;
import { isNumber } from "../../core/util/types";
import { load_image } from "../../core/util/image";
import { color2css } from "../../core/util/color";
import { text_width } from "../../core/graphics";
import { font_metrics, parse_css_font_size } from "../../core/util/text";
import { AffineTransform } from "../../core/util/affine";
import { BBox } from "../../core/util/bbox";
import { BaseText, BaseTextView } from "./base_text";
import { default_provider } from "./providers";
/**
 * Helper class for rendering MathText into Canvas
 */
export class MathTextView extends BaseTextView {
    constructor() {
        super(...arguments);
        this._position = { sx: 0, sy: 0 };
        // Align does nothing, needed to maintain compatibility with TextBox,
        // to align you need to use TeX Macros.
        // http://docs.mathjax.org/en/latest/input/tex/macros/index.html?highlight=align
        this.align = "left";
        this._x_anchor = "left";
        this._y_anchor = "center";
        this._base_font_size = 13; // the same as .bk-root's font-size (13px)
        this.font_size_scale = 1.0;
        this.svg_image = null;
    }
    graphics() {
        return this;
    }
    // Same for infer_text_height
    infer_text_height() {
        return "ascent_descent";
    }
    set base_font_size(v) {
        if (v != null)
            this._base_font_size = v;
    }
    get base_font_size() {
        return this._base_font_size;
    }
    get has_image_loaded() {
        return this.svg_image != null;
    }
    _rect() {
        const { width, height } = this._size();
        const { x, y } = this._computed_position();
        const bbox = new BBox({ x, y, width, height });
        return bbox.rect;
    }
    set position(p) {
        this._position = p;
    }
    get position() {
        return this._position;
    }
    get text() {
        return this.model.text;
    }
    get provider() {
        return default_provider;
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        if (this.provider.status == "not_started")
            await this.provider.fetch();
        if (this.provider.status == "not_started" || this.provider.status == "loading")
            this.provider.ready.connect(() => this.load_image());
        if (this.provider.status == "loaded")
            await this.load_image();
    }
    connect_signals() {
        super.connect_signals();
        this.on_change(this.model.properties.text, () => this.load_image());
    }
    set visuals(v) {
        const color = v.color;
        const alpha = v.alpha;
        const style = v.font_style;
        let size = v.font_size;
        const face = v.font;
        const { font_size_scale, _base_font_size } = this;
        const res = parse_css_font_size(size);
        if (res != null) {
            let { value, unit } = res;
            value *= font_size_scale;
            if (unit == "em" && _base_font_size) {
                value *= _base_font_size;
                unit = "px";
            }
            size = `${value}${unit}`;
        }
        const font = `${style} ${size} ${face}`;
        this.font = font;
        this.color = color2css(color, alpha);
    }
    /**
     * Calculates position of element after considering
     * anchor and dimensions
     */
    _computed_position() {
        const { width, height } = this._size();
        const { sx, sy, x_anchor = this._x_anchor, y_anchor = this._y_anchor } = this.position;
        const x = sx - (() => {
            if (isNumber(x_anchor))
                return x_anchor * width;
            else {
                switch (x_anchor) {
                    case "left": return 0;
                    case "center": return 0.5 * width;
                    case "right": return width;
                }
            }
        })();
        const y = sy - (() => {
            if (isNumber(y_anchor))
                return y_anchor * height;
            else {
                switch (y_anchor) {
                    case "top": return 0;
                    case "center": return 0.5 * height;
                    case "bottom": return height;
                    case "baseline": return 0.5 * height;
                }
            }
        })();
        return { x, y };
    }
    /**
     * Uses the width, height and given angle to calculate the size
    */
    size() {
        const { width, height } = this._size();
        const { angle } = this;
        if (!angle)
            return { width, height };
        else {
            const c = Math.cos(Math.abs(angle));
            const s = Math.sin(Math.abs(angle));
            return {
                width: Math.abs(width * c + height * s),
                height: Math.abs(width * s + height * c),
            };
        }
    }
    get_text_dimensions() {
        return {
            width: text_width(this.model.text, this.font),
            height: font_metrics(this.font).height,
        };
    }
    get_image_dimensions() {
        const heightEx = parseFloat(this.svg_element
            .getAttribute("height")
            ?.replace(/([A-z])/g, "") ?? "0");
        const widthEx = parseFloat(this.svg_element
            .getAttribute("width")
            ?.replace(/([A-z])/g, "") ?? "0");
        return {
            width: font_metrics(this.font).x_height * widthEx,
            height: font_metrics(this.font).x_height * heightEx,
        };
    }
    _size() {
        return this.has_image_loaded ? this.get_image_dimensions() : this.get_text_dimensions();
    }
    bbox() {
        const { p0, p1, p2, p3 } = this.rect();
        const left = Math.min(p0.x, p1.x, p2.x, p3.x);
        const top = Math.min(p0.y, p1.y, p2.y, p3.y);
        const right = Math.max(p0.x, p1.x, p2.x, p3.x);
        const bottom = Math.max(p0.y, p1.y, p2.y, p3.y);
        return new BBox({ left, right, top, bottom });
    }
    rect() {
        const rect = this._rect();
        const { angle } = this;
        if (!angle)
            return rect;
        else {
            const { sx, sy } = this.position;
            const tr = new AffineTransform();
            tr.translate(sx, sy);
            tr.rotate(angle);
            tr.translate(-sx, -sy);
            return tr.apply_rect(rect);
        }
    }
    paint_rect(ctx) {
        const { p0, p1, p2, p3 } = this.rect();
        ctx.save();
        ctx.strokeStyle = "red";
        ctx.lineWidth = 1;
        ctx.beginPath();
        const { round } = Math;
        ctx.moveTo(round(p0.x), round(p0.y));
        ctx.lineTo(round(p1.x), round(p1.y));
        ctx.lineTo(round(p2.x), round(p2.y));
        ctx.lineTo(round(p3.x), round(p3.y));
        ctx.closePath();
        ctx.stroke();
        ctx.restore();
    }
    paint_bbox(ctx) {
        const { x, y, width, height } = this.bbox();
        ctx.save();
        ctx.strokeStyle = "blue";
        ctx.lineWidth = 1;
        ctx.beginPath();
        const { round } = Math;
        ctx.moveTo(round(x), round(y));
        ctx.lineTo(round(x), round(y + height));
        ctx.lineTo(round(x + width), round(y + height));
        ctx.lineTo(round(x + width), round(y));
        ctx.closePath();
        ctx.stroke();
        ctx.restore();
    }
    async load_image() {
        if (this.provider.MathJax == null)
            return null;
        const mathjax_element = this._process_text(this.model.text);
        if (mathjax_element == null) {
            this._has_finished = true;
            return null;
        }
        const svg_element = mathjax_element.children[0];
        this.svg_element = svg_element;
        svg_element.setAttribute("font", this.font);
        svg_element.setAttribute("stroke", this.color);
        const outer_HTML = svg_element.outerHTML;
        const blob = new Blob([outer_HTML], { type: "image/svg+xml" });
        const url = URL.createObjectURL(blob);
        try {
            this.svg_image = await load_image(url);
        }
        finally {
            URL.revokeObjectURL(url);
        }
        this.parent.request_layout();
        return this.svg_image;
    }
    /**
     * Takes a Canvas' Context2d and if the image has already
     * been loaded draws the image in it otherwise draws the model's text.
    */
    paint(ctx) {
        ctx.save();
        const { sx, sy } = this.position;
        if (this.angle) {
            ctx.translate(sx, sy);
            ctx.rotate(this.angle);
            ctx.translate(-sx, -sy);
        }
        const { x, y } = this._computed_position();
        if (this.svg_image != null) {
            const { width, height } = this.get_image_dimensions();
            ctx.drawImage(this.svg_image, x, y, width, height);
        }
        else {
            ctx.fillStyle = this.color;
            ctx.font = this.font;
            ctx.textAlign = "left";
            ctx.textBaseline = "alphabetic";
            ctx.fillText(this.model.text, x, y + font_metrics(this.font).ascent);
        }
        ctx.restore();
        if (!this._has_finished && (this.provider.status == "failed" || this.has_image_loaded)) {
            this._has_finished = true;
            this.parent.notify_finished_after_paint();
        }
    }
}
MathTextView.__name__ = "MathTextView";
export class MathText extends BaseText {
    constructor(attrs) {
        super(attrs);
    }
}
MathText.__name__ = "MathText";
export class AsciiView extends MathTextView {
    _process_text(_text) {
        return undefined; // TODO: this.provider.MathJax?.ascii2svg(text)
    }
}
AsciiView.__name__ = "AsciiView";
export class Ascii extends MathText {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Ascii;
Ascii.__name__ = "Ascii";
(() => {
    _a.prototype.default_view = AsciiView;
})();
export class MathMLView extends MathTextView {
    _process_text(text) {
        return this.provider.MathJax?.mathml2svg(text.trim());
    }
}
MathMLView.__name__ = "MathMLView";
export class MathML extends MathText {
    constructor(attrs) {
        super(attrs);
    }
}
_b = MathML;
MathML.__name__ = "MathML";
(() => {
    _b.prototype.default_view = MathMLView;
})();
export class TeXView extends MathTextView {
    _process_text(text) {
        // TODO: allow plot/document level configuration of macros
        return this.provider.MathJax?.tex2svg(text, undefined, this.model.macros);
    }
}
TeXView.__name__ = "TeXView";
export class TeX extends MathText {
    constructor(attrs) {
        super(attrs);
    }
}
_c = TeX;
TeX.__name__ = "TeX";
(() => {
    _c.prototype.default_view = TeXView;
    _c.define(({ Boolean, Number, String, Dict, Tuple, Or }) => ({
        macros: [Dict(Or(String, Tuple(String, Number))), {}],
        inline: [Boolean, false],
    }));
})();
//# sourceMappingURL=math_text.js.map