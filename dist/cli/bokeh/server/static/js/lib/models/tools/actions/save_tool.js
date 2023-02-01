var _a;
import { ActionTool, ActionToolView } from "./action_tool";
import { tool_icon_save } from "../../../styles/icons.css";
export class SaveToolView extends ActionToolView {
    async copy() {
        const blob = await this.plot_view.to_blob();
        const item = new ClipboardItem({ [blob.type]: Promise.resolve(blob) });
        await navigator.clipboard.write([item]);
    }
    async save(name) {
        const blob = await this.plot_view.to_blob();
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = name; // + ".png" | "svg" (inferred from MIME type)
        link.target = "_blank";
        link.dispatchEvent(new MouseEvent("click"));
    }
    doit(action = "save") {
        switch (action) {
            case "save":
                this.save("bokeh_plot");
                break;
            case "copy":
                this.copy();
                break;
        }
    }
}
SaveToolView.__name__ = "SaveToolView";
export class SaveTool extends ActionTool {
    constructor(attrs) {
        super(attrs);
        this.tool_name = "Save";
        this.icon = tool_icon_save;
    }
    get menu() {
        return [
            {
                icon: "bk-tool-icon-copy-to-clipboard",
                tooltip: "Copy image to clipboard",
                if: () => typeof ClipboardItem !== "undefined",
                handler: () => {
                    this.do.emit("copy");
                },
            },
        ];
    }
}
_a = SaveTool;
SaveTool.__name__ = "SaveTool";
(() => {
    _a.prototype.default_view = SaveToolView;
    _a.register_alias("save", () => new SaveTool());
})();
//# sourceMappingURL=save_tool.js.map