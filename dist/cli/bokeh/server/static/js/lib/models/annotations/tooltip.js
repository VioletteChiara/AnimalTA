var _a;
import { Annotation, AnnotationView } from "./annotation";
import { TooltipAttachment } from "../../core/enums";
import { div, display, undisplay, empty, remove, classes } from "../../core/dom";
import tooltips_css, * as tooltips from "../../styles/tooltips.css";
const arrow_size = 10; // XXX: keep in sync with less
export class TooltipView extends AnnotationView {
    initialize() {
        super.initialize();
        this.el = div({ class: tooltips.tooltip });
        undisplay(this.el);
        this.plot_view.canvas_view.add_overlay(this.el);
    }
    remove() {
        remove(this.el);
        super.remove();
    }
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.properties.content.change, () => this.render());
        this.connect(this.model.properties.position.change, () => this._reposition());
    }
    styles() {
        return [...super.styles(), tooltips_css];
    }
    render() {
        if (!this.model.visible)
            undisplay(this.el);
        super.render();
    }
    _render() {
        const { content } = this.model;
        if (content == null) {
            undisplay(this.el);
            return;
        }
        empty(this.el);
        classes(this.el).toggle("bk-tooltip-custom", this.model.custom);
        this.el.appendChild(content);
        if (this.model.show_arrow)
            this.el.classList.add(tooltips.tooltip_arrow);
    }
    _reposition() {
        const { position } = this.model;
        if (position == null) {
            undisplay(this.el);
            return;
        }
        const [sx, sy] = position;
        const side = (() => {
            const area = this.parent.layout.bbox.relative();
            const { attachment } = this.model;
            switch (attachment) {
                case "horizontal":
                    return sx < area.hcenter ? "right" : "left";
                case "vertical":
                    return sy < area.vcenter ? "below" : "above";
                default:
                    return attachment;
            }
        })();
        this.el.classList.remove(tooltips.right);
        this.el.classList.remove(tooltips.left);
        this.el.classList.remove(tooltips.above);
        this.el.classList.remove(tooltips.below);
        display(this.el); // XXX: {offset,client}Width() gives 0 when display="none"
        // slightly confusing: side "left" (for example) is relative to point that
        // is being annotated but CS class ".bk-left" is relative to the tooltip itself
        let top;
        let left = null;
        let right = null;
        switch (side) {
            case "right":
                this.el.classList.add(tooltips.left);
                left = sx + (this.el.offsetWidth - this.el.clientWidth) + arrow_size;
                top = sy - this.el.offsetHeight / 2;
                break;
            case "left":
                this.el.classList.add(tooltips.right);
                right = (this.plot_view.layout.bbox.width - sx) + arrow_size;
                top = sy - this.el.offsetHeight / 2;
                break;
            case "below":
                this.el.classList.add(tooltips.above);
                top = sy + (this.el.offsetHeight - this.el.clientHeight) + arrow_size;
                left = Math.round(sx - this.el.offsetWidth / 2);
                break;
            case "above":
                this.el.classList.add(tooltips.below);
                top = sy - this.el.offsetHeight - arrow_size;
                left = Math.round(sx - this.el.offsetWidth / 2);
                break;
        }
        this.el.style.top = `${top}px`;
        this.el.style.left = left != null ? `${left}px` : "auto";
        this.el.style.right = right != null ? `${right}px` : "auto";
    }
}
TooltipView.__name__ = "TooltipView";
export class Tooltip extends Annotation {
    constructor(attrs) {
        super(attrs);
    }
    clear() {
        this.position = null;
    }
}
_a = Tooltip;
Tooltip.__name__ = "Tooltip";
(() => {
    _a.prototype.default_view = TooltipView;
    _a.define(({ Boolean }) => ({
        attachment: [TooltipAttachment, "horizontal"],
        inner_only: [Boolean, true],
        show_arrow: [Boolean, true],
    }));
    _a.internal(({ Boolean, Number, Tuple, Ref, Nullable }) => ({
        position: [Nullable(Tuple(Number, Number)), null],
        content: [Ref(HTMLElement), () => div()],
        custom: [Boolean],
    }));
    _a.override({
        level: "overlay",
    });
})();
//# sourceMappingURL=tooltip.js.map