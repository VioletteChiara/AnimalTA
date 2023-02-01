var _a;
import { Renderer, RendererView } from "./renderer";
export class DataRendererView extends RendererView {
    get xscale() {
        return this.coordinates.x_scale;
    }
    get yscale() {
        return this.coordinates.y_scale;
    }
}
DataRendererView.__name__ = "DataRendererView";
export class DataRenderer extends Renderer {
    constructor(attrs) {
        super(attrs);
    }
    get selection_manager() {
        return this.get_selection_manager();
    }
}
_a = DataRenderer;
DataRenderer.__name__ = "DataRenderer";
(() => {
    _a.override({
        level: "glyph",
    });
})();
//# sourceMappingURL=data_renderer.js.map