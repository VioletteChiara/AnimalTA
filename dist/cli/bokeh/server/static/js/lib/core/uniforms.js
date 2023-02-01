import { equals } from "./util/eq";
export class Uniform {
    is_Scalar() { return this.is_scalar; }
    is_Vector() { return !this.is_scalar; }
}
Uniform.__name__ = "Uniform";
export class UniformScalar extends Uniform {
    constructor(value, length) {
        super();
        this.value = value;
        this.length = length;
        this.is_scalar = true;
    }
    get(_i) {
        return this.value;
    }
    *[Symbol.iterator]() {
        const { length, value } = this;
        for (let i = 0; i < length; i++) {
            yield value;
        }
    }
    select(indices) {
        return new UniformScalar(this.value, indices.count);
    }
    [equals](that, cmp) {
        return cmp.eq(this.length, that.length) && cmp.eq(this.value, that.value);
    }
}
UniformScalar.__name__ = "UniformScalar";
export class UniformVector extends Uniform {
    constructor(array) {
        super();
        this.array = array;
        this.is_scalar = false;
        this.length = this.array.length;
    }
    get(i) {
        return this.array[i];
    }
    *[Symbol.iterator]() {
        yield* this.array;
    }
    select(indices) {
        const array = indices.select(this.array);
        return new this.constructor(array);
    }
    [equals](that, cmp) {
        return cmp.eq(this.length, that.length) && cmp.eq(this.array, that.array);
    }
}
UniformVector.__name__ = "UniformVector";
export class ColorUniformVector extends UniformVector {
    constructor(array) {
        super(array);
        this.array = array;
        this._view = new DataView(array.buffer);
    }
    get(i) {
        return this._view.getUint32(4 * i);
    }
    *[Symbol.iterator]() {
        const n = this.length;
        for (let i = 0; i < n; i++)
            yield this.get(i);
    }
}
ColorUniformVector.__name__ = "ColorUniformVector";
//# sourceMappingURL=uniforms.js.map