var _a;
import { XYGlyph, XYGlyphView } from "./xy_glyph";
import { to_screen } from "../../core/types";
import * as p from "../../core/properties";
import { Selection } from "../selections/selection";
import { concat } from "../../core/util/array";
import { is_NDArray } from "../../core/util/ndarray";
import { assert } from "../../core/util/assert";
export class ImageBaseView extends XYGlyphView {
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.properties.global_alpha.change, () => this.renderer.request_render());
    }
    _render(ctx, indices, data) {
        const { image_data, sx, sy, sw, sh, global_alpha } = data ?? this;
        const old_smoothing = ctx.getImageSmoothingEnabled();
        ctx.setImageSmoothingEnabled(false);
        const scalar_alpha = global_alpha.is_Scalar();
        if (scalar_alpha)
            ctx.globalAlpha = global_alpha.value;
        for (const i of indices) {
            const image_data_i = image_data[i];
            const sx_i = sx[i];
            const sy_i = sy[i];
            const sw_i = sw[i];
            const sh_i = sh[i];
            const alpha_i = this.global_alpha.get(i);
            if (image_data_i == null || !isFinite(sx_i + sy_i + sw_i + sh_i + alpha_i))
                continue;
            if (!scalar_alpha)
                ctx.globalAlpha = alpha_i;
            const y_offset = sy_i;
            ctx.translate(0, y_offset);
            ctx.scale(1, -1);
            ctx.translate(0, -y_offset);
            ctx.drawImage(image_data_i, sx_i | 0, sy_i | 0, sw_i, sh_i);
            ctx.translate(0, y_offset);
            ctx.scale(1, -1);
            ctx.translate(0, -y_offset);
        }
        ctx.setImageSmoothingEnabled(old_smoothing);
    }
    _set_data(indices) {
        this._set_width_heigh_data();
        for (let i = 0, end = this.image.length; i < end; i++) {
            if (indices != null && indices.indexOf(i) < 0)
                continue;
            const img = this.image.get(i);
            let flat_img;
            if (is_NDArray(img)) {
                assert(img.dimension == 2, "expected a 2D array");
                flat_img = img;
                this._height[i] = img.shape[0];
                this._width[i] = img.shape[1];
            }
            else {
                flat_img = concat(img);
                this._height[i] = img.length;
                this._width[i] = img[0].length;
            }
            const buf8 = this._flat_img_to_buf8(flat_img);
            this._set_image_data_from_buffer(i, buf8);
        }
    }
    _index_data(index) {
        const { data_size } = this;
        for (let i = 0; i < data_size; i++) {
            const [l, r, t, b] = this._lrtb(i);
            index.add_rect(l, b, r, t);
        }
    }
    _lrtb(i) {
        const dw_i = this.dw.get(i);
        const dh_i = this.dh.get(i);
        const xr = this.renderer.xscale.source_range;
        const x1 = this._x[i];
        const x2 = xr.is_reversed ? x1 - dw_i : x1 + dw_i;
        const yr = this.renderer.yscale.source_range;
        const y1 = this._y[i];
        const y2 = yr.is_reversed ? y1 - dh_i : y1 + dh_i;
        const [l, r] = x1 < x2 ? [x1, x2] : [x2, x1];
        const [b, t] = y1 < y2 ? [y1, y2] : [y2, y1];
        return [l, r, t, b];
    }
    _set_width_heigh_data() {
        if (this.image_data == null || this.image_data.length != this.image.length)
            this.image_data = new Array(this.image.length);
        if (this._width == null || this._width.length != this.image.length)
            this._width = new Uint32Array(this.image.length);
        if (this._height == null || this._height.length != this.image.length)
            this._height = new Uint32Array(this.image.length);
    }
    _get_or_create_canvas(i) {
        const _image_data = this.image_data[i];
        if (_image_data != null && _image_data.width == this._width[i] &&
            _image_data.height == this._height[i])
            return _image_data;
        else {
            const canvas = document.createElement("canvas");
            canvas.width = this._width[i];
            canvas.height = this._height[i];
            return canvas;
        }
    }
    _set_image_data_from_buffer(i, buf8) {
        const canvas = this._get_or_create_canvas(i);
        const ctx = canvas.getContext("2d");
        const image_data = ctx.getImageData(0, 0, this._width[i], this._height[i]);
        image_data.data.set(buf8);
        ctx.putImageData(image_data, 0, 0);
        this.image_data[i] = canvas;
    }
    _map_data() {
        if (this.model.properties.dw.units == "data")
            this.sw = this.sdist(this.renderer.xscale, this._x, this.dw, "edge", this.model.dilate);
        else
            this.sw = to_screen(this.dw);
        if (this.model.properties.dh.units == "data")
            this.sh = this.sdist(this.renderer.yscale, this._y, this.dh, "edge", this.model.dilate);
        else
            this.sh = to_screen(this.dh);
    }
    _image_index(index, x, y) {
        const [l, r, t, b] = this._lrtb(index);
        const width = this._width[index];
        const height = this._height[index];
        const dx = (r - l) / width;
        const dy = (t - b) / height;
        let dim1 = Math.floor((x - l) / dx);
        let dim2 = Math.floor((y - b) / dy);
        if (this.renderer.xscale.source_range.is_reversed)
            dim1 = width - dim1 - 1;
        if (this.renderer.yscale.source_range.is_reversed)
            dim2 = height - dim2 - 1;
        return { index, dim1, dim2, flat_index: dim2 * width + dim1 };
    }
    _hit_point(geometry) {
        const { sx, sy } = geometry;
        const x = this.renderer.xscale.invert(sx);
        const y = this.renderer.yscale.invert(sy);
        const candidates = this.index.indices({ x0: x, x1: x, y0: y, y1: y });
        const result = new Selection();
        for (const index of candidates) {
            if (sx != Infinity && sy != Infinity) {
                result.image_indices.push(this._image_index(index, x, y));
            }
        }
        return result;
    }
}
ImageBaseView.__name__ = "ImageBaseView";
export class ImageBase extends XYGlyph {
    constructor(attrs) {
        super(attrs);
    }
}
_a = ImageBase;
ImageBase.__name__ = "ImageBase";
(() => {
    _a.define(({ Boolean }) => ({
        image: [p.NDArraySpec, { field: "image" }],
        dw: [p.DistanceSpec, { field: "dw" }],
        dh: [p.DistanceSpec, { field: "dh" }],
        global_alpha: [p.NumberSpec, { value: 1.0 }],
        dilate: [Boolean, false],
    }));
})();
//# sourceMappingURL=image_base.js.map