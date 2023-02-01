var _a;
import { ActionTool, ActionToolView, ActionToolButtonView } from "./action_tool";
export class CustomActionButtonView extends ActionToolButtonView {
    css_classes() {
        return super.css_classes().concat("bk-toolbar-button-custom-action");
    }
}
CustomActionButtonView.__name__ = "CustomActionButtonView";
export class CustomActionView extends ActionToolView {
    doit() {
        this.model.callback?.execute(this.model);
    }
}
CustomActionView.__name__ = "CustomActionView";
export class CustomAction extends ActionTool {
    constructor(attrs) {
        super(attrs);
        this.tool_name = "Custom Action";
        this.button_view = CustomActionButtonView;
    }
}
_a = CustomAction;
CustomAction.__name__ = "CustomAction";
(() => {
    _a.prototype.default_view = CustomActionView;
    _a.define(({ Any, String, Nullable }) => ({
        callback: [Nullable(Any /*TODO*/)],
        icon: [String],
    }));
    _a.override({
        description: "Perform a Custom Action",
    });
})();
//# sourceMappingURL=custom_action.js.map