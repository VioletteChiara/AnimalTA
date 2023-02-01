import { Model } from "../../model";
import { LayoutDOM, LayoutDOMView } from "../layouts/layout_dom";
import { Styles } from "./styles";
import { View } from "../../core/view";
import { DOMView } from "../../core/dom_view";
import * as p from "../../core/properties";
import { Index as DataIndex } from "../../core/util/templating";
import { ColumnarDataSource } from "../sources/columnar_data_source";
export { Styles };
export declare abstract class DOMNodeView extends DOMView {
    model: DOMNode;
}
export declare namespace DOMNode {
    type Attrs = p.AttrsOf<Props>;
    type Props = Model.Props;
}
export interface DOMNode extends DOMNode.Attrs {
}
export declare abstract class DOMNode extends Model {
    properties: DOMNode.Props;
    __view_type__: DOMNodeView;
    static __module__: string;
    constructor(attrs?: Partial<DOMNode.Attrs>);
}
export declare class TextView extends DOMNodeView {
    model: Text;
    el: globalThis.Text;
    render(): void;
    protected _createElement(): globalThis.Text;
}
export declare namespace Text {
    type Attrs = p.AttrsOf<Props>;
    type Props = DOMNode.Props & {
        content: p.Property<string>;
    };
}
export interface Text extends Text.Attrs {
}
export declare class Text extends DOMNode {
    properties: Text.Props;
    __view_type__: TextView;
    constructor(attrs?: Partial<Text.Attrs>);
}
export declare abstract class PlaceholderView extends DOMNodeView {
    model: Placeholder;
    static tag_name: "span";
    abstract update(source: ColumnarDataSource, i: DataIndex, vars: object): void;
}
export declare namespace Placeholder {
    type Attrs = p.AttrsOf<Props>;
    type Props = DOMNode.Props & {};
}
export interface Placeholder extends Placeholder.Attrs {
}
export declare abstract class Placeholder extends DOMNode {
    properties: Placeholder.Props;
    __view_type__: PlaceholderView;
    constructor(attrs?: Partial<Placeholder.Attrs>);
}
export declare class IndexView extends PlaceholderView {
    model: Index;
    update(_source: ColumnarDataSource, i: DataIndex, _vars: object): void;
}
export declare namespace Index {
    type Attrs = p.AttrsOf<Props>;
    type Props = Placeholder.Props & {};
}
export interface Index extends Index.Attrs {
}
export declare class Index extends Placeholder {
    properties: Index.Props;
    __view_type__: IndexView;
    constructor(attrs?: Partial<Index.Attrs>);
}
export declare class ValueRefView extends PlaceholderView {
    model: ValueRef;
    update(source: ColumnarDataSource, i: DataIndex, _vars: object): void;
}
export declare namespace ValueRef {
    type Attrs = p.AttrsOf<Props>;
    type Props = Placeholder.Props & {
        field: p.Property<string>;
    };
}
export interface ValueRef extends ValueRef.Attrs {
}
export declare class ValueRef extends Placeholder {
    properties: ValueRef.Props;
    __view_type__: ValueRefView;
    constructor(attrs?: Partial<ValueRef.Attrs>);
}
export declare class ColorRefView extends ValueRefView {
    model: ColorRef;
    value_el?: HTMLElement;
    swatch_el?: HTMLElement;
    render(): void;
    update(source: ColumnarDataSource, i: DataIndex, _vars: object): void;
}
export declare namespace ColorRef {
    type Attrs = p.AttrsOf<Props>;
    type Props = ValueRef.Props & {
        hex: p.Property<boolean>;
        swatch: p.Property<boolean>;
    };
}
export interface ColorRef extends ColorRef.Attrs {
}
export declare class ColorRef extends ValueRef {
    properties: ColorRef.Props;
    __view_type__: ColorRefView;
    constructor(attrs?: Partial<ColorRef.Attrs>);
}
export declare abstract class DOMElementView extends DOMNodeView {
    model: DOMElement;
    el: HTMLElement;
    child_views: Map<DOMNode | LayoutDOM, DOMNodeView | LayoutDOMView>;
    lazy_initialize(): Promise<void>;
    render(): void;
}
export declare namespace DOMElement {
    type Attrs = p.AttrsOf<Props>;
    type Props = DOMNode.Props & {
        style: p.Property<Styles | {
            [key: string]: string;
        } | null>;
        children: p.Property<(string | DOMNode | LayoutDOM)[]>;
    };
}
export interface DOMElement extends DOMElement.Attrs {
}
export declare abstract class DOMElement extends DOMNode {
    properties: DOMElement.Props;
    __view_type__: DOMElementView;
    constructor(attrs?: Partial<DOMElement.Attrs>);
}
export declare abstract class ActionView extends View {
    model: Action;
    abstract update(source: ColumnarDataSource, i: DataIndex, vars: object): void;
}
export declare namespace Action {
    type Attrs = p.AttrsOf<Props>;
    type Props = Model.Props & {};
}
export interface Action extends Action.Attrs {
}
export declare abstract class Action extends Model {
    properties: Action.Props;
    __view_type__: ActionView;
    static __module__: string;
    constructor(attrs?: Partial<Action.Attrs>);
}
export declare class TemplateView extends DOMElementView {
    model: Template;
    static tag_name: "div";
    action_views: Map<Action, ActionView>;
    lazy_initialize(): Promise<void>;
    remove(): void;
    update(source: ColumnarDataSource, i: DataIndex, vars?: object): void;
}
export declare namespace Template {
    type Attrs = p.AttrsOf<Props>;
    type Props = DOMElement.Props & {
        actions: p.Property<Action[]>;
    };
}
export interface Template extends Template.Attrs {
}
export declare class Template extends DOMElement {
    properties: Template.Props;
    __view_type__: TemplateView;
}
export declare class SpanView extends DOMElementView {
    model: Span;
    static tag_name: "span";
}
export declare class Span extends DOMElement {
    __view_type__: SpanView;
}
export declare class DivView extends DOMElementView {
    model: Div;
    static tag_name: "div";
}
export declare class Div extends DOMElement {
    __view_type__: DivView;
}
export declare class TableView extends DOMElementView {
    model: Table;
    static tag_name: "table";
}
export declare class Table extends DOMElement {
    __view_type__: TableView;
}
export declare class TableRowView extends DOMElementView {
    model: TableRow;
    static tag_name: "tr";
}
export declare class TableRow extends DOMElement {
    __view_type__: TableRowView;
}
import { RendererGroup } from "../renderers/renderer";
export declare class ToggleGroupView extends ActionView {
    model: ToggleGroup;
    update(_source: ColumnarDataSource, i: DataIndex, _vars: object): void;
}
export declare namespace ToggleGroup {
    type Attrs = p.AttrsOf<Props>;
    type Props = Action.Props & {
        groups: p.Property<RendererGroup[]>;
    };
}
export interface ToggleGroup extends ToggleGroup.Attrs {
}
export declare class ToggleGroup extends Action {
    properties: ToggleGroup.Props;
    __view_type__: ToggleGroupView;
    constructor(attrs?: Partial<ToggleGroup.Attrs>);
}
//# sourceMappingURL=index.d.ts.map