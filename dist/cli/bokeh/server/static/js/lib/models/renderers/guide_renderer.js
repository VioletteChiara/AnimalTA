var _a;
import { Renderer, RendererView } from "./renderer";
export class GuideRendererView extends RendererView {
}
GuideRendererView.__name__ = "GuideRendererView";
export class GuideRenderer extends Renderer {
    constructor(attrs) {
        super(attrs);
    }
}
_a = GuideRenderer;
GuideRenderer.__name__ = "GuideRenderer";
(() => {
    _a.override({
        level: "guide",
    });
})();
//# sourceMappingURL=guide_renderer.js.map