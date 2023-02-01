import { Signal0 } from "../../core/signaling";
export class StateManager {
    constructor(parent, initial_state) {
        this.parent = parent;
        this.initial_state = initial_state;
        this.changed = new Signal0(this.parent, "state_changed");
        this.history = [];
        this.index = -1;
    }
    _do_state_change(index) {
        const state = this.history[index] != null ? this.history[index].state : this.initial_state;
        if (state.range != null)
            this.parent.update_range(state.range);
        if (state.selection != null)
            this.parent.update_selection(state.selection);
        return state;
    }
    push(type, new_state) {
        const { history, index } = this;
        const prev_state = history[index] != null ? history[index].state : {};
        const state = { ...this.initial_state, ...prev_state, ...new_state };
        this.history = this.history.slice(0, this.index + 1);
        this.history.push({ type, state });
        this.index = this.history.length - 1;
        this.changed.emit();
    }
    clear() {
        this.history = [];
        this.index = -1;
        this.changed.emit();
    }
    undo() {
        if (this.can_undo) {
            this.index -= 1;
            const state = this._do_state_change(this.index);
            this.changed.emit();
            return state;
        }
        return null;
    }
    redo() {
        if (this.can_redo) {
            this.index += 1;
            const state = this._do_state_change(this.index);
            this.changed.emit();
            return state;
        }
        return null;
    }
    get can_undo() {
        return this.index >= 0;
    }
    get can_redo() {
        return this.index < this.history.length - 1;
    }
}
StateManager.__name__ = "StateManager";
//# sourceMappingURL=state_manager.js.map