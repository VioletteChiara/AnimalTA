var _a;
import { ActionTool, ActionToolView } from "./action_tool";
import { tool_icon_undo } from "../../../styles/icons.css";
export class UndoToolView extends ActionToolView {
    connect_signals() {
        super.connect_signals();
        this.connect(this.plot_view.state.changed, () => this.model.disabled = !this.plot_view.state.can_undo);
    }
    doit() {
        const state = this.plot_view.state.undo();
        if (state?.range != null) {
            this.plot_view.trigger_ranges_update_event();
        }
    }
}
UndoToolView.__name__ = "UndoToolView";
export class UndoTool extends ActionTool {
    constructor(attrs) {
        super(attrs);
        this.tool_name = "Undo";
        this.icon = tool_icon_undo;
    }
}
_a = UndoTool;
UndoTool.__name__ = "UndoTool";
(() => {
    _a.prototype.default_view = UndoToolView;
    _a.override({
        disabled: true,
    });
    _a.register_alias("undo", () => new UndoTool());
})();
//# sourceMappingURL=undo_tool.js.map