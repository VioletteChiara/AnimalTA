var _a, _b;
import { span } from "../../../core/dom";
import { Grid as SlickGrid, Group } from "@bokeh/slickgrid";
import { DTINDEX_NAME } from "./definitions";
import { TableDataProvider, DataTableView, DataTable } from "./data_table";
import { ColumnDataSource } from "../../sources/column_data_source";
import { RowAggregator } from "./row_aggregators";
import { Model } from "../../../model";
function groupCellFormatter(_row, _cell, _value, _columnDef, dataContext) {
    const { collapsed, level, title } = dataContext;
    const toggle = span({
        class: `slick-group-toggle ${collapsed ? "collapsed" : "expanded"}`,
        style: { "margin-left": `${level * 15}px` },
    });
    const titleElement = span({
        class: "slick-group-title",
        level,
    }, title);
    return `${toggle.outerHTML}${titleElement.outerHTML}`;
}
function indentFormatter(formatter, indent) {
    return (row, cell, value, columnDef, dataContext) => {
        const spacer = span({
            class: "slick-group-toggle",
            style: { "margin-left": `${(indent ?? 0) * 15}px` },
        });
        const formatted = formatter ? formatter(row, cell, value, columnDef, dataContext) : `${value}`;
        return `${spacer.outerHTML}${formatted && formatted.replace(/^<div/, "<span").replace(/div>$/, "span>")}`;
    };
}
function handleGridClick(event, args) {
    const item = this.getDataItem(args.row);
    if (item instanceof Group && event.target.classList.contains("slick-group-toggle")) {
        if (item.collapsed) {
            this.getData().expandGroup(item.groupingKey);
        }
        else {
            this.getData().collapseGroup(item.groupingKey);
        }
        event.stopImmediatePropagation();
        event.preventDefault();
        this.invalidate();
        this.render();
    }
}
export class GroupingInfo extends Model {
    constructor(attrs) {
        super(attrs);
    }
    get comparer() {
        return (a, b) => {
            return a.value === b.value ? 0 : a.value > b.value ? 1 : -1;
        };
    }
}
_a = GroupingInfo;
GroupingInfo.__name__ = "GroupingInfo";
(() => {
    _a.define(({ Boolean, String, Array, Ref }) => ({
        getter: [String, ""],
        aggregators: [Array(Ref(RowAggregator)), []],
        collapsed: [Boolean, false],
    }));
})();
export class DataCubeProvider extends TableDataProvider {
    constructor(source, view, columns, target) {
        super(source, view);
        this.columns = columns;
        this.groupingInfos = [];
        this.groupingDelimiter = ":|:";
        this.target = target;
    }
    setGrouping(groupingInfos) {
        this.groupingInfos = groupingInfos;
        this.toggledGroupsByLevel = groupingInfos.map(() => ({}));
        this.refresh();
    }
    extractGroups(rows, parentGroup) {
        const groups = [];
        const groupsByValue = new Map();
        const level = parentGroup ? parentGroup.level + 1 : 0;
        const { comparer, getter } = this.groupingInfos[level];
        rows.forEach((row) => {
            const value = this.source.data[getter][row];
            let group = groupsByValue.get(value);
            if (!group) {
                const groupingKey = parentGroup ? `${parentGroup.groupingKey}${this.groupingDelimiter}${value}` : `${value}`;
                group = Object.assign(new Group(), { value, level, groupingKey });
                groups.push(group);
                groupsByValue.set(value, group);
            }
            group.rows.push(row);
        });
        if (level < this.groupingInfos.length - 1) {
            groups.forEach((group) => {
                group.groups = this.extractGroups(group.rows, group);
            });
        }
        groups.sort(comparer);
        return groups;
    }
    calculateTotals(group, aggregators) {
        const totals = { avg: {}, max: {}, min: {}, sum: {} };
        const { source: { data } } = this;
        const keys = Object.keys(data);
        const items = group.rows.map(i => keys.reduce((o, c) => ({ ...o, [c]: data[c][i] }), {}));
        aggregators.forEach((aggregator) => {
            aggregator.init();
            items.forEach((item) => aggregator.accumulate(item));
            aggregator.storeResult(totals);
        });
        return totals;
    }
    addTotals(groups, level = 0) {
        const { aggregators, collapsed: groupCollapsed } = this.groupingInfos[level];
        const toggledGroups = this.toggledGroupsByLevel[level];
        groups.forEach((group) => {
            if (group.groups) {
                this.addTotals(group.groups, level + 1);
            }
            if (aggregators.length && group.rows.length) {
                group.totals = this.calculateTotals(group, aggregators);
            }
            group.collapsed = groupCollapsed !== toggledGroups[group.groupingKey];
            group.title = group.value ? `${group.value}` : "";
        });
    }
    flattenedGroupedRows(groups, level = 0) {
        const rows = [];
        groups.forEach((group) => {
            rows.push(group);
            if (!group.collapsed) {
                const subRows = group.groups
                    ? this.flattenedGroupedRows(group.groups, level + 1)
                    : group.rows;
                rows.push(...subRows);
            }
        });
        return rows;
    }
    refresh() {
        const groups = this.extractGroups([...this.view.indices]);
        const labels = this.source.data[this.columns[0].field];
        if (groups.length) {
            this.addTotals(groups);
            this.rows = this.flattenedGroupedRows(groups);
            this.target.data = {
                row_indices: this.rows.map(value => value instanceof Group ? value.rows : value),
                labels: this.rows.map(value => value instanceof Group ? value.title : labels[value]),
            };
        }
    }
    getLength() {
        return this.rows.length;
    }
    getItem(i) {
        const item = this.rows[i];
        const { source: { data } } = this;
        return item instanceof Group
            ? item
            : Object.keys(data)
                .reduce((o, c) => ({ ...o, [c]: data[c][item] }), { [DTINDEX_NAME]: item });
    }
    getItemMetadata(i) {
        const myItem = this.rows[i];
        const columns = this.columns.slice(1);
        const aggregators = myItem instanceof Group
            ? this.groupingInfos[myItem.level].aggregators
            : [];
        function adapter(column) {
            const { field: myField, formatter } = column;
            const aggregator = aggregators.find(({ field_ }) => field_ === myField);
            if (aggregator) {
                const { key } = aggregator;
                return {
                    formatter(row, cell, _value, columnDef, dataContext) {
                        return formatter ? formatter(row, cell, dataContext.totals[key][myField], columnDef, dataContext) : "";
                    },
                };
            }
            return {};
        }
        return myItem instanceof Group
            ? {
                selectable: false,
                focusable: false,
                cssClasses: "slick-group",
                columns: [{ formatter: groupCellFormatter }, ...columns.map(adapter)],
            }
            : {};
    }
    collapseGroup(groupingKey) {
        const level = groupingKey.split(this.groupingDelimiter).length - 1;
        this.toggledGroupsByLevel[level][groupingKey] = !this.groupingInfos[level].collapsed;
        this.refresh();
    }
    expandGroup(groupingKey) {
        const level = groupingKey.split(this.groupingDelimiter).length - 1;
        this.toggledGroupsByLevel[level][groupingKey] = this.groupingInfos[level].collapsed;
        this.refresh();
    }
}
DataCubeProvider.__name__ = "DataCubeProvider";
export class DataCubeView extends DataTableView {
    render() {
        const options = {
            enableCellNavigation: this.model.selectable !== false,
            enableColumnReorder: false,
            autosizeColsMode: this.autosize,
            multiColumnSort: false,
            editable: this.model.editable,
            autoEdit: this.model.auto_edit,
            rowHeight: this.model.row_height,
        };
        const columns = this.model.columns.map(column => column.toColumn());
        columns[0].formatter = indentFormatter(columns[0].formatter, this.model.grouping.length);
        delete columns[0].editor;
        this.data = new DataCubeProvider(this.model.source, this.model.view, columns, this.model.target);
        this.data.setGrouping(this.model.grouping);
        this.el.style.width = `${this.model.width}px`;
        this.grid = new SlickGrid(this.el, this.data, columns, options);
        this.grid.onClick.subscribe(handleGridClick);
    }
}
DataCubeView.__name__ = "DataCubeView";
export class DataCube extends DataTable {
    constructor(attrs) {
        super(attrs);
    }
}
_b = DataCube;
DataCube.__name__ = "DataCube";
(() => {
    _b.prototype.default_view = DataCubeView;
    _b.define(({ Array, Ref }) => ({
        grouping: [Array(Ref(GroupingInfo)), []],
        target: [Ref(ColumnDataSource)],
    }));
})();
//# sourceMappingURL=data_cube.js.map