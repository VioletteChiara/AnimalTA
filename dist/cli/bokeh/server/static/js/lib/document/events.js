import { serialize } from "../core/serializer";
export class DocumentEvent {
    constructor(document) {
        this.document = document;
    }
}
DocumentEvent.__name__ = "DocumentEvent";
export class DocumentEventBatch extends DocumentEvent {
    constructor(document, events, setter_id) {
        super(document);
        this.events = events;
        this.setter_id = setter_id;
    }
}
DocumentEventBatch.__name__ = "DocumentEventBatch";
export class DocumentChangedEvent extends DocumentEvent {
}
DocumentChangedEvent.__name__ = "DocumentChangedEvent";
export class MessageSentEvent extends DocumentChangedEvent {
    constructor(document, msg_type, msg_data) {
        super(document);
        this.msg_type = msg_type;
        this.msg_data = msg_data;
    }
    [serialize](serializer) {
        const value = this.msg_data;
        const value_serialized = serializer.to_serializable(value);
        return {
            kind: "MessageSent",
            msg_type: this.msg_type,
            msg_data: value_serialized,
        };
    }
}
MessageSentEvent.__name__ = "MessageSentEvent";
export class ModelChangedEvent extends DocumentChangedEvent {
    constructor(document, model, attr, old, new_, setter_id, hint) {
        super(document);
        this.model = model;
        this.attr = attr;
        this.old = old;
        this.new_ = new_;
        this.setter_id = setter_id;
        this.hint = hint;
    }
    [serialize](serializer) {
        if (this.hint != null)
            return serializer.to_serializable(this.hint);
        const value = this.new_;
        const value_serialized = serializer.to_serializable(value);
        if (this.model != value) {
            // we know we don't want a whole new copy of the obj we're
            // patching unless it's also the value itself
            serializer.remove_def(this.model);
        }
        return {
            kind: "ModelChanged",
            model: this.model.ref(),
            attr: this.attr,
            new: value_serialized,
        };
    }
}
ModelChangedEvent.__name__ = "ModelChangedEvent";
export class ColumnsPatchedEvent extends DocumentChangedEvent {
    constructor(document, column_source, patches) {
        super(document);
        this.column_source = column_source;
        this.patches = patches;
    }
    [serialize](_serializer) {
        return {
            kind: "ColumnsPatched",
            column_source: this.column_source,
            patches: this.patches,
        };
    }
}
ColumnsPatchedEvent.__name__ = "ColumnsPatchedEvent";
export class ColumnsStreamedEvent extends DocumentChangedEvent {
    constructor(document, column_source, data, rollover) {
        super(document);
        this.column_source = column_source;
        this.data = data;
        this.rollover = rollover;
    }
    [serialize](_serializer) {
        return {
            kind: "ColumnsStreamed",
            column_source: this.column_source,
            data: this.data,
            rollover: this.rollover,
        };
    }
}
ColumnsStreamedEvent.__name__ = "ColumnsStreamedEvent";
export class TitleChangedEvent extends DocumentChangedEvent {
    constructor(document, title, setter_id) {
        super(document);
        this.title = title;
        this.setter_id = setter_id;
    }
    [serialize](_serializer) {
        return {
            kind: "TitleChanged",
            title: this.title,
        };
    }
}
TitleChangedEvent.__name__ = "TitleChangedEvent";
export class RootAddedEvent extends DocumentChangedEvent {
    constructor(document, model, setter_id) {
        super(document);
        this.model = model;
        this.setter_id = setter_id;
    }
    [serialize](serializer) {
        return {
            kind: "RootAdded",
            model: serializer.to_serializable(this.model),
        };
    }
}
RootAddedEvent.__name__ = "RootAddedEvent";
export class RootRemovedEvent extends DocumentChangedEvent {
    constructor(document, model, setter_id) {
        super(document);
        this.model = model;
        this.setter_id = setter_id;
    }
    [serialize](_serializer) {
        return {
            kind: "RootRemoved",
            model: this.model.ref(),
        };
    }
}
RootRemovedEvent.__name__ = "RootRemovedEvent";
//# sourceMappingURL=events.js.map