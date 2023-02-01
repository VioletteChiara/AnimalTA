import * as p from "../../core/properties";
import { Widget, WidgetView } from "./widget";
export declare class FileInputView extends WidgetView {
    model: FileInput;
    protected dialog_el: HTMLInputElement;
    connect_signals(): void;
    render(): void;
    load_files(files: FileList): Promise<void>;
    protected _read_file(file: File): Promise<string>;
}
export declare namespace FileInput {
    type Attrs = p.AttrsOf<Props>;
    type Props = Widget.Props & {
        value: p.Property<string | string[]>;
        mime_type: p.Property<string | string[]>;
        filename: p.Property<string | string[]>;
        accept: p.Property<string>;
        multiple: p.Property<boolean>;
    };
}
export interface FileInput extends FileInput.Attrs {
}
export declare class FileInput extends Widget {
    properties: FileInput.Props;
    __view_type__: FileInputView;
    constructor(attrs?: Partial<FileInput.Attrs>);
}
//# sourceMappingURL=file_input.d.ts.map