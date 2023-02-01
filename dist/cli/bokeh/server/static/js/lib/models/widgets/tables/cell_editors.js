var _a, _b, _c, _d, _e, _f, _g, _h, _j;
import { input, textarea, select, option, Keys } from "../../../core/dom";
import { DOMView } from "../../../core/dom_view";
import { Model } from "../../../model";
import { DTINDEX_NAME } from "./definitions";
import * as tables from "../../../styles/widgets/tables.css";
export class CellEditorView extends DOMView {
    constructor(options) {
        const { model, parent } = options.column;
        super({ model, parent, ...options });
        this.args = options;
        this.initialize(); // XXX: no build_views()
        this.render(); // XXX: this isn't governed by layout
    }
    get emptyValue() {
        return null;
    }
    initialize() {
        super.initialize();
        this.inputEl = this._createInput();
        this.defaultValue = null;
    }
    async lazy_initialize() {
        throw new Error("unsupported");
    }
    css_classes() {
        return super.css_classes().concat(tables.cell_editor);
    }
    render() {
        super.render();
        this.args.container.append(this.el);
        this.el.appendChild(this.inputEl);
        this.renderEditor();
        this.disableNavigation();
    }
    renderEditor() { }
    disableNavigation() {
        // XXX: without cast `event` is of non-specific type `Event`
        this.inputEl.addEventListener("keydown", (event) => {
            switch (event.keyCode) {
                case Keys.Left:
                case Keys.Right:
                case Keys.Up:
                case Keys.Down:
                case Keys.PageUp:
                case Keys.PageDown:
                    event.stopImmediatePropagation();
            }
        });
    }
    destroy() {
        this.remove();
    }
    focus() {
        this.inputEl.focus();
    }
    show() { }
    hide() { }
    position() { }
    getValue() {
        return this.inputEl.value;
    }
    setValue(val) {
        this.inputEl.value = val;
    }
    serializeValue() {
        return this.getValue();
    }
    isValueChanged() {
        return !(this.getValue() == "" && this.defaultValue == null) && this.getValue() !== this.defaultValue;
    }
    applyValue(item, state) {
        const grid_data = this.args.grid.getData();
        const offset = grid_data.index.indexOf(item[DTINDEX_NAME]);
        grid_data.setField(offset, this.args.column.field, state);
    }
    loadValue(item) {
        const value = item[this.args.column.field];
        this.defaultValue = value != null ? value : this.emptyValue;
        this.setValue(this.defaultValue);
    }
    validateValue(value) {
        if (this.args.column.validator) {
            const result = this.args.column.validator(value);
            if (!result.valid) {
                return result;
            }
        }
        return { valid: true, msg: null };
    }
    validate() {
        return this.validateValue(this.getValue());
    }
}
CellEditorView.__name__ = "CellEditorView";
export class CellEditor extends Model {
}
CellEditor.__name__ = "CellEditor";
export class StringEditorView extends CellEditorView {
    get emptyValue() {
        return "";
    }
    _createInput() {
        return input({ type: "text" });
    }
    renderEditor() {
        //completions = @model.completions
        //if completions.length != 0
        //  @inputEl.classList.add("bk-cell-editor-completion")
        //  $(@inputEl).autocomplete({source: completions})
        //  $(@inputEl).autocomplete("widget")
        this.inputEl.focus();
        this.inputEl.select();
    }
    loadValue(item) {
        super.loadValue(item);
        this.inputEl.defaultValue = this.defaultValue;
        this.inputEl.select();
    }
}
StringEditorView.__name__ = "StringEditorView";
export class StringEditor extends CellEditor {
}
_a = StringEditor;
StringEditor.__name__ = "StringEditor";
(() => {
    _a.prototype.default_view = StringEditorView;
    _a.define(({ String, Array }) => ({
        completions: [Array(String), []],
    }));
})();
export class TextEditorView extends CellEditorView {
    _createInput() {
        return textarea();
    }
    renderEditor() {
        this.inputEl.focus();
        this.inputEl.select();
    }
}
TextEditorView.__name__ = "TextEditorView";
export class TextEditor extends CellEditor {
}
_b = TextEditor;
TextEditor.__name__ = "TextEditor";
(() => {
    _b.prototype.default_view = TextEditorView;
})();
export class SelectEditorView extends CellEditorView {
    _createInput() {
        return select();
    }
    renderEditor() {
        for (const opt of this.model.options) {
            this.inputEl.appendChild(option({ value: opt }, opt));
        }
        this.focus();
    }
}
SelectEditorView.__name__ = "SelectEditorView";
export class SelectEditor extends CellEditor {
}
_c = SelectEditor;
SelectEditor.__name__ = "SelectEditor";
(() => {
    _c.prototype.default_view = SelectEditorView;
    _c.define(({ String, Array }) => ({
        options: [Array(String), []],
    }));
})();
export class PercentEditorView extends CellEditorView {
    _createInput() {
        return input({ type: "text" });
    }
}
PercentEditorView.__name__ = "PercentEditorView";
export class PercentEditor extends CellEditor {
}
_d = PercentEditor;
PercentEditor.__name__ = "PercentEditor";
(() => {
    _d.prototype.default_view = PercentEditorView;
})();
export class CheckboxEditorView extends CellEditorView {
    _createInput() {
        return input({ type: "checkbox" });
    }
    renderEditor() {
        this.focus();
    }
    loadValue(item) {
        this.defaultValue = !!item[this.args.column.field];
        this.inputEl.checked = this.defaultValue;
    }
    serializeValue() {
        return this.inputEl.checked;
    }
}
CheckboxEditorView.__name__ = "CheckboxEditorView";
export class CheckboxEditor extends CellEditor {
}
_e = CheckboxEditor;
CheckboxEditor.__name__ = "CheckboxEditor";
(() => {
    _e.prototype.default_view = CheckboxEditorView;
})();
export class IntEditorView extends CellEditorView {
    _createInput() {
        return input({ type: "text" });
    }
    renderEditor() {
        //$(@inputEl).spinner({step: @model.step})
        this.inputEl.focus();
        this.inputEl.select();
    }
    remove() {
        //$(@inputEl).spinner("destroy")
        super.remove();
    }
    serializeValue() {
        return parseInt(this.getValue(), 10) ?? 0;
    }
    loadValue(item) {
        super.loadValue(item);
        this.inputEl.defaultValue = this.defaultValue;
        this.inputEl.select();
    }
    validateValue(value) {
        if (isNaN(value))
            return { valid: false, msg: "Please enter a valid integer" };
        else
            return super.validateValue(value);
    }
}
IntEditorView.__name__ = "IntEditorView";
export class IntEditor extends CellEditor {
}
_f = IntEditor;
IntEditor.__name__ = "IntEditor";
(() => {
    _f.prototype.default_view = IntEditorView;
    _f.define(({ Int }) => ({
        step: [Int, 1],
    }));
})();
export class NumberEditorView extends CellEditorView {
    _createInput() {
        return input({ type: "text" });
    }
    renderEditor() {
        //$(@inputEl).spinner({step: @model.step})
        this.inputEl.focus();
        this.inputEl.select();
    }
    remove() {
        //$(@inputEl).spinner("destroy")
        super.remove();
    }
    serializeValue() {
        return parseFloat(this.getValue()) ?? 0.0;
    }
    loadValue(item) {
        super.loadValue(item);
        this.inputEl.defaultValue = this.defaultValue;
        this.inputEl.select();
    }
    validateValue(value) {
        if (isNaN(value))
            return { valid: false, msg: "Please enter a valid number" };
        else
            return super.validateValue(value);
    }
}
NumberEditorView.__name__ = "NumberEditorView";
export class NumberEditor extends CellEditor {
}
_g = NumberEditor;
NumberEditor.__name__ = "NumberEditor";
(() => {
    _g.prototype.default_view = NumberEditorView;
    _g.define(({ Number }) => ({
        step: [Number, 0.01],
    }));
})();
export class TimeEditorView extends CellEditorView {
    _createInput() {
        return input({ type: "text" });
    }
}
TimeEditorView.__name__ = "TimeEditorView";
export class TimeEditor extends CellEditor {
}
_h = TimeEditor;
TimeEditor.__name__ = "TimeEditor";
(() => {
    _h.prototype.default_view = TimeEditorView;
})();
export class DateEditorView extends CellEditorView {
    _createInput() {
        return input({ type: "text" });
    }
    get emptyValue() {
        return new Date();
    }
    renderEditor() {
        //this.calendarOpen = false
        //@$datepicker = $(@inputEl).datepicker({
        //  showOn: "button"
        //  buttonImageOnly: true
        //  beforeShow: () => @calendarOpen = true
        //  onClose: () => @calendarOpen = false
        //})
        //@$datepicker.siblings(".ui-datepicker-trigger").css("vertical-align": "middle")
        //@$datepicker.width(@$datepicker.width() - (14 + 2*4 + 4)) # img width + margins + edge distance
        this.inputEl.focus();
        this.inputEl.select();
    }
    destroy() {
        //$.datepicker.dpDiv.stop(true, true)
        //@$datepicker.datepicker("hide")
        //@$datepicker.datepicker("destroy")
        super.destroy();
    }
    show() {
        //if @calendarOpen
        //  $.datepicker.dpDiv.stop(true, true).show()
        super.show();
    }
    hide() {
        //if @calendarOpen
        //  $.datepicker.dpDiv.stop(true, true).hide()
        super.hide();
    }
    position( /*_position*/) {
        //if @calendarOpen
        //  $.datepicker.dpDiv.css(top: position.top + 30, left: position.left)
        return super.position();
    }
    getValue() {
        //return @$datepicker.datepicker("getDate").getTime()
    }
    setValue(_val) {
        //@$datepicker.datepicker("setDate", new Date(val))
    }
}
DateEditorView.__name__ = "DateEditorView";
export class DateEditor extends CellEditor {
}
_j = DateEditor;
DateEditor.__name__ = "DateEditor";
(() => {
    _j.prototype.default_view = DateEditorView;
})();
//# sourceMappingURL=cell_editors.js.map