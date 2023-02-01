import { Signal0 } from "../../core/signaling";
import type { PlotView } from "./plot_canvas";
import type { RangeInfo } from "./range_manager";
import { Selection } from "../selections/selection";
import type { DataRenderer } from "../renderers/data_renderer";
export declare type StateInfo = {
    range?: RangeInfo;
    selection: Map<DataRenderer, Selection>;
    dimensions: {
        width: number;
        height: number;
    };
};
export declare class StateManager {
    readonly parent: PlotView;
    readonly initial_state: StateInfo;
    constructor(parent: PlotView, initial_state: StateInfo);
    readonly changed: Signal0<this["parent"]>;
    protected history: {
        type: string;
        state: StateInfo;
    }[];
    protected index: number;
    protected _do_state_change(index: number): StateInfo;
    push(type: string, new_state: Partial<StateInfo>): void;
    clear(): void;
    undo(): StateInfo | null;
    redo(): StateInfo | null;
    get can_undo(): boolean;
    get can_redo(): boolean;
}
//# sourceMappingURL=state_manager.d.ts.map