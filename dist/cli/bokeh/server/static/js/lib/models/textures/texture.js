var _a;
import { Model } from "../../model";
import { TextureRepetition } from "../../core/enums";
export class Texture extends Model {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Texture;
Texture.__name__ = "Texture";
(() => {
    _a.define(() => ({
        repetition: [TextureRepetition, "repeat"],
    }));
})();
//# sourceMappingURL=texture.js.map