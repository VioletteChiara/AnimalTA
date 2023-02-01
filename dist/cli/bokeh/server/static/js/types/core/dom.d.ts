import { Size, Box, Extents } from "./types";
export declare type HTMLAttrs = {
    [name: string]: unknown;
};
export declare type HTMLItem = string | Node | NodeList | HTMLCollection | null | undefined;
export declare type HTMLChild = HTMLItem | HTMLItem[];
export declare function createElement<T extends keyof HTMLElementTagNameMap>(tag: T, attrs: HTMLAttrs | null, ...children: HTMLChild[]): HTMLElementTagNameMap[T];
export declare const div: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLDivElement, span: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLSpanElement, canvas: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLCanvasElement, link: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLLinkElement, style: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLStyleElement, a: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLAnchorElement, p: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLParagraphElement, i: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLElement, pre: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLPreElement, button: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLButtonElement, label: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLLabelElement, input: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLInputElement, select: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLSelectElement, option: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLOptionElement, optgroup: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLOptGroupElement, textarea: (attrs?: HTMLAttrs | HTMLChild, ...children: HTMLChild[]) => HTMLTextAreaElement;
export declare function createSVGElement<T extends keyof SVGElementTagNameMap>(tag: T, attrs: {
    [key: string]: string | false | null | undefined;
}, ...children: HTMLChild[]): SVGElementTagNameMap[T];
export declare function nbsp(): Text;
export declare function append(element: HTMLElement, ...children: Element[]): void;
export declare function remove(element: Node): void;
export declare const removeElement: typeof remove;
export declare function replaceWith(element: HTMLElement, replacement: HTMLElement): void;
export declare function prepend(element: HTMLElement, ...nodes: Node[]): void;
export declare function empty(node: Node, attrs?: boolean): void;
export declare function display(element: HTMLElement): void;
export declare function undisplay(element: HTMLElement): void;
export declare function show(element: HTMLElement): void;
export declare function hide(element: HTMLElement): void;
export declare function offset(element: HTMLElement): {
    top: number;
    left: number;
};
export declare function matches(el: HTMLElement, selector: string): boolean;
export declare function parent(el: HTMLElement, selector: string): HTMLElement | null;
export declare type ElementExtents = {
    border: Extents;
    margin: Extents;
    padding: Extents;
};
export declare function extents(el: HTMLElement): ElementExtents;
export declare function size(el: HTMLElement): Size;
export declare function scroll_size(el: HTMLElement): Size;
export declare function outer_size(el: HTMLElement): Size;
export declare function content_size(el: HTMLElement): Size;
export declare function position(el: HTMLElement, box: Box, margin?: Extents): void;
export declare function children(el: HTMLElement): HTMLElement[];
export declare class ClassList {
    readonly el: HTMLElement;
    private readonly classList;
    constructor(el: HTMLElement);
    get values(): string[];
    has(cls: string): boolean;
    add(...classes: string[]): this;
    remove(...classes: string[]): this;
    clear(): this;
    toggle(cls: string, activate?: boolean): this;
}
export declare function classes(el: HTMLElement): ClassList;
export declare function toggle_attribute(el: HTMLElement, attr: string, state?: boolean): void;
export declare enum Keys {
    Backspace = 8,
    Tab = 9,
    Enter = 13,
    Esc = 27,
    PageUp = 33,
    PageDown = 34,
    Left = 37,
    Up = 38,
    Right = 39,
    Down = 40,
    Delete = 46
}
export declare function undisplayed<T>(el: HTMLElement, fn: () => T): T;
export declare function unsized<T>(el: HTMLElement, fn: () => T): T;
export declare function sized<T>(el: HTMLElement, size: Partial<Size>, fn: () => T): T;
export declare class StyleSheet {
    readonly root: HTMLElement;
    private readonly style;
    private readonly known;
    constructor(root: HTMLElement);
    append(css: string): void;
}
export declare const stylesheet: StyleSheet;
export declare function dom_ready(): Promise<void>;
//# sourceMappingURL=dom.d.ts.map