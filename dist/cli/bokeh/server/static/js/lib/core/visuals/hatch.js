import { VisualProperties, VisualUniforms } from "./visual";
import { get_pattern } from "./patterns";
import * as p from "../properties";
import * as mixins from "../property_mixins";
export class Hatch extends VisualProperties {
    constructor() {
        super(...arguments);
        this._update_iteration = 0;
    }
    update() {
        this._update_iteration++;
        this._hatch_image = null;
        if (!this.doit)
            return;
        const color = this.hatch_color.get_value();
        const alpha = this.hatch_alpha.get_value();
        const scale = this.hatch_scale.get_value();
        const pattern = this.hatch_pattern.get_value();
        const weight = this.hatch_weight.get_value();
        const finalize = (image) => {
            this._hatch_image = image;
        };
        const textures = this.hatch_extra.get_value();
        const texture = textures[pattern];
        if (texture != null) {
            const image = texture.get_pattern(color, alpha, scale, weight);
            if (image instanceof Promise) {
                const { _update_iteration } = this;
                image.then((image) => {
                    if (this._update_iteration == _update_iteration) {
                        finalize(image);
                        this.obj.request_render();
                    }
                });
            }
            else {
                finalize(image);
            }
        }
        else {
            const layer = this.obj.canvas.create_layer();
            const image = get_pattern(layer, pattern, color, alpha, scale, weight);
            finalize(image);
        }
    }
    get doit() {
        const color = this.hatch_color.get_value();
        const alpha = this.hatch_alpha.get_value();
        const pattern = this.hatch_pattern.get_value();
        return !(color == null || alpha == 0 || pattern == " " || pattern == "blank" || pattern == null);
    }
    apply(ctx, rule) {
        const { doit } = this;
        if (doit) {
            this.set_value(ctx);
            ctx.layer.undo_transform(() => ctx.fill(rule));
        }
        return doit;
    }
    set_value(ctx) {
        const pattern = this.pattern(ctx);
        ctx.fillStyle = pattern ?? "transparent";
    }
    pattern(ctx) {
        const image = this._hatch_image;
        if (image == null)
            return null;
        else
            return ctx.createPattern(image, this.repetition());
    }
    repetition() {
        const pattern = this.hatch_pattern.get_value();
        const texture = this.hatch_extra.get_value()[pattern];
        if (texture == null)
            return "repeat";
        else {
            switch (texture.repetition) {
                case "repeat": return "repeat";
                case "repeat_x": return "repeat-x";
                case "repeat_y": return "repeat-y";
                case "no_repeat": return "no-repeat";
            }
        }
    }
}
Hatch.__name__ = "Hatch";
export class HatchScalar extends VisualUniforms {
    constructor() {
        super(...arguments);
        this._static_doit = false;
        this._update_iteration = 0;
    }
    _compute_static_doit() {
        const color = this.hatch_color.value;
        const alpha = this.hatch_alpha.value;
        const pattern = this.hatch_pattern.value;
        return !(color == null || alpha == 0 || pattern == " " || pattern == "blank" || pattern == null);
    }
    update() {
        this._update_iteration++;
        const n = this.hatch_color.length;
        this._hatch_image = new p.UniformScalar(null, n);
        this._static_doit = this._compute_static_doit();
        if (!this._static_doit)
            return;
        const color = this.hatch_color.value;
        const alpha = this.hatch_alpha.value;
        const scale = this.hatch_scale.value;
        const pattern = this.hatch_pattern.value;
        const weight = this.hatch_weight.value;
        const finalize = (image) => {
            this._hatch_image = new p.UniformScalar(image, n);
        };
        const textures = this.hatch_extra.value;
        const texture = textures[pattern];
        if (texture != null) {
            const image = texture.get_pattern(color, alpha, scale, weight);
            if (image instanceof Promise) {
                const { _update_iteration } = this;
                image.then((image) => {
                    if (this._update_iteration == _update_iteration) {
                        finalize(image);
                        this.obj.request_render();
                    }
                });
            }
            else {
                finalize(image);
            }
        }
        else {
            const layer = this.obj.canvas.create_layer();
            const image = get_pattern(layer, pattern, color, alpha, scale, weight);
            finalize(image);
        }
    }
    get doit() {
        return this._static_doit;
    }
    apply(ctx, rule) {
        const { doit } = this;
        if (doit) {
            this.set_value(ctx);
            ctx.layer.undo_transform(() => ctx.fill(rule));
        }
        return doit;
    }
    set_value(ctx) {
        ctx.fillStyle = this.pattern(ctx) ?? "transparent";
    }
    pattern(ctx) {
        const image = this._hatch_image.value;
        if (image == null)
            return null;
        else
            return ctx.createPattern(image, this.repetition());
    }
    repetition() {
        const pattern = this.hatch_pattern.value;
        const texture = this.hatch_extra.value[pattern];
        if (texture == null)
            return "repeat";
        else {
            switch (texture.repetition) {
                case "repeat": return "repeat";
                case "repeat_x": return "repeat-x";
                case "repeat_y": return "repeat-y";
                case "no_repeat": return "no-repeat";
            }
        }
    }
}
HatchScalar.__name__ = "HatchScalar";
export class HatchVector extends VisualUniforms {
    constructor() {
        super(...arguments);
        this._static_doit = false;
        this._update_iteration = 0;
    }
    _compute_static_doit() {
        const { hatch_color } = this;
        if (hatch_color.is_Scalar() && hatch_color.value == 0)
            return false;
        const { hatch_alpha } = this;
        if (hatch_alpha.is_Scalar() && hatch_alpha.value == 0)
            return false;
        const { hatch_pattern } = this;
        if (hatch_pattern.is_Scalar()) {
            const pattern = hatch_pattern.value;
            if (pattern == " " || pattern == "blank" || pattern == null)
                return false;
        }
        return true;
    }
    update() {
        this._update_iteration++;
        const n = this.hatch_color.length;
        this._hatch_image = new p.UniformScalar(null, n);
        this._static_doit = this._compute_static_doit();
        if (!this._static_doit)
            return;
        const resolve_image = (pattern, color, alpha, scale, weight, finalize) => {
            const textures = this.hatch_extra.value;
            const texture = textures[pattern];
            if (texture != null) {
                const image = texture.get_pattern(color, alpha, scale, weight);
                if (image instanceof Promise) {
                    const { _update_iteration } = this;
                    image.then((image) => {
                        if (this._update_iteration == _update_iteration) {
                            finalize(image);
                            this.obj.request_render();
                        }
                    });
                }
                else {
                    finalize(image);
                }
            }
            else {
                const layer = this.obj.canvas.create_layer();
                const image = get_pattern(layer, pattern, color, alpha, scale, weight);
                finalize(image);
            }
        };
        if (this.hatch_color.is_Scalar() &&
            this.hatch_alpha.is_Scalar() &&
            this.hatch_scale.is_Scalar() &&
            this.hatch_pattern.is_Scalar() &&
            this.hatch_weight.is_Scalar()) {
            const color = this.hatch_color.value;
            const alpha = this.hatch_alpha.value;
            const scale = this.hatch_scale.value;
            const pattern = this.hatch_pattern.value;
            const weight = this.hatch_weight.value;
            resolve_image(pattern, color, alpha, scale, weight, (image) => {
                this._hatch_image = new p.UniformScalar(image, n);
            });
        }
        else {
            const images = new Array(n);
            images.fill(null);
            this._hatch_image = new p.UniformVector(images);
            for (let i = 0; i < n; i++) {
                const color = this.hatch_color.get(i);
                const alpha = this.hatch_alpha.get(i);
                const scale = this.hatch_scale.get(i);
                const pattern = this.hatch_pattern.get(i);
                const weight = this.hatch_weight.get(i);
                resolve_image(pattern, color, alpha, scale, weight, (image) => {
                    images[i] = image;
                });
            }
        }
    }
    get doit() {
        return this._static_doit;
    }
    apply(ctx, i, rule) {
        const { doit } = this;
        if (doit) {
            this.set_vectorize(ctx, i);
            ctx.layer.undo_transform(() => ctx.fill(rule));
        }
        return doit;
    }
    set_vectorize(ctx, i) {
        ctx.fillStyle = this.pattern(ctx, i) ?? "transparent";
    }
    pattern(ctx, i) {
        const image = this._hatch_image.get(i);
        if (image == null)
            return null;
        else
            return ctx.createPattern(image, this.repetition(i));
    }
    repetition(i) {
        const pattern = this.hatch_pattern.get(i);
        const texture = this.hatch_extra.value[pattern];
        if (texture == null)
            return "repeat";
        else {
            switch (texture.repetition) {
                case "repeat": return "repeat";
                case "repeat_x": return "repeat-x";
                case "repeat_y": return "repeat-y";
                case "no_repeat": return "no-repeat";
            }
        }
    }
}
HatchVector.__name__ = "HatchVector";
Hatch.prototype.type = "hatch";
Hatch.prototype.attrs = Object.keys(mixins.Hatch);
HatchScalar.prototype.type = "hatch";
HatchScalar.prototype.attrs = Object.keys(mixins.HatchScalar);
HatchVector.prototype.type = "hatch";
HatchVector.prototype.attrs = Object.keys(mixins.HatchVector);
//# sourceMappingURL=hatch.js.map