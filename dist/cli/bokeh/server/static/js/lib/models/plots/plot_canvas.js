import { CartesianFrame } from "../canvas/cartesian_frame";
import { Canvas } from "../canvas/canvas";
import { LayoutDOMView } from "../layouts/layout_dom";
import { Annotation, AnnotationView } from "../annotations/annotation";
import { Title } from "../annotations/title";
import { AxisView } from "../axes/axis";
import { ToolbarPanel } from "../annotations/toolbar_panel";
import { Reset } from "../../core/bokeh_events";
import { build_view, build_views, remove_views } from "../../core/build_views";
import { Visuals } from "../../core/visuals";
import { logger } from "../../core/logging";
import { RangesUpdate } from "../../core/bokeh_events";
import { throttle } from "../../core/util/throttle";
import { isArray } from "../../core/util/types";
import { copy, reversed } from "../../core/util/array";
import { CanvasLayer } from "../../core/util/canvas";
import { HStack, VStack, NodeLayout } from "../../core/layout/alignments";
import { BorderLayout } from "../../core/layout/border";
import { Row, Column } from "../../core/layout/grid";
import { Panel } from "../../core/layout/side_panel";
import { BBox } from "../../core/util/bbox";
import { RangeManager } from "./range_manager";
import { StateManager } from "./state_manager";
import { settings } from "../../core/settings";
export class PlotView extends LayoutDOMView {
    constructor() {
        super(...arguments);
        this._outer_bbox = new BBox();
        this._inner_bbox = new BBox();
        this._needs_paint = true;
        this._needs_layout = false;
        this._invalidated_painters = new Set();
        this._invalidate_all = true;
        this._needs_notify = false;
    }
    get canvas() {
        return this.canvas_view;
    }
    get state() {
        return this._state_manager;
    }
    set invalidate_dataranges(value) {
        this._range_manager.invalidate_dataranges = value;
    }
    renderer_view(renderer) {
        const view = this.renderer_views.get(renderer);
        if (view == null) {
            for (const [, renderer_view] of this.renderer_views) {
                const view = renderer_view.renderer_view(renderer);
                if (view != null)
                    return view;
            }
        }
        return view;
    }
    get is_paused() {
        return this._is_paused != null && this._is_paused !== 0;
    }
    get child_models() {
        return [];
    }
    pause() {
        if (this._is_paused == null)
            this._is_paused = 1;
        else
            this._is_paused += 1;
    }
    unpause(no_render = false) {
        if (this._is_paused == null)
            throw new Error("wasn't paused");
        this._is_paused -= 1;
        if (this._is_paused == 0 && !no_render)
            this.request_paint("everything");
    }
    notify_finished_after_paint() {
        this._needs_notify = true;
    }
    // TODO: this needs to be removed
    request_render() {
        this.request_paint("everything");
    }
    request_paint(to_invalidate) {
        this.invalidate_painters(to_invalidate);
        this.schedule_paint();
    }
    invalidate_painters(to_invalidate) {
        if (to_invalidate == "everything")
            this._invalidate_all = true;
        else if (isArray(to_invalidate)) {
            for (const renderer_view of to_invalidate)
                this._invalidated_painters.add(renderer_view);
        }
        else
            this._invalidated_painters.add(to_invalidate);
    }
    schedule_paint() {
        if (!this.is_paused) {
            const promise = this.throttled_paint();
            this._ready = this._ready.then(() => promise);
        }
    }
    request_layout() {
        this._needs_layout = true;
        this.request_paint("everything");
    }
    reset() {
        if (this.model.reset_policy == "standard") {
            this.state.clear();
            this.reset_range();
            this.reset_selection();
        }
        this.model.trigger_event(new Reset());
    }
    remove() {
        remove_views(this.renderer_views);
        remove_views(this.tool_views);
        this.canvas_view.remove();
        super.remove();
    }
    render() {
        super.render();
        this.el.appendChild(this.canvas_view.el);
        this.canvas_view.render();
    }
    initialize() {
        this.pause();
        super.initialize();
        this.lod_started = false;
        this.visuals = new Visuals(this);
        this._initial_state = {
            selection: new Map(),
            dimensions: { width: 0, height: 0 }, // XXX: initial dimensions
        };
        this.visibility_callbacks = [];
        this.renderer_views = new Map();
        this.tool_views = new Map();
        this.frame = new CartesianFrame(this.model.x_scale, this.model.y_scale, this.model.x_range, this.model.y_range, this.model.extra_x_ranges, this.model.extra_y_ranges, this.model.extra_x_scales, this.model.extra_y_scales);
        this._range_manager = new RangeManager(this);
        this._state_manager = new StateManager(this, this._initial_state);
        this.throttled_paint = throttle(() => this.repaint(), 1000 / 60);
        const { title_location, title } = this.model;
        if (title_location != null && title != null) {
            this._title = title instanceof Title ? title : new Title({ text: title });
        }
        const { toolbar_location, toolbar } = this.model;
        if (toolbar_location != null && toolbar != null) {
            this._toolbar = new ToolbarPanel({ toolbar });
            toolbar.toolbar_location = toolbar_location;
        }
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        const { hidpi, output_backend } = this.model;
        const canvas = new Canvas({ hidpi, output_backend });
        this.canvas_view = await build_view(canvas, { parent: this });
        this.canvas_view.plot_views = [this];
        await this.build_renderer_views();
        await this.build_tool_views();
        this._range_manager.update_dataranges();
        this.unpause(true);
        logger.debug("PlotView initialized");
    }
    _width_policy() {
        return this.model.frame_width == null ? super._width_policy() : "min";
    }
    _height_policy() {
        return this.model.frame_height == null ? super._height_policy() : "min";
    }
    _update_layout() {
        this.layout = new BorderLayout();
        this.layout.set_sizing(this.box_sizing());
        const above = copy(this.model.above);
        const below = copy(this.model.below);
        const left = copy(this.model.left);
        const right = copy(this.model.right);
        const get_side = (side) => {
            switch (side) {
                case "above": return above;
                case "below": return below;
                case "left": return left;
                case "right": return right;
            }
        };
        const { title_location, title } = this.model;
        if (title_location != null && title != null) {
            get_side(title_location).push(this._title);
        }
        const { toolbar_location, toolbar } = this.model;
        if (toolbar_location != null && toolbar != null) {
            const panels = get_side(toolbar_location);
            let push_toolbar = true;
            if (this.model.toolbar_sticky) {
                for (let i = 0; i < panels.length; i++) {
                    const panel = panels[i];
                    if (panel instanceof Title) {
                        if (toolbar_location == "above" || toolbar_location == "below")
                            panels[i] = [panel, this._toolbar];
                        else
                            panels[i] = [this._toolbar, panel];
                        push_toolbar = false;
                        break;
                    }
                }
            }
            if (push_toolbar)
                panels.push(this._toolbar);
        }
        const set_layout = (side, model) => {
            const view = this.renderer_view(model);
            view.panel = new Panel(side);
            view.update_layout?.();
            return view.layout;
        };
        const set_layouts = (side, panels) => {
            const horizontal = side == "above" || side == "below";
            const layouts = [];
            for (const panel of panels) {
                if (isArray(panel)) {
                    const items = panel.map((subpanel) => {
                        const item = set_layout(side, subpanel);
                        if (subpanel instanceof ToolbarPanel) {
                            const dim = horizontal ? "width_policy" : "height_policy";
                            item.set_sizing({ ...item.sizing, [dim]: "min" });
                        }
                        return item;
                    });
                    let layout;
                    if (horizontal) {
                        layout = new Row(items);
                        layout.set_sizing({ width_policy: "max", height_policy: "min" });
                    }
                    else {
                        layout = new Column(items);
                        layout.set_sizing({ width_policy: "min", height_policy: "max" });
                    }
                    layout.absolute = true;
                    layouts.push(layout);
                }
                else
                    layouts.push(set_layout(side, panel));
            }
            return layouts;
        };
        const min_border = this.model.min_border ?? 0;
        this.layout.min_border = {
            left: this.model.min_border_left ?? min_border,
            top: this.model.min_border_top ?? min_border,
            right: this.model.min_border_right ?? min_border,
            bottom: this.model.min_border_bottom ?? min_border,
        };
        const center_panel = new NodeLayout();
        const top_panel = new VStack();
        const bottom_panel = new VStack();
        const left_panel = new HStack();
        const right_panel = new HStack();
        center_panel.absolute = true;
        top_panel.absolute = true;
        bottom_panel.absolute = true;
        left_panel.absolute = true;
        right_panel.absolute = true;
        center_panel.children =
            this.model.center.filter((obj) => {
                return obj instanceof Annotation;
            }).map((model) => {
                const view = this.renderer_view(model);
                view.update_layout?.();
                return view.layout;
            }).filter((layout) => {
                return layout != null;
            });
        const { frame_width, frame_height } = this.model;
        center_panel.set_sizing({
            ...(frame_width != null ? { width_policy: "fixed", width: frame_width } : { width_policy: "fit" }),
            ...(frame_height != null ? { height_policy: "fixed", height: frame_height } : { height_policy: "fit" }),
        });
        center_panel.on_resize((bbox) => this.frame.set_geometry(bbox));
        top_panel.children = reversed(set_layouts("above", above));
        bottom_panel.children = set_layouts("below", below);
        left_panel.children = reversed(set_layouts("left", left));
        right_panel.children = set_layouts("right", right);
        top_panel.set_sizing({ width_policy: "fit", height_policy: "min" /*, min_height: this.layout.min_border.top*/ });
        bottom_panel.set_sizing({ width_policy: "fit", height_policy: "min" /*, min_height: this.layout.min_width.bottom*/ });
        left_panel.set_sizing({ width_policy: "min", height_policy: "fit" /*, min_width: this.layout.min_width.left*/ });
        right_panel.set_sizing({ width_policy: "min", height_policy: "fit" /*, min_width: this.layout.min_width.right*/ });
        this.layout.center_panel = center_panel;
        this.layout.top_panel = top_panel;
        this.layout.bottom_panel = bottom_panel;
        this.layout.left_panel = left_panel;
        this.layout.right_panel = right_panel;
    }
    get axis_views() {
        const views = [];
        for (const [, renderer_view] of this.renderer_views) {
            if (renderer_view instanceof AxisView)
                views.push(renderer_view);
        }
        return views;
    }
    set_toolbar_visibility(visible) {
        for (const callback of this.visibility_callbacks)
            callback(visible);
    }
    update_range(range_info, options) {
        this.pause();
        this._range_manager.update(range_info, options);
        this.unpause();
    }
    reset_range() {
        this.update_range(null);
        this.trigger_ranges_update_event();
    }
    trigger_ranges_update_event() {
        const { x_range, y_range } = this.model;
        this.model.trigger_event(new RangesUpdate(x_range.start, x_range.end, y_range.start, y_range.end));
    }
    get_selection() {
        const selection = new Map();
        for (const renderer of this.model.data_renderers) {
            const { selected } = renderer.selection_manager.source;
            selection.set(renderer, selected);
        }
        return selection;
    }
    update_selection(selections) {
        for (const renderer of this.model.data_renderers) {
            const ds = renderer.selection_manager.source;
            if (selections != null) {
                const selection = selections.get(renderer);
                if (selection != null) {
                    ds.selected.update(selection, true);
                }
            }
            else
                ds.selection_manager.clear();
        }
    }
    reset_selection() {
        this.update_selection(null);
    }
    _invalidate_layout() {
        const needs_layout = () => {
            for (const panel of this.model.side_panels) {
                const view = this.renderer_views.get(panel);
                if (view.layout?.has_size_changed()) {
                    this.invalidate_painters(view);
                    return true;
                }
            }
            return false;
        };
        if (needs_layout())
            this.root.compute_layout();
    }
    get_renderer_views() {
        return this.computed_renderers.map((r) => this.renderer_views.get(r));
    }
    *_compute_renderers() {
        const { above, below, left, right, center, renderers } = this.model;
        yield* renderers;
        yield* above;
        yield* below;
        yield* left;
        yield* right;
        yield* center;
        if (this._title != null)
            yield this._title;
        if (this._toolbar != null)
            yield this._toolbar;
        for (const tool of this.model.toolbar.tools) {
            if (tool.overlay != null)
                yield tool.overlay;
            yield* tool.synthetic_renderers;
        }
    }
    async build_renderer_views() {
        this.computed_renderers = [...this._compute_renderers()];
        await build_views(this.renderer_views, this.computed_renderers, { parent: this });
    }
    async build_tool_views() {
        const tool_models = this.model.toolbar.tools;
        const new_tool_views = await build_views(this.tool_views, tool_models, { parent: this });
        new_tool_views.map((tool_view) => this.canvas_view.ui_event_bus.register_tool(tool_view));
    }
    connect_signals() {
        super.connect_signals();
        const { x_ranges, y_ranges } = this.frame;
        for (const [, range] of x_ranges) {
            this.connect(range.change, () => { this._needs_layout = true; this.request_paint("everything"); });
        }
        for (const [, range] of y_ranges) {
            this.connect(range.change, () => { this._needs_layout = true; this.request_paint("everything"); });
        }
        const { above, below, left, right, center, renderers } = this.model.properties;
        this.on_change([above, below, left, right, center, renderers], async () => await this.build_renderer_views());
        this.connect(this.model.toolbar.properties.tools.change, async () => {
            await this.build_renderer_views();
            await this.build_tool_views();
        });
        this.connect(this.model.change, () => this.request_paint("everything"));
        this.connect(this.model.reset, () => this.reset());
    }
    has_finished() {
        if (!super.has_finished())
            return false;
        if (this.model.visible) {
            for (const [, renderer_view] of this.renderer_views) {
                if (!renderer_view.has_finished())
                    return false;
            }
        }
        return true;
    }
    after_layout() {
        super.after_layout();
        for (const [, child_view] of this.renderer_views) {
            if (child_view instanceof AnnotationView)
                child_view.after_layout?.();
        }
        this._needs_layout = false;
        this.model.setv({
            inner_width: Math.round(this.frame.bbox.width),
            inner_height: Math.round(this.frame.bbox.height),
            outer_width: Math.round(this.layout.bbox.width),
            outer_height: Math.round(this.layout.bbox.height),
        }, { no_change: true });
        if (this.model.match_aspect !== false) {
            this.pause();
            this._range_manager.update_dataranges();
            this.unpause(true);
        }
        if (!this._outer_bbox.equals(this.layout.bbox)) {
            const { width, height } = this.layout.bbox;
            this.canvas_view.resize(width, height);
            this._outer_bbox = this.layout.bbox;
            this._invalidate_all = true;
            this._needs_paint = true;
        }
        const { inner_bbox } = this.layout;
        if (!this._inner_bbox.equals(inner_bbox)) {
            this._inner_bbox = inner_bbox;
            this._needs_paint = true;
        }
        if (this._needs_paint) {
            // XXX: can't be this.request_paint(), because it would trigger back-and-forth
            // layout recomputing feedback loop between plots. Plots are also much more
            // responsive this way, especially in interactive mode.
            this.paint();
        }
    }
    repaint() {
        if (this._needs_layout)
            this._invalidate_layout();
        this.paint();
    }
    paint() {
        if (this.is_paused)
            return;
        if (this.model.visible) {
            logger.trace(`${this.toString()}.paint()`);
            this._actual_paint();
        }
        if (this._needs_notify) {
            this._needs_notify = false;
            this.notify_finished();
        }
    }
    _actual_paint() {
        const { document } = this.model;
        if (document != null) {
            const interactive_duration = document.interactive_duration();
            if (interactive_duration >= 0 && interactive_duration < this.model.lod_interval) {
                setTimeout(() => {
                    if (document.interactive_duration() > this.model.lod_timeout) {
                        document.interactive_stop();
                    }
                    this.request_paint("everything"); // TODO: this.schedule_paint()
                }, this.model.lod_timeout);
            }
            else
                document.interactive_stop();
        }
        if (this._range_manager.invalidate_dataranges) {
            this._range_manager.update_dataranges();
            this._invalidate_layout();
        }
        let do_primary = false;
        let do_overlays = false;
        if (this._invalidate_all) {
            do_primary = true;
            do_overlays = true;
        }
        else {
            for (const painter of this._invalidated_painters) {
                const { level } = painter.model;
                if (level != "overlay")
                    do_primary = true;
                else
                    do_overlays = true;
                if (do_primary && do_overlays)
                    break;
            }
        }
        this._invalidated_painters.clear();
        this._invalidate_all = false;
        const frame_box = [
            this.frame.bbox.left,
            this.frame.bbox.top,
            this.frame.bbox.width,
            this.frame.bbox.height,
        ];
        const { primary, overlays } = this.canvas_view;
        if (do_primary) {
            primary.prepare();
            this.canvas_view.prepare_webgl(frame_box);
            this._map_hook(primary.ctx, frame_box);
            this._paint_empty(primary.ctx, frame_box);
            this._paint_outline(primary.ctx, frame_box);
            this._paint_levels(primary.ctx, "image", frame_box, true);
            this._paint_levels(primary.ctx, "underlay", frame_box, true);
            this._paint_levels(primary.ctx, "glyph", frame_box, true);
            this._paint_levels(primary.ctx, "guide", frame_box, false);
            this._paint_levels(primary.ctx, "annotation", frame_box, false);
            primary.finish();
        }
        if (do_overlays || settings.wireframe) {
            overlays.prepare();
            this._paint_levels(overlays.ctx, "overlay", frame_box, false);
            if (settings.wireframe)
                this._paint_layout(overlays.ctx, this.layout);
            overlays.finish();
        }
        if (this._initial_state.range == null) {
            this._initial_state.range = this._range_manager.compute_initial() ?? undefined;
        }
        this._needs_paint = false;
    }
    _paint_levels(ctx, level, clip_region, global_clip) {
        for (const renderer of this.computed_renderers) {
            if (renderer.level != level)
                continue;
            const renderer_view = this.renderer_views.get(renderer);
            ctx.save();
            if (global_clip || renderer_view.needs_clip) {
                ctx.beginPath();
                ctx.rect(...clip_region);
                ctx.clip();
            }
            renderer_view.render();
            ctx.restore();
            if (renderer_view.has_webgl && renderer_view.needs_webgl_blit) {
                this.canvas_view.blit_webgl(ctx);
            }
        }
    }
    _paint_layout(ctx, layout) {
        const { x, y, width, height } = layout.bbox;
        ctx.strokeStyle = "blue";
        ctx.strokeRect(x, y, width, height);
        for (const child of layout) {
            ctx.save();
            if (!layout.absolute)
                ctx.translate(x, y);
            this._paint_layout(ctx, child);
            ctx.restore();
        }
    }
    _map_hook(_ctx, _frame_box) { }
    _paint_empty(ctx, frame_box) {
        const [cx, cy, cw, ch] = [0, 0, this.layout.bbox.width, this.layout.bbox.height];
        const [fx, fy, fw, fh] = frame_box;
        if (this.visuals.border_fill.doit) {
            this.visuals.border_fill.set_value(ctx);
            ctx.fillRect(cx, cy, cw, ch);
            ctx.clearRect(fx, fy, fw, fh);
        }
        if (this.visuals.background_fill.doit) {
            this.visuals.background_fill.set_value(ctx);
            ctx.fillRect(fx, fy, fw, fh);
        }
    }
    _paint_outline(ctx, frame_box) {
        if (this.visuals.outline_line.doit) {
            ctx.save();
            this.visuals.outline_line.set_value(ctx);
            let [x0, y0, w, h] = frame_box;
            // XXX: shrink outline region by 1px to make right and bottom lines visible
            // if they are on the edge of the canvas.
            if (x0 + w == this.layout.bbox.width) {
                w -= 1;
            }
            if (y0 + h == this.layout.bbox.height) {
                h -= 1;
            }
            ctx.strokeRect(x0, y0, w, h);
            ctx.restore();
        }
    }
    to_blob() {
        return this.canvas_view.to_blob();
    }
    export(type, hidpi = true) {
        const output_backend = type == "png" ? "canvas" : "svg";
        const composite = new CanvasLayer(output_backend, hidpi);
        const { width, height } = this.layout.bbox;
        composite.resize(width, height);
        const { canvas } = this.canvas_view.compose();
        composite.ctx.drawImage(canvas, 0, 0);
        return composite;
    }
    serializable_state() {
        const { children, ...state } = super.serializable_state();
        const renderers = this.get_renderer_views()
            .map((view) => view.serializable_state())
            .filter((item) => item.bbox != null);
        return { ...state, children: [...children ?? [], ...renderers] };
    }
}
PlotView.__name__ = "PlotView";
//# sourceMappingURL=plot_canvas.js.map