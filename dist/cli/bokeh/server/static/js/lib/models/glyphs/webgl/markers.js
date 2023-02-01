import { BaseGLGlyph } from "./base";
import { Float32Buffer, NormalizedUint8Buffer, Uint8Buffer } from "./buffer";
// Avoiding use of nan or inf to represent missing data in webgl as shaders may
// have reduced floating point precision.  So here using a large-ish negative
// value instead.
const missing_point = -10000;
// XXX: this is needed to cut circular dependency between this and models/glyphs/circle
function is_CircleView(glyph_view) {
    return glyph_view.model.type == "Circle";
}
// Base class for markers. All markers share the same GLSL, except for one
// function in the fragment shader that defines the marker geometry and is
// enabled through a #define.
export class MarkerGL extends BaseGLGlyph {
    constructor(regl_wrapper, glyph, marker_type) {
        super(regl_wrapper, glyph);
        this.glyph = glyph;
        this.marker_type = marker_type;
        this._marker_type = marker_type;
        this._antialias = 0.8;
        this._show_all = false;
    }
    static is_supported(marker_type) {
        switch (marker_type) {
            case "asterisk":
            case "circle":
            case "circle_cross":
            case "circle_dot":
            case "circle_x":
            case "circle_y":
            case "cross":
            case "dash":
            case "diamond":
            case "diamond_cross":
            case "diamond_dot":
            case "dot":
            case "hex":
            case "hex_dot":
            case "inverted_triangle":
            case "plus":
            case "square":
            case "square_cross":
            case "square_dot":
            case "square_pin":
            case "square_x":
            case "star":
            case "star_dot":
            case "triangle":
            case "triangle_dot":
            case "triangle_pin":
            case "x":
            case "y":
                return true;
            default:
                return false;
        }
    }
    draw(indices, main_glyph, transform) {
        // The main glyph has the data, this glyph has the visuals.
        const mainGlGlyph = main_glyph.glglyph;
        // Temporary solution for circles to always force call to _set_data.
        // Correct solution depends on keeping the webgl properties constant and
        // only changing the indices, which in turn depends on the correct webgl
        // instanced rendering.
        if (mainGlGlyph.data_changed || is_CircleView(this.glyph)) {
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
        const props = {
            scissor: this.regl_wrapper.scissor,
            viewport: this.regl_wrapper.viewport,
            canvas_size: [transform.width, transform.height],
            pixel_ratio: transform.pixel_ratio,
            center: mainGlGlyph._centers,
            size: mainGlGlyph._sizes,
            angle: mainGlGlyph._angles,
            nmarkers,
            antialias: this._antialias,
            linewidth: this._linewidths,
            line_color: this._line_rgba,
            fill_color: this._fill_rgba,
            show: this._show,
        };
        this.regl_wrapper.marker(this._marker_type)(props);
    }
    _set_data() {
        const nmarkers = this.glyph.sx.length;
        if (this._centers == null) {
            // Either all or none are set.
            this._centers = new Float32Buffer(this.regl_wrapper);
            this._sizes = new Float32Buffer(this.regl_wrapper);
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
        if (is_CircleView(this.glyph) && this.glyph.radius != null) {
            const sizes_array = this._sizes.get_sized_array(nmarkers);
            for (let i = 0; i < nmarkers; i++)
                sizes_array[i] = this.glyph.sradius[i] * 2;
            this._sizes.update();
        }
        else {
            this._sizes.set_from_prop(this.glyph.size);
        }
        this._angles.set_from_prop(this.glyph.angle);
    }
    _set_visuals() {
        const fill = this.glyph.visuals.fill;
        const line = this.glyph.visuals.line;
        if (this._linewidths == null) {
            // Either all or none are set.
            this._linewidths = new Float32Buffer(this.regl_wrapper);
            this._line_rgba = new NormalizedUint8Buffer(this.regl_wrapper);
            this._fill_rgba = new NormalizedUint8Buffer(this.regl_wrapper);
        }
        this._linewidths.set_from_prop(line.line_width);
        this._line_rgba.set_from_color(line.line_color, line.line_alpha);
        this._fill_rgba.set_from_color(fill.fill_color, fill.fill_alpha);
    }
}
MarkerGL.__name__ = "MarkerGL";
//# sourceMappingURL=markers.js.map