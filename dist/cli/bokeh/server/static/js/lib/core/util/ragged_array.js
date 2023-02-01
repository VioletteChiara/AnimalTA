var _a;
import { equals } from "./eq";
import { assert } from "./assert";
export class RaggedArray {
    constructor(offsets, array) {
        this.offsets = offsets;
        this.array = array;
    }
    [(_a = Symbol.toStringTag, equals)](that, cmp) {
        return cmp.arrays(this.offsets, that.offsets) && cmp.arrays(this.array, that.array);
    }
    get length() {
        return this.offsets.length;
    }
    clone() {
        return new RaggedArray(this.offsets.slice(), this.array.slice());
    }
    static from(items, ctor) {
        const n = items.length;
        let offset = 0;
        const offsets = (() => {
            const offsets = new Uint32Array(n);
            for (let i = 0; i < n; i++) {
                const length = items[i].length;
                offsets[i] = offset;
                offset += length;
            }
            if (offset < 256)
                return new Uint8Array(offsets);
            else if (offset < 65536)
                return new Uint16Array(offsets);
            else
                return offsets;
        })();
        const array = new ctor(offset);
        for (let i = 0; i < n; i++) {
            array.set(items[i], offsets[i]);
        }
        return new RaggedArray(offsets, array);
    }
    *[Symbol.iterator]() {
        const { offsets, length } = this;
        for (let i = 0; i < length; i++) {
            yield this.array.subarray(offsets[i], offsets[i + 1]);
        }
    }
    _check_bounds(i) {
        assert(0 <= i && i < this.length, `Out of bounds: 0 <= ${i} < ${this.length}`);
    }
    get(i) {
        this._check_bounds(i);
        const { offsets } = this;
        return this.array.subarray(offsets[i], offsets[i + 1]);
    }
    set(i, array) {
        this._check_bounds(i);
        this.array.set(array, this.offsets[i]);
    }
}
RaggedArray.__name__ = "RaggedArray";
RaggedArray[_a] = "RaggedArray";
//# sourceMappingURL=ragged_array.js.map