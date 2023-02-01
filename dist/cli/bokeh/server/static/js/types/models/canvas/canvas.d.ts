import { HasProps } from "../../core/has_props";
import { DOMView } from "../../core/dom_view";
import * as p from "../../core/properties";
import { OutputBackend } from "../../core/enums";
import { UIEventBus } from "../../core/ui_events";
import { BBox } from "../../core/util/bbox";
import { Context2d, CanvasLayer } from "../../core/util/canvas";
import { PlotView } from "../plots/plot";
import type { ReglWrapper } from "../glyphs/webgl/regl_wrap";
export declare type FrameBox = [number, number, number, number];
export declare type WebGLState = {
    readonly canvas: HTMLCanvasElement;
    readonly regl_wrapper: ReglWrapper;
};
export declare class CanvasView extends DOMView {
    model: Canvas;
    el: HTMLElement;
    bbox: BBox;
    webgl: WebGLState | null;
    underlays_el: HTMLElement;
    primary: CanvasLayer;
    overlays: CanvasLayer;
    overlays_el: HTMLElement;
    events_el: HTMLElement;
    ui_event_bus: UIEventBus;
    initialize(): void;
    lazy_initialize(): Promise<void>;
    remove(): void;
    add_underlay(el: HTMLElement): void;
    add_overlay(el: HTMLElement): void;
    add_event(el: HTMLElement): void;
    get pixel_ratio(): number;
    resize(width: number, height: number): void;
    prepare_webgl(frame_box: FrameBox): void;
    blit_webgl(ctx: Context2d): void;
    protected _clear_webgl(): void;
    compose(): CanvasLayer;
    create_layer(): CanvasLayer;
    to_blob(): Promise<Blob>;
    plot_views: PlotView[];
}
export declare namespace Canvas {
    type Attrs = p.AttrsOf<Props>;
    type Props = HasProps.Props & {
        hidpi: p.Property<boolean>;
        output_backend: p.Property<OutputBackend>;
    };
}
export interface Canvas extends Canvas.Attrs {
}
export declare class Canvas extends HasProps {
    properties: Canvas.Props;
    __view_type__: CanvasView;
    constructor(attrs?: Partial<Canvas.Attrs>);
}
//# sourceMappingURL=canvas.d.ts.map