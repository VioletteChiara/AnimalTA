var _a;
import { Callback } from "./callback";
import { replace_placeholders } from "../../core/util/templating";
import { isString } from "../../core/util/types";
export class OpenURL extends Callback {
    constructor(attrs) {
        super(attrs);
    }
    navigate(url) {
        if (this.same_tab)
            window.location.href = url;
        else
            window.open(url);
    }
    execute(_cb_obj, { source }) {
        const open_url = (i) => {
            const url = replace_placeholders(this.url, source, i, undefined, undefined, encodeURI);
            if (!isString(url))
                throw new Error("HTML output is not supported in this context");
            this.navigate(url);
        };
        const { selected } = source;
        for (const i of selected.indices)
            open_url(i);
        for (const i of selected.line_indices)
            open_url(i);
        // TODO: multiline_indices: {[key: string]: number[]}
    }
}
_a = OpenURL;
OpenURL.__name__ = "OpenURL";
(() => {
    _a.define(({ Boolean, String }) => ({
        url: [String, "http://"],
        same_tab: [Boolean, false],
    }));
})();
//# sourceMappingURL=open_url.js.map