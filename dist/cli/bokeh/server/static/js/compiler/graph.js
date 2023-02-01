"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.detect_cycles = void 0;
function detect_cycles(graph) {
    const cycles = [];
    const state = new Map();
    for (const node of graph.keys()) {
        state.set(node, { visited: false, explored: false });
    }
    function detect_cycle(nodes) {
        const node = nodes[0];
        const entry = state.get(node);
        if (entry.visited)
            return false;
        if (entry.explored) {
            cycles.push(nodes);
            return true;
        }
        entry.explored = true;
        const neighbors = graph.get(node);
        for (const neighbor of neighbors) {
            const { visited } = state.get(neighbor);
            if (!visited) {
                const cycle = detect_cycle([neighbor, ...nodes]);
                if (cycle)
                    break;
            }
        }
        entry.explored = false;
        entry.visited = true;
        return false;
    }
    for (const node of graph.keys()) {
        detect_cycle([node]);
    }
    return cycles;
}
exports.detect_cycles = detect_cycles;
//# sourceMappingURL=graph.js.map