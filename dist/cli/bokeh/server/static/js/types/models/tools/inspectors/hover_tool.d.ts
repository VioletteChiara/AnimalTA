import { InspectTool, InspectToolView } from "./inspect_tool";
import { CallbackLike1 } from "../../callbacks/callback";
import { Tooltip, TooltipView } from "../../annotations/tooltip";
import { Renderer } from "../../renderers/renderer";
import { GlyphRenderer } from "../../renderers/glyph_renderer";
import { DataRenderer } from "../../renderers/data_renderer";
import { MoveEvent } from "../../../core/ui_events";
import { Formatters, Vars } from "../../../core/util/templating";
import * as p from "../../../core/properties";
import { Arrayable } from "../../../core/types";
import { HoverMode, PointPolicy, LinePolicy, Anchor, TooltipAttachment, MutedPolicy } from "../../../core/enums";
import { Geometry, PointGeometry, SpanGeometry, GeometryData } from "../../../core/geometry";
import { ColumnarDataSource } from "../../sources/columnar_data_source";
import { ImageIndex, Selection } from "../../selections/selection";
import { Template, TemplateView } from "../../dom";
export declare type TooltipVars = {
    index: number;
} & Vars;
export declare function _nearest_line_hit(i: number, geometry: Geometry, sx: number, sy: number, dx: Arrayable<number>, dy: Arrayable<number>): [[number, number], number];
export declare function _line_hit(xs: Arrayable<number>, ys: Arrayable<number>, ind: number): [[number, number], number];
export declare class HoverToolView extends InspectToolView {
    model: HoverTool;
    protected _ttviews: Map<Tooltip, TooltipView>;
    protected _ttmodels: Map<GlyphRenderer, Tooltip>;
    protected _template_el?: HTMLElement;
    protected _template_view?: TemplateView;
    initialize(): void;
    lazy_initialize(): Promise<void>;
    remove(): void;
    connect_signals(): void;
    protected _update_ttmodels(): Promise<void>;
    get computed_renderers(): DataRenderer[];
    get ttmodels(): Map<GlyphRenderer, Tooltip>;
    _clear(): void;
    _move(ev: MoveEvent): void;
    _move_exit(): void;
    _inspect(sx: number, sy: number): void;
    _update([renderer, { geometry }]: [Renderer, {
        geometry: Geometry;
    }]): void;
    _emit_callback(geometry: PointGeometry | SpanGeometry): void;
    _create_template(tooltips: [string, string][]): HTMLElement;
    _render_template(template: HTMLElement, tooltips: [string, string][], ds: ColumnarDataSource, i: number | ImageIndex, vars: TooltipVars): HTMLElement;
    _render_tooltips(ds: ColumnarDataSource, i: number | ImageIndex, vars: TooltipVars): HTMLElement | null;
}
export declare namespace HoverTool {
    type Attrs = p.AttrsOf<Props>;
    type Props = InspectTool.Props & {
        tooltips: p.Property<null | Template | string | [string, string][] | ((source: ColumnarDataSource, vars: TooltipVars) => HTMLElement)>;
        formatters: p.Property<Formatters>;
        renderers: p.Property<DataRenderer[] | "auto">;
        /** @deprecated */
        names: p.Property<string[]>;
        mode: p.Property<HoverMode>;
        muted_policy: p.Property<MutedPolicy>;
        point_policy: p.Property<PointPolicy>;
        line_policy: p.Property<LinePolicy>;
        show_arrow: p.Property<boolean>;
        anchor: p.Property<Anchor>;
        attachment: p.Property<TooltipAttachment>;
        callback: p.Property<CallbackLike1<HoverTool, {
            geometry: GeometryData;
            renderer: Renderer;
            index: Selection;
        }> | null>;
    };
}
export interface HoverTool extends HoverTool.Attrs {
}
export declare class HoverTool extends InspectTool {
    properties: HoverTool.Props;
    __view_type__: HoverToolView;
    constructor(attrs?: Partial<HoverTool.Attrs>);
    tool_name: string;
    icon: string;
}
//# sourceMappingURL=hover_tool.d.ts.map