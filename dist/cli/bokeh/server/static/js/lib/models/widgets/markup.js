var _a;
import { CachedVariadicBox } from "../../core/layout/html";
import { div } from "../../core/dom";
import { default_provider } from "../text/providers";
import { Widget, WidgetView } from "./widget";
import clearfix_css, { clearfix } from "../../styles/clearfix.css";
export class MarkupView extends WidgetView {
    get provider() {
        return default_provider;
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        if (this.provider.status == "not_started")
            await this.provider.fetch();
        if (this.provider.status == "not_started" || this.provider.status == "loading")
            this.provider.ready.connect(() => {
                if (this.contains_tex_string())
                    this.rerender();
            });
    }
    after_layout() {
        super.after_layout();
        if (this.provider.status === "loading")
            this._has_finished = false;
    }
    rerender() {
        this.layout.invalidate_cache();
        this.render();
        this.root.compute_layout(); // XXX: invalidate_layout?
    }
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.change, () => {
            this.rerender();
        });
    }
    styles() {
        return [...super.styles(), clearfix_css];
    }
    _update_layout() {
        this.layout = new CachedVariadicBox(this.el);
        this.layout.set_sizing(this.box_sizing());
    }
    render() {
        super.render();
        const style = { ...this.model.style, display: "inline-block" };
        this.markup_el = div({ class: clearfix, style });
        this.el.appendChild(this.markup_el);
        if (this.provider.status == "failed" || this.provider.status == "loaded")
            this._has_finished = true;
    }
    has_math_disabled() {
        return this.model.disable_math || !this.contains_tex_string();
    }
    process_tex() {
        if (!this.provider.MathJax)
            return this.model.text;
        const { text } = this.model;
        const tex_parts = this.provider.MathJax.find_tex(text);
        const processed_text = [];
        let last_index = 0;
        for (const part of tex_parts) {
            processed_text.push(text.slice(last_index, part.start.n));
            processed_text.push(this.provider.MathJax.tex2svg(part.math, { display: part.display }).outerHTML);
            last_index = part.end.n;
        }
        if (last_index < text.length)
            processed_text.push(text.slice(last_index));
        return processed_text.join("");
    }
    contains_tex_string() {
        if (!this.provider.MathJax)
            return false;
        return this.provider.MathJax.find_tex(this.model.text).length > 0;
    }
    ;
}
MarkupView.__name__ = "MarkupView";
export class Markup extends Widget {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Markup;
Markup.__name__ = "Markup";
(() => {
    _a.define(({ Boolean, String, Dict }) => ({
        text: [String, ""],
        style: [Dict(String), {}],
        disable_math: [Boolean, false],
    }));
})();
//# sourceMappingURL=markup.js.map