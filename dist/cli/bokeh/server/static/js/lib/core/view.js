import { Signal0, Signal } from "./signaling";
import { stylesheet } from "./dom";
import { isArray } from "./util/types";
import root_css from "../styles/root.css";
export class View {
    constructor(options) {
        this.removed = new Signal0(this, "removed");
        this._ready = Promise.resolve(undefined);
        /** @internal */
        this._slots = new WeakMap();
        this._idle_notified = false;
        const { model, parent } = options;
        this.model = model;
        this.parent = parent;
        this.root = parent == null ? this : parent.root;
        this.removed.emit();
    }
    get ready() {
        return this._ready;
    }
    connect(signal, slot) {
        let new_slot = this._slots.get(slot);
        if (new_slot == null) {
            new_slot = (args, sender) => {
                const promise = Promise.resolve(slot.call(this, args, sender));
                this._ready = this._ready.then(() => promise);
            };
            this._slots.set(slot, new_slot);
        }
        return signal.connect(new_slot, this);
    }
    disconnect(signal, slot) {
        return signal.disconnect(slot, this);
    }
    initialize() {
        this._has_finished = false;
        if (this.is_root) {
            this._stylesheet = stylesheet;
        }
        for (const style of this.styles()) {
            this.stylesheet.append(style);
        }
    }
    async lazy_initialize() { }
    remove() {
        this.disconnect_signals();
        this.removed.emit();
    }
    toString() {
        return `${this.model.type}View(${this.model.id})`;
    }
    serializable_state() {
        return { type: this.model.type };
    }
    get is_root() {
        return this.parent == null;
    }
    has_finished() {
        return this._has_finished;
    }
    get is_idle() {
        return this.has_finished();
    }
    connect_signals() { }
    disconnect_signals() {
        Signal.disconnect_receiver(this);
    }
    on_change(properties, fn) {
        for (const property of isArray(properties) ? properties : [properties]) {
            this.connect(property.change, fn);
        }
    }
    cursor(_sx, _sy) {
        return null;
    }
    get stylesheet() {
        if (this.is_root)
            return this._stylesheet;
        else
            return this.root.stylesheet;
    }
    styles() {
        return [root_css];
    }
    notify_finished() {
        if (!this.is_root)
            this.root.notify_finished();
        else {
            if (!this._idle_notified && this.has_finished()) {
                if (this.model.document != null) {
                    this._idle_notified = true;
                    this.model.document.notify_idle(this.model);
                }
            }
        }
    }
}
View.__name__ = "View";
//# sourceMappingURL=view.js.map