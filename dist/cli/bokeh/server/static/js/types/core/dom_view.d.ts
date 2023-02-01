import { View } from "./view";
export interface DOMView extends View {
    constructor: Function & {
        tag_name: keyof HTMLElementTagNameMap;
    };
}
export declare abstract class DOMView extends View {
    static tag_name: keyof HTMLElementTagNameMap;
    el: Node;
    readonly root: DOMView;
    initialize(): void;
    remove(): void;
    css_classes(): string[];
    render(): void;
    renderTo(element: Node): void;
    protected _createElement(): this["el"];
}
//# sourceMappingURL=dom_view.d.ts.map