var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k, _l, _m, _o;
import { Model } from "../../model";
import { LayoutDOM } from "../layouts/layout_dom";
import { Styles } from "./styles";
import { span } from "../../core/dom";
import { View } from "../../core/view";
import { DOMView } from "../../core/dom_view";
import { build_views, remove_views } from "../../core/build_views";
import { isString } from "../../core/util/types";
import { entries } from "../../core/util/object";
import * as styles from "../../styles/tooltips.css";
import { _get_column_value } from "../../core/util/templating";
export { Styles };
export class DOMNodeView extends DOMView {
}
DOMNodeView.__name__ = "DOMNodeView";
export class DOMNode extends Model {
    constructor(attrs) {
        super(attrs);
    }
}
DOMNode.__name__ = "DOMNode";
DOMNode.__module__ = "bokeh.models.dom";
export class TextView extends DOMNodeView {
    render() {
        super.render();
        this.el.textContent = this.model.content;
    }
    _createElement() {
        return document.createTextNode("");
    }
}
TextView.__name__ = "TextView";
export class Text extends DOMNode {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Text;
Text.__name__ = "Text";
(() => {
    _a.prototype.default_view = TextView;
    _a.define(({ String }) => ({
        content: [String, ""],
    }));
})();
export class PlaceholderView extends DOMNodeView {
}
PlaceholderView.__name__ = "PlaceholderView";
PlaceholderView.tag_name = "span";
export class Placeholder extends DOMNode {
    constructor(attrs) {
        super(attrs);
    }
}
_b = Placeholder;
Placeholder.__name__ = "Placeholder";
(() => {
    _b.define(({}) => ({}));
})();
export class IndexView extends PlaceholderView {
    update(_source, i, _vars /*, formatters?: Formatters*/) {
        this.el.textContent = i.toString();
    }
}
IndexView.__name__ = "IndexView";
export class Index extends Placeholder {
    constructor(attrs) {
        super(attrs);
    }
}
_c = Index;
Index.__name__ = "Index";
(() => {
    _c.prototype.default_view = IndexView;
    _c.define(({}) => ({}));
})();
export class ValueRefView extends PlaceholderView {
    update(source, i, _vars /*, formatters?: Formatters*/) {
        const value = _get_column_value(this.model.field, source, i);
        const text = value == null ? "???" : `${value}`; //.toString()
        this.el.textContent = text;
    }
}
ValueRefView.__name__ = "ValueRefView";
export class ValueRef extends Placeholder {
    constructor(attrs) {
        super(attrs);
    }
}
_d = ValueRef;
ValueRef.__name__ = "ValueRef";
(() => {
    _d.prototype.default_view = ValueRefView;
    _d.define(({ String }) => ({
        field: [String],
    }));
})();
export class ColorRefView extends ValueRefView {
    render() {
        super.render();
        this.value_el = span();
        this.swatch_el = span({ class: styles.tooltip_color_block }, " ");
        this.el.appendChild(this.value_el);
        this.el.appendChild(this.swatch_el);
    }
    update(source, i, _vars /*, formatters?: Formatters*/) {
        const value = _get_column_value(this.model.field, source, i);
        const text = value == null ? "???" : `${value}`; //.toString()
        this.el.textContent = text;
    }
}
ColorRefView.__name__ = "ColorRefView";
export class ColorRef extends ValueRef {
    constructor(attrs) {
        super(attrs);
    }
}
_e = ColorRef;
ColorRef.__name__ = "ColorRef";
(() => {
    _e.prototype.default_view = ColorRefView;
    _e.define(({ Boolean }) => ({
        hex: [Boolean, true],
        swatch: [Boolean, true],
    }));
})();
export class DOMElementView extends DOMNodeView {
    constructor() {
        super(...arguments);
        this.child_views = new Map();
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        const children = this.model.children.filter((obj) => obj instanceof Model);
        await build_views(this.child_views, children, { parent: this });
    }
    render() {
        super.render();
        const { style } = this.model;
        if (style != null) {
            /*
            type IsString<T> = T extends string ? T : never
            type Key = Exclude<IsString<keyof CSSStyleDeclaration>,
              "length" | "parentRule" | "getPropertyPriority" | "getPropertyValue" | "item" | "removeProperty" | "setProperty">
            //this.el.style[key as Key] = value
            */
            if (style instanceof Styles) {
                for (const prop of style) {
                    const value = prop.get_value();
                    if (isString(value)) {
                        const name = prop.attr.replace(/_/g, "-");
                        if (this.el.style.hasOwnProperty(name)) {
                            this.el.style.setProperty(name, value);
                        }
                    }
                }
            }
            else {
                for (const [key, value] of entries(style)) {
                    const name = key.replace(/_/g, "-");
                    if (this.el.style.hasOwnProperty(name)) {
                        this.el.style.setProperty(name, value);
                    }
                }
            }
        }
        for (const child of this.model.children) {
            if (isString(child)) {
                const node = document.createTextNode(child);
                this.el.appendChild(node);
            }
            else {
                const child_view = this.child_views.get(child);
                child_view.renderTo(this.el);
            }
        }
    }
}
DOMElementView.__name__ = "DOMElementView";
export class DOMElement extends DOMNode {
    constructor(attrs) {
        super(attrs);
    }
}
_f = DOMElement;
DOMElement.__name__ = "DOMElement";
(() => {
    _f.define(({ String, Array, Dict, Or, Nullable, Ref }) => ({
        style: [Nullable(Or(Ref(Styles), Dict(String))), null],
        children: [Array(Or(String, Ref(DOMNode), Ref(LayoutDOM))), []],
    }));
})();
export class ActionView extends View {
}
ActionView.__name__ = "ActionView";
export class Action extends Model {
    constructor(attrs) {
        super(attrs);
    }
}
_g = Action;
Action.__name__ = "Action";
Action.__module__ = "bokeh.models.dom";
(() => {
    _g.define(({}) => ({}));
})();
export class TemplateView extends DOMElementView {
    constructor() {
        super(...arguments);
        this.action_views = new Map();
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        await build_views(this.action_views, this.model.actions, { parent: this });
    }
    remove() {
        remove_views(this.action_views);
        super.remove();
    }
    update(source, i, vars = {} /*, formatters?: Formatters*/) {
        function descend(obj) {
            for (const child of obj.child_views.values()) {
                if (child instanceof PlaceholderView) {
                    child.update(source, i, vars);
                }
                else if (child instanceof DOMElementView) {
                    descend(child);
                }
            }
        }
        descend(this);
        for (const action of this.action_views.values()) {
            action.update(source, i, vars);
        }
    }
}
TemplateView.__name__ = "TemplateView";
TemplateView.tag_name = "div";
export class Template extends DOMElement {
}
_h = Template;
Template.__name__ = "Template";
(() => {
    _h.prototype.default_view = TemplateView;
    _h.define(({ Array, Ref }) => ({
        actions: [Array(Ref(Action)), []],
    }));
})();
export class SpanView extends DOMElementView {
}
SpanView.__name__ = "SpanView";
SpanView.tag_name = "span";
export class Span extends DOMElement {
}
_j = Span;
Span.__name__ = "Span";
(() => {
    _j.prototype.default_view = SpanView;
})();
export class DivView extends DOMElementView {
}
DivView.__name__ = "DivView";
DivView.tag_name = "div";
export class Div extends DOMElement {
}
_k = Div;
Div.__name__ = "Div";
(() => {
    _k.prototype.default_view = DivView;
})();
export class TableView extends DOMElementView {
}
TableView.__name__ = "TableView";
TableView.tag_name = "table";
export class Table extends DOMElement {
}
_l = Table;
Table.__name__ = "Table";
(() => {
    _l.prototype.default_view = TableView;
})();
export class TableRowView extends DOMElementView {
}
TableRowView.__name__ = "TableRowView";
TableRowView.tag_name = "tr";
export class TableRow extends DOMElement {
}
_m = TableRow;
TableRow.__name__ = "TableRow";
(() => {
    _m.prototype.default_view = TableRowView;
})();
/////
import { RendererGroup } from "../renderers/renderer";
import { enumerate } from "../../core/util/iterator";
export class ToggleGroupView extends ActionView {
    update(_source, i, _vars /*, formatters?: Formatters*/) {
        for (const [group, j] of enumerate(this.model.groups)) {
            group.visible = i == j;
        }
    }
}
ToggleGroupView.__name__ = "ToggleGroupView";
export class ToggleGroup extends Action {
    constructor(attrs) {
        super(attrs);
    }
}
_o = ToggleGroup;
ToggleGroup.__name__ = "ToggleGroup";
(() => {
    _o.prototype.default_view = ToggleGroupView;
    _o.define(({ Array, Ref }) => ({
        groups: [Array(Ref(RendererGroup)), []],
    }));
})();
/*
export namespace X {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Y.Props & {}
}

export interface X extends X.Attrs {}

export class X extends Y {
  override properties: X.Props

  constructor(attrs?: Partial<X.Attrs>) {
    super(attrs)
  }

  static {
    this.define<X.Props>(({}) => ({
    }))
  }
}
*/
//# sourceMappingURL=index.js.map