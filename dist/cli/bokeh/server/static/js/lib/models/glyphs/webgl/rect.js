import { BaseGLGlyph } from "./base";
import { Float32Buffer, NormalizedUint8Buffer, Uint8Buffer } from "./buffer";
// Avoiding use of nan or inf to represent missing data in webgl as shaders may
// have reduced floating point precision.  So here using a large-ish negative
// value instead.
const missing_point = -10000;
export class RectGL extends BaseGLGlyph {
    constructor(regl_wrapper, glyph) {
        super(regl_wrapper, glyph);
        this.glyph = glyph;
        this._antialias = 1.5;
    }
    draw(indices, main_glyph, transform) {
        // The main glyph has the data, this glyph has the visuals.
        const mainGlGlyph = main_glyph.glglyph;
        if (mainGlGlyph.data_changed) {
            mainGlGlyph._set_data();
            mainGlGlyph.data_changed = false;
        }
        if (this.visuals_changed) {
            this._set_visuals();
            this.visuals_changed = false;
        }
        const nmarkers = mainGlGlyph._centers.length / 2;
        if (this._show == null)
            this._show = new Uint8Buffer(this.regl_wrapper);
        const prev_nmarkers = this._show.length;
        const show_array = this._show.get_sized_array(nmarkers);
        if (indices.length < nmarkers) {
            this._show_all = false;
            // Reset all show values to zero.
            for (let i = 0; i < nmarkers; i++)
                show_array[i] = 0;
            // Set show values of markers to render to 255.
            for (let j = 0; j < indices.length; j++) {
                show_array[indices[j]] = 255;
            }
        }
        else if (!this._show_all || prev_nmarkers != nmarkers) {
            this._show_all = true;
            for (let i = 0; i < nmarkers; i++)
                show_array[i] = 255;
        }
        this._show.update();
        if (this._have_hatch) {
            const props = {
                scissor: this.regl_wrapper.scissor,
                viewport: this.regl_wrapper.viewport,
                canvas_size: [transform.width, transform.height],
                pixel_ratio: transform.pixel_ratio,
                center: mainGlGlyph._centers,
                width: mainGlGlyph._widths,
                height: mainGlGlyph._heights,
                angle: mainGlGlyph._angles,
                nmarkers,
                antialias: this._antialias,
                linewidth: this._linewidths,
                line_color: this._line_rgba,
                fill_color: this._fill_rgba,
                line_join: this._line_joins,
                show: this._show,
                hatch_pattern: this._hatch_patterns,
                hatch_scale: this._hatch_scales,
                hatch_weight: this._hatch_weights,
                hatch_color: this._hatch_rgba,
            };
            this.regl_wrapper.rect_hatch()(props);
        }
        else {
            const props = {
                scissor: this.regl_wrapper.scissor,
                viewport: this.regl_wrapper.viewport,
                canvas_size: [transform.width, transform.height],
                pixel_ratio: transform.pixel_ratio,
                center: mainGlGlyph._centers,
                width: mainGlGlyph._widths,
                height: mainGlGlyph._heights,
                angle: mainGlGlyph._angles,
                nmarkers,
                antialias: this._antialias,
                linewidth: this._linewidths,
                line_color: this._line_rgba,
                fill_color: this._fill_rgba,
                line_join: this._line_joins,
                show: this._show,
            };
            this.regl_wrapper.rect_no_hatch()(props);
        }
    }
    _set_data() {
        const nmarkers = this.glyph.sx.length;
        if (this._centers == null) {
            // Either all or none are set.
            this._centers = new Float32Buffer(this.regl_wrapper);
            this._widths = new Float32Buffer(this.regl_wrapper);
            this._heights = new Float32Buffer(this.regl_wrapper);
            this._angles = new Float32Buffer(this.regl_wrapper);
        }
        const centers_array = this._centers.get_sized_array(nmarkers * 2);
        for (let i = 0; i < nmarkers; i++) {
            if (isFinite(this.glyph.sx[i]) && isFinite(this.glyph.sy[i])) {
                centers_array[2 * i] = this.glyph.sx[i];
                centers_array[2 * i + 1] = this.glyph.sy[i];
            }
            else {
                centers_array[2 * i] = missing_point;
                centers_array[2 * i + 1] = missing_point;
            }
        }
        this._centers.update();
        this._widths.set_from_array(this.glyph.sw);
        this._heights.set_from_array(this.glyph.sh);
        this._angles.set_from_prop(this.glyph.angle);
    }
    _set_visuals() {
        const fill = this.glyph.visuals.fill;
        const line = this.glyph.visuals.line;
        if (this._linewidths == null) {
            // Either all or none are set.
            this._linewidths = new Float32Buffer(this.regl_wrapper);
            this._line_joins = new Uint8Buffer(this.regl_wrapper);
            this._line_rgba = new NormalizedUint8Buffer(this.regl_wrapper);
            this._fill_rgba = new NormalizedUint8Buffer(this.regl_wrapper);
        }
        this._linewidths.set_from_prop(line.line_width);
        this._line_joins.set_from_line_join(line.line_join);
        this._line_rgba.set_from_color(line.line_color, line.line_alpha);
        this._fill_rgba.set_from_color(fill.fill_color, fill.fill_alpha);
        this._have_hatch = this.glyph.visuals.hatch.doit;
        if (this._have_hatch) {
            const hatch = this.glyph.visuals.hatch;
            if (this._hatch_patterns == null) {
                // Either all or none are set.
                this._hatch_patterns = new Uint8Buffer(this.regl_wrapper);
                this._hatch_scales = new Float32Buffer(this.regl_wrapper);
                this._hatch_weights = new Float32Buffer(this.regl_wrapper);
                this._hatch_rgba = new NormalizedUint8Buffer(this.regl_wrapper);
            }
            this._hatch_patterns.set_from_hatch_pattern(hatch.hatch_pattern);
            this._hatch_scales.set_from_prop(hatch.hatch_scale);
            this._hatch_weights.set_from_prop(hatch.hatch_weight);
            this._hatch_rgba.set_from_color(hatch.hatch_color, hatch.hatch_alpha);
        }
    }
}
RectGL.__name__ = "RectGL";
//# sourceMappingURL=rect.js.map