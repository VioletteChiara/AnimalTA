var _a;
import { Annotation, AnnotationView } from "./annotation";
import { Toolbar } from "../tools/toolbar";
import { build_view } from "../../core/build_views";
import { div, empty, position, display, undisplay, remove } from "../../core/dom";
import { SideLayout } from "../../core/layout/side_panel";
import { BBox } from "../../core/util/bbox";
export class ToolbarPanelView extends AnnotationView {
    constructor() {
        super(...arguments);
        this._invalidate_toolbar = true;
        this._previous_bbox = new BBox();
    }
    update_layout() {
        this.layout = new SideLayout(this.panel, () => this.get_size(), true);
    }
    initialize() {
        super.initialize();
        this.el = div();
        this.plot_view.canvas_view.add_event(this.el);
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        this._toolbar_view = await build_view(this.model.toolbar, { parent: this });
        this.plot_view.visibility_callbacks.push((visible) => this._toolbar_view.set_visibility(visible));
    }
    remove() {
        this._toolbar_view.remove();
        remove(this.el);
        super.remove();
    }
    render() {
        if (!this.model.visible)
            undisplay(this.el);
        super.render();
    }
    _render() {
        // TODO: this should be handled by the layout
        const { bbox } = this.layout;
        if (!this._previous_bbox.equals(bbox)) {
            position(this.el, bbox);
            this._previous_bbox = bbox;
            this._invalidate_toolbar = true;
        }
        if (this._invalidate_toolbar) {
            this.el.style.position = "absolute";
            this.el.style.overflow = "hidden";
            empty(this.el);
            this.el.appendChild(this._toolbar_view.el);
            this._toolbar_view.layout.bbox = bbox;
            this._toolbar_view.render();
            this._invalidate_toolbar = false;
        }
        display(this.el);
    }
    _get_size() {
        const { tools, logo } = this.model.toolbar;
        return {
            width: tools.length * 30 + (logo != null ? 25 : 0) + 15,
            height: 30,
        };
    }
}
ToolbarPanelView.__name__ = "ToolbarPanelView";
export class ToolbarPanel extends Annotation {
    constructor(attrs) {
        super(attrs);
    }
}
_a = ToolbarPanel;
ToolbarPanel.__name__ = "ToolbarPanel";
(() => {
    _a.prototype.default_view = ToolbarPanelView;
    _a.define(({ Ref }) => ({
        toolbar: [Ref(Toolbar)],
    }));
})();
//# sourceMappingURL=toolbar_panel.js.map