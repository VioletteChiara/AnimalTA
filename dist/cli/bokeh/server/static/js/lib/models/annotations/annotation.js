var _a;
import { Renderer, RendererView } from "../renderers/renderer";
export class AnnotationView extends RendererView {
    get_size() {
        if (this.model.visible) {
            const { width, height } = this._get_size();
            return { width: Math.round(width), height: Math.round(height) };
        }
        else
            return { width: 0, height: 0 };
    }
    _get_size() {
        throw new Error("not implemented");
    }
    connect_signals() {
        super.connect_signals();
        const p = this.model.properties;
        this.on_change(p.visible, () => {
            if (this.layout != null) {
                this.layout.visible = this.model.visible;
                this.plot_view.request_layout();
            }
        });
    }
    get needs_clip() {
        return this.layout == null; // TODO: change this, when center layout is fully implemented
    }
    serializable_state() {
        const state = super.serializable_state();
        return this.layout == null ? state : { ...state, bbox: this.layout.bbox.box };
    }
}
AnnotationView.__name__ = "AnnotationView";
export class Annotation extends Renderer {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Annotation;
Annotation.__name__ = "Annotation";
(() => {
    _a.override({
        level: "annotation",
    });
})();
//# sourceMappingURL=annotation.js.map