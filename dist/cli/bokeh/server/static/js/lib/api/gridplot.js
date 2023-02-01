import { Row, Column, GridBox, ToolbarBox, ProxyToolbar, Plot } from "./models";
import { Matrix } from "../core/util/matrix";
import { unreachable } from "../core/util/assert";
function or_else(value, default_value) {
    if (value === undefined)
        return default_value;
    else
        return value;
}
export function gridplot(children, options = {}) {
    const toolbar_location = or_else(options.toolbar_location, "above");
    const merge_tools = or_else(options.merge_tools, true);
    const sizing_mode = or_else(options.sizing_mode, null);
    const matrix = Matrix.from(children);
    const items = [];
    const toolbars = [];
    for (const [item, row, col] of matrix) {
        if (item == null)
            continue;
        if (item instanceof Plot) {
            if (merge_tools) {
                toolbars.push(item.toolbar);
                item.toolbar_location = null;
            }
            if (options.plot_width != null)
                item.width = options.plot_width;
            if (options.plot_height != null)
                item.height = options.plot_height;
        }
        if (options.width != null)
            item.width = options.width;
        if (options.height != null)
            item.height = options.height;
        items.push([item, row, col]);
    }
    const grid = new GridBox({ children: items, sizing_mode });
    if (!merge_tools || toolbar_location == null)
        return grid;
    const tools = [];
    for (const toolbar of toolbars) {
        tools.push(...toolbar.tools);
    }
    const toolbar = new ToolbarBox({
        toolbar: new ProxyToolbar({ toolbars, tools }),
        toolbar_location,
    });
    switch (toolbar_location) {
        case "above":
            return new Column({ children: [toolbar, grid], sizing_mode });
        case "below":
            return new Column({ children: [grid, toolbar], sizing_mode });
        case "left":
            return new Row({ children: [toolbar, grid], sizing_mode });
        case "right":
            return new Row({ children: [grid, toolbar], sizing_mode });
        default:
            unreachable();
    }
}
//# sourceMappingURL=gridplot.js.map