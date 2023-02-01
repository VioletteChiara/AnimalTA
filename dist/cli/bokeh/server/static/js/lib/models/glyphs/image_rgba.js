var _a;
import { ImageBase, ImageBaseView } from "./image_base";
import { isArray } from "../../core/util/types";
export class ImageRGBAView extends ImageBaseView {
    _flat_img_to_buf8(img) {
        let array;
        if (isArray(img)) {
            array = new Uint32Array(img);
        }
        else {
            array = img;
        }
        return new Uint8ClampedArray(array.buffer);
    }
}
ImageRGBAView.__name__ = "ImageRGBAView";
export class ImageRGBA extends ImageBase {
    constructor(attrs) {
        super(attrs);
    }
}
_a = ImageRGBA;
ImageRGBA.__name__ = "ImageRGBA";
(() => {
    _a.prototype.default_view = ImageRGBAView;
})();
//# sourceMappingURL=image_rgba.js.map