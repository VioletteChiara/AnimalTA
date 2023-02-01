import { min } from "./array";
export class Matrix {
    constructor(nrows, ncols, init) {
        this.nrows = nrows;
        this.ncols = ncols;
        this._matrix = new Array(nrows);
        for (let y = 0; y < nrows; y++) {
            this._matrix[y] = new Array(ncols);
            for (let x = 0; x < ncols; x++) {
                this._matrix[y][x] = init(y, x);
            }
        }
    }
    at(row, col) {
        return this._matrix[row][col];
    }
    *[Symbol.iterator]() {
        for (let y = 0; y < this.nrows; y++) {
            for (let x = 0; x < this.ncols; x++) {
                const value = this._matrix[y][x];
                yield [value, y, x];
            }
        }
    }
    *values() {
        for (const [item] of this) {
            yield item;
        }
    }
    map(fn) {
        return new Matrix(this.nrows, this.ncols, (row, col) => fn(this.at(row, col), row, col));
    }
    apply(obj) {
        const fn = Matrix.from(obj);
        const { nrows, ncols } = this;
        if (nrows == fn.nrows && ncols == fn.ncols)
            return new Matrix(nrows, ncols, (row, col) => fn.at(row, col)(this.at(row, col), row, col));
        else
            throw new Error("dimensions don't match");
    }
    to_sparse() {
        return [...this];
    }
    static from(obj, ncols) {
        if (obj instanceof Matrix) {
            return obj;
        }
        else if (ncols != null) {
            const entries = obj;
            const nrows = Math.floor(entries.length / ncols);
            return new Matrix(nrows, ncols, (row, col) => entries[row * ncols + col]);
        }
        else {
            const arrays = obj;
            const nrows = obj.length;
            const ncols = min(arrays.map((row) => row.length));
            return new Matrix(nrows, ncols, (row, col) => arrays[row][col]);
        }
    }
}
Matrix.__name__ = "Matrix";
//# sourceMappingURL=matrix.js.map