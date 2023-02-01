import { Model } from "../../model";
export class Expression extends Model {
    constructor(attrs) {
        super(attrs);
    }
    initialize() {
        super.initialize();
        this._result = new Map();
    }
    v_compute(source) {
        let result = this._result.get(source);
        if (result === undefined || source.changed_for(this)) {
            result = this._v_compute(source);
            this._result.set(source, result);
        }
        return result;
    }
}
Expression.__name__ = "Expression";
export class ScalarExpression extends Model {
    constructor(attrs) {
        super(attrs);
    }
    initialize() {
        super.initialize();
        this._result = new Map();
    }
    compute(source) {
        let result = this._result.get(source);
        if (result === undefined || source.changed_for(this)) {
            result = this._compute(source);
            this._result.set(source, result);
        }
        return result;
    }
}
ScalarExpression.__name__ = "ScalarExpression";
//# sourceMappingURL=expression.js.map