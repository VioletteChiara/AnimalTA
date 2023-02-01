import { VisualProperties, VisualUniforms } from "./visual";
import * as mixins from "../property_mixins";
import { color2css } from "../util/color";
export class Text extends VisualProperties {
    get doit() {
        const color = this.text_color.get_value();
        const alpha = this.text_alpha.get_value();
        return !(color == null || alpha == 0);
    }
    values() {
        return {
            color: this.text_color.get_value(),
            alpha: this.text_alpha.get_value(),
            font: this.text_font.get_value(),
            font_size: this.text_font_size.get_value(),
            font_style: this.text_font_style.get_value(),
            align: this.text_align.get_value(),
            baseline: this.text_baseline.get_value(),
            line_height: this.text_line_height.get_value(),
        };
    }
    set_value(ctx) {
        const color = this.text_color.get_value();
        const alpha = this.text_alpha.get_value();
        ctx.fillStyle = color2css(color, alpha);
        ctx.font = this.font_value();
        ctx.textAlign = this.text_align.get_value();
        ctx.textBaseline = this.text_baseline.get_value();
    }
    font_value() {
        const style = this.text_font_style.get_value();
        const size = this.text_font_size.get_value();
        const face = this.text_font.get_value();
        return `${style} ${size} ${face}`;
    }
}
Text.__name__ = "Text";
export class TextScalar extends VisualUniforms {
    get doit() {
        const color = this.text_color.value;
        const alpha = this.text_alpha.value;
        return !(color == 0 || alpha == 0);
    }
    values() {
        return {
            color: this.text_color.value,
            alpha: this.text_alpha.value,
            font: this.text_font.value,
            font_size: this.text_font_size.value,
            font_style: this.text_font_style.value,
            align: this.text_align.value,
            baseline: this.text_baseline.value,
            line_height: this.text_line_height.value,
        };
    }
    set_value(ctx) {
        const color = this.text_color.value;
        const alpha = this.text_alpha.value;
        const font = this.font_value();
        const align = this.text_align.value;
        const baseline = this.text_baseline.value;
        ctx.fillStyle = color2css(color, alpha);
        ctx.font = font;
        ctx.textAlign = align;
        ctx.textBaseline = baseline;
    }
    font_value() {
        const style = this.text_font_style.value;
        const size = this.text_font_size.value;
        const face = this.text_font.value;
        return `${style} ${size} ${face}`;
    }
}
TextScalar.__name__ = "TextScalar";
export class TextVector extends VisualUniforms {
    values(i) {
        return {
            color: this.text_color.get(i),
            alpha: this.text_alpha.get(i),
            font: this.text_font.get(i),
            font_size: this.text_font_size.get(i),
            font_style: this.text_font_style.get(i),
            align: this.text_align.get(i),
            baseline: this.text_baseline.get(i),
            line_height: this.text_line_height.get(i),
        };
    }
    get doit() {
        const { text_color } = this;
        if (text_color.is_Scalar() && text_color.value == 0)
            return false;
        const { text_alpha } = this;
        if (text_alpha.is_Scalar() && text_alpha.value == 0)
            return false;
        return true;
    }
    set_vectorize(ctx, i) {
        const color = this.text_color.get(i);
        const alpha = this.text_alpha.get(i);
        const font = this.font_value(i);
        const align = this.text_align.get(i);
        const baseline = this.text_baseline.get(i);
        ctx.fillStyle = color2css(color, alpha);
        ctx.font = font;
        ctx.textAlign = align;
        ctx.textBaseline = baseline;
    }
    font_value(i) {
        const style = this.text_font_style.get(i);
        const size = this.text_font_size.get(i);
        const face = this.text_font.get(i);
        return `${style} ${size} ${face}`;
    }
}
TextVector.__name__ = "TextVector";
Text.prototype.type = "text";
Text.prototype.attrs = Object.keys(mixins.Text);
TextScalar.prototype.type = "text";
TextScalar.prototype.attrs = Object.keys(mixins.TextScalar);
TextVector.prototype.type = "text";
TextVector.prototype.attrs = Object.keys(mixins.TextVector);
//# sourceMappingURL=text.js.map