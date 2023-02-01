var _a;
import { ActionTool, ActionToolView } from "./action_tool";
import { tool_icon_help } from "../../../styles/icons.css";
export class HelpToolView extends ActionToolView {
    doit() {
        window.open(this.model.redirect);
    }
}
HelpToolView.__name__ = "HelpToolView";
export class HelpTool extends ActionTool {
    constructor(attrs) {
        super(attrs);
        this.tool_name = "Help";
        this.icon = tool_icon_help;
    }
}
_a = HelpTool;
HelpTool.__name__ = "HelpTool";
(() => {
    _a.prototype.default_view = HelpToolView;
    _a.define(({ String }) => ({
        redirect: [String, "https://docs.bokeh.org/en/latest/docs/user_guide/tools.html"],
    }));
    _a.override({
        description: "Click the question mark to learn more about Bokeh plot tools.",
    });
    _a.register_alias("help", () => new HelpTool());
})();
//# sourceMappingURL=help_tool.js.map