var _a;
import { Texture } from "./texture";
import { use_strict } from "../../core/util/string";
export class CanvasTexture extends Texture {
    constructor(attrs) {
        super(attrs);
    }
    get func() {
        const code = use_strict(this.code);
        return new Function("ctx", "color", "scale", "weight", code);
    }
    get_pattern(color, scale, weight) {
        const canvas = document.createElement("canvas");
        canvas.width = scale;
        canvas.height = scale;
        const pattern_ctx = canvas.getContext("2d");
        this.func.call(this, pattern_ctx, color, scale, weight);
        return canvas;
    }
}
_a = CanvasTexture;
CanvasTexture.__name__ = "CanvasTexture";
(() => {
    _a.define(({ String }) => ({
        code: [String],
    }));
})();
//# sourceMappingURL=canvas_texture.js.map