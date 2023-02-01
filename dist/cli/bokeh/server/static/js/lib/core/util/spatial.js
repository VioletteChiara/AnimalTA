import FlatBush from "flatbush";
import { Indices } from "../types";
import { empty } from "./bbox";
function upperBound(value, arr) {
    let i = 0;
    let j = arr.length - 1;
    while (i < j) {
        const m = (i + j) >> 1;
        if (arr[m] > value) {
            j = m;
        }
        else {
            i = m + 1;
        }
    }
    return arr[i];
}
class _FlatBush extends FlatBush {
    get boxes() {
        return this._boxes;
    }
    search_indices(minX, minY, maxX, maxY) {
        if (this._pos !== this._boxes.length) {
            throw new Error("Data not yet indexed - call index.finish().");
        }
        let nodeIndex = this._boxes.length - 4;
        const queue = [];
        const results = new Indices(this.numItems);
        while (nodeIndex !== undefined) {
            // find the end index of the node
            const end = Math.min(nodeIndex + this.nodeSize * 4, upperBound(nodeIndex, this._levelBounds));
            // search through child nodes
            for (let pos = nodeIndex; pos < end; pos += 4) {
                const index = this._indices[pos >> 2] | 0;
                // check if node bbox intersects with query bbox
                const nodeMinX = this._boxes[pos + 0];
                const nodeMinY = this._boxes[pos + 1];
                const nodeMaxX = this._boxes[pos + 2];
                const nodeMaxY = this._boxes[pos + 3];
                if (maxX < nodeMinX)
                    continue;
                if (maxY < nodeMinY)
                    continue;
                if (minX > nodeMaxX)
                    continue;
                if (minY > nodeMaxY)
                    continue;
                if (nodeIndex < this.numItems * 4) {
                    results.set(index); // leaf item
                }
                else {
                    queue.push(index); // node; add it to the search queue
                }
            }
            nodeIndex = queue.pop();
        }
        return results;
    }
}
_FlatBush.__name__ = "_FlatBush";
export class SpatialIndex {
    constructor(size) {
        this.index = null;
        if (size > 0) {
            this.index = new _FlatBush(size);
        }
    }
    add_rect(x0, y0, x1, y1) {
        if (!isFinite(x0 + y0 + x1 + y1))
            this.add_empty();
        else
            this.index?.add(x0, y0, x1, y1);
    }
    add_point(x, y) {
        if (!isFinite(x + y))
            this.add_empty();
        else
            this.index?.add(x, y, x, y);
    }
    add_empty() {
        this.index?.add(Infinity, Infinity, -Infinity, -Infinity);
    }
    finish() {
        this.index?.finish();
    }
    _normalize(rect) {
        let { x0, y0, x1, y1 } = rect;
        if (x0 > x1)
            [x0, x1] = [x1, x0];
        if (y0 > y1)
            [y0, y1] = [y1, y0];
        return { x0, y0, x1, y1 };
    }
    get bbox() {
        if (this.index == null)
            return empty();
        else {
            const { minX, minY, maxX, maxY } = this.index;
            return { x0: minX, y0: minY, x1: maxX, y1: maxY };
        }
    }
    indices(rect) {
        if (this.index == null)
            return new Indices(0);
        else {
            const { x0, y0, x1, y1 } = this._normalize(rect);
            return this.index.search_indices(x0, y0, x1, y1);
        }
    }
    bounds(rect) {
        const bounds = empty();
        if (this.index == null)
            return bounds;
        const { boxes } = this.index;
        for (const i of this.indices(rect)) {
            const x0 = boxes[4 * i + 0];
            const y0 = boxes[4 * i + 1];
            const x1 = boxes[4 * i + 2];
            const y1 = boxes[4 * i + 3];
            if (x0 >= rect.x0 && x0 < bounds.x0)
                bounds.x0 = x0;
            if (x1 <= rect.x1 && x1 > bounds.x1)
                bounds.x1 = x1;
            if (y0 >= rect.y0 && y0 < bounds.y0)
                bounds.y0 = y0;
            if (y1 <= rect.y1 && y1 > bounds.y1)
                bounds.y1 = y1;
        }
        return bounds;
    }
}
SpatialIndex.__name__ = "SpatialIndex";
//# sourceMappingURL=spatial.js.map