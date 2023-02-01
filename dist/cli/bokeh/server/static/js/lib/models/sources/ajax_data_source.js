var _a;
import { WebDataSource } from "./web_data_source";
import { HTTPMethod } from "../../core/enums";
import { logger } from "../../core/logging";
import { entries } from "../../core/util/object";
export class AjaxDataSource extends WebDataSource {
    constructor(attrs) {
        super(attrs);
        this.interval = null;
        this.initialized = false;
    }
    destroy() {
        if (this.interval != null)
            clearInterval(this.interval);
        super.destroy();
    }
    setup() {
        if (!this.initialized) {
            this.initialized = true;
            this.get_data(this.mode);
            if (this.polling_interval != null) {
                const callback = () => this.get_data(this.mode, this.max_size, this.if_modified);
                this.interval = setInterval(callback, this.polling_interval);
            }
        }
    }
    get_data(mode, max_size = null, _if_modified = false) {
        const xhr = this.prepare_request();
        // TODO: if_modified
        xhr.addEventListener("load", () => this.do_load(xhr, mode, max_size ?? undefined));
        xhr.addEventListener("error", () => this.do_error(xhr));
        xhr.send();
    }
    prepare_request() {
        const xhr = new XMLHttpRequest();
        xhr.open(this.method, this.data_url, true);
        xhr.withCredentials = false;
        xhr.setRequestHeader("Content-Type", this.content_type);
        const http_headers = this.http_headers;
        for (const [name, value] of entries(http_headers)) {
            xhr.setRequestHeader(name, value);
        }
        return xhr;
    }
    do_load(xhr, mode, max_size) {
        if (xhr.status === 200) {
            const raw_data = JSON.parse(xhr.responseText);
            this.load_data(raw_data, mode, max_size);
        }
    }
    do_error(xhr) {
        logger.error(`Failed to fetch JSON from ${this.data_url} with code ${xhr.status}`);
    }
}
_a = AjaxDataSource;
AjaxDataSource.__name__ = "AjaxDataSource";
(() => {
    _a.define(({ Boolean, Int, String, Dict, Nullable }) => ({
        polling_interval: [Nullable(Int), null],
        content_type: [String, "application/json"],
        http_headers: [Dict(String), {}],
        method: [HTTPMethod, "POST"],
        if_modified: [Boolean, false],
    }));
})();
//# sourceMappingURL=ajax_data_source.js.map