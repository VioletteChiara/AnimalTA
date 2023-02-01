import { Signal } from "./signaling";
import { Keys } from "./dom";
import { PlotView } from "../models/plots/plot";
import { ToolView } from "../models/tools/tool";
import { RendererView } from "../models/renderers/renderer";
import type { CanvasView } from "../models/canvas/canvas";
declare type HammerEvent = {
    type: string;
    deltaX: number;
    deltaY: number;
    scale: number;
    rotation: number;
    srcEvent: TouchEvent | MouseEvent | PointerEvent;
};
export declare type ScreenCoord = {
    sx: number;
    sy: number;
};
export declare type PanEvent = {
    type: "pan" | "panstart" | "panend";
    sx: number;
    sy: number;
    deltaX: number;
    deltaY: number;
    shiftKey: boolean;
    ctrlKey: boolean;
};
export declare type PinchEvent = {
    type: "pinch" | "pinchstart" | "pinchend";
    sx: number;
    sy: number;
    scale: number;
    shiftKey: boolean;
    ctrlKey: boolean;
};
export declare type RotateEvent = {
    type: "rotate" | "rotatestart" | "rotateend";
    sx: number;
    sy: number;
    rotation: number;
    shiftKey: boolean;
    ctrlKey: boolean;
};
export declare type GestureEvent = PanEvent | PinchEvent | RotateEvent;
export declare type TapEvent = {
    type: "tap" | "doubletap" | "press" | "pressup" | "contextmenu";
    sx: number;
    sy: number;
    shiftKey: boolean;
    ctrlKey: boolean;
};
export declare type MoveEvent = {
    type: "mousemove" | "mouseenter" | "mouseleave";
    sx: number;
    sy: number;
    shiftKey: boolean;
    ctrlKey: boolean;
};
export declare type ScrollEvent = {
    type: "wheel";
    sx: number;
    sy: number;
    delta: number;
    shiftKey: boolean;
    ctrlKey: boolean;
};
export declare type UIEvent = GestureEvent | TapEvent | MoveEvent | ScrollEvent;
export declare type KeyEvent = {
    type: "keyup" | "keydown";
    keyCode: Keys;
};
export declare type EventType = "pan" | "pinch" | "rotate" | "move" | "tap" | "press" | "pressup" | "scroll";
export declare type UISignal<E> = Signal<{
    id: string | null;
    e: E;
}, UIEventBus>;
export declare class UIEventBus implements EventListenerObject {
    readonly canvas_view: CanvasView;
    readonly pan_start: UISignal<PanEvent>;
    readonly pan: UISignal<PanEvent>;
    readonly pan_end: UISignal<PanEvent>;
    readonly pinch_start: UISignal<PinchEvent>;
    readonly pinch: UISignal<PinchEvent>;
    readonly pinch_end: UISignal<PinchEvent>;
    readonly rotate_start: UISignal<RotateEvent>;
    readonly rotate: UISignal<RotateEvent>;
    readonly rotate_end: UISignal<RotateEvent>;
    readonly tap: UISignal<TapEvent>;
    readonly doubletap: UISignal<TapEvent>;
    readonly press: UISignal<TapEvent>;
    readonly pressup: UISignal<TapEvent>;
    readonly move_enter: UISignal<MoveEvent>;
    readonly move: UISignal<MoveEvent>;
    readonly move_exit: UISignal<MoveEvent>;
    readonly scroll: UISignal<ScrollEvent>;
    readonly keydown: UISignal<KeyEvent>;
    readonly keyup: UISignal<KeyEvent>;
    private readonly hammer;
    private menu;
    get hit_area(): HTMLElement;
    constructor(canvas_view: CanvasView);
    destroy(): void;
    handleEvent(e: KeyboardEvent): void;
    protected _configure_hammerjs(): void;
    register_tool(tool_view: ToolView): void;
    private _register_tool;
    protected _hit_test_renderers(plot_view: PlotView, sx: number, sy: number): RendererView | null;
    set_cursor(cursor?: string): void;
    protected _hit_test_frame(plot_view: PlotView, sx: number, sy: number): boolean;
    protected _hit_test_canvas(plot_view: PlotView, sx: number, sy: number): boolean;
    protected _hit_test_plot(sx: number, sy: number): PlotView | null;
    protected _prev_move: {
        sx: number;
        sy: number;
        plot_view: PlotView | null;
    } | null;
    protected _curr_pan: {
        plot_view: PlotView;
    } | null;
    protected _curr_pinch: {
        plot_view: PlotView;
    } | null;
    protected _curr_rotate: {
        plot_view: PlotView;
    } | null;
    _trigger<E extends UIEvent>(signal: UISignal<E>, e: E, srcEvent: Event): void;
    __trigger<E extends UIEvent>(plot_view: PlotView, signal: UISignal<E>, e: E, srcEvent: Event): void;
    trigger<E>(signal: UISignal<E>, e: E, id?: string | null): void;
    _trigger_bokeh_event(plot_view: PlotView, e: UIEvent): void;
    _get_sxy(event: TouchEvent | MouseEvent | PointerEvent): ScreenCoord;
    _pan_event(e: HammerEvent): PanEvent;
    _pinch_event(e: HammerEvent): PinchEvent;
    _rotate_event(e: HammerEvent): RotateEvent;
    _tap_event(e: HammerEvent): TapEvent;
    _move_event(e: MouseEvent): MoveEvent;
    _scroll_event(e: WheelEvent): ScrollEvent;
    _key_event(e: KeyboardEvent): KeyEvent;
    _pan_start(e: HammerEvent): void;
    _pan(e: HammerEvent): void;
    _pan_end(e: HammerEvent): void;
    _pinch_start(e: HammerEvent): void;
    _pinch(e: HammerEvent): void;
    _pinch_end(e: HammerEvent): void;
    _rotate_start(e: HammerEvent): void;
    _rotate(e: HammerEvent): void;
    _rotate_end(e: HammerEvent): void;
    _tap(e: HammerEvent): void;
    _doubletap(e: HammerEvent): void;
    _press(e: HammerEvent): void;
    _pressup(e: HammerEvent): void;
    _mouse_enter(e: MouseEvent): void;
    _mouse_move(e: MouseEvent): void;
    _mouse_exit(e: MouseEvent): void;
    _mouse_wheel(e: WheelEvent): void;
    _context_menu(e: MouseEvent): void;
    _key_down(e: KeyboardEvent): void;
    _key_up(e: KeyboardEvent): void;
}
export {};
//# sourceMappingURL=ui_events.d.ts.map