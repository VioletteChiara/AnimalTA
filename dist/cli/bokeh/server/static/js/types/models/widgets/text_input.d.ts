import { TextLikeInput, TextLikeInputView } from "./text_like_input";
import * as p from "../../core/properties";
export declare class TextInputView extends TextLikeInputView {
    model: TextInput;
    protected input_el: HTMLInputElement;
    protected _render_input(): void;
}
export declare namespace TextInput {
    type Attrs = p.AttrsOf<Props>;
    type Props = TextLikeInput.Props;
}
export interface TextInput extends TextInput.Attrs {
}
export declare class TextInput extends TextLikeInput {
    properties: TextInput.Props;
    __view_type__: TextInputView;
    constructor(attrs?: Partial<TextInput.Attrs>);
}
//# sourceMappingURL=text_input.d.ts.map