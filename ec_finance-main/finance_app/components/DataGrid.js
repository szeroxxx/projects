import { SearchOutlined } from "@ant-design/icons";
import { Button, DatePicker, Form, Input, Pagination, Select, Space, Table, Tooltip, Affix } from "antd";
import axios from "axios";
import moment from "moment";
import React, { useContext, useEffect, useRef, useState } from "react";
import JsxParser from "react-jsx-parser";
import Constant from "../common/Constant";

const EditableContext = React.createContext(null);
let sortOrder, sortColumn, rowKey;
const { RangePicker } = DatePicker;
const { Search } = Input;
const { Option } = Select;
const EditableRow = ({ index, ...props }) => {
  const [form] = Form.useForm();
  return (
    <Form form={form} component={false}>
      <EditableContext.Provider value={form}>
        <tr {...props} />
      </EditableContext.Provider>
    </Form>
  );
};
const EditableCell = ({ title, required, editable, children, dataIndex, record, handleSave, ...restProps }) => {
  const [editing, setEditing] = useState(false);
  const inputRef = useRef(null);
  const form = useContext(EditableContext);
  useEffect(() => {
    if (editing) {
      inputRef.current.focus();
    }
  }, [editing]);

  const toggleEdit = () => {
    setEditing(!editing);
    form.setFieldsValue({
      [dataIndex]: record[dataIndex],
    });
  };

  const save = async () => {
    try {
      const values = await form.validateFields();
      toggleEdit();
      handleSave({ ...record, ...values });
    } catch (errInfo) {}
  };

  let childNode = children;

  if (editable) {
    childNode = editing ? (
      <Form.Item
        style={{
          margin: 0,
        }}
        name={dataIndex}
        rules={[
          {
            required: required,
            message: `${title} is required.`,
          },
        ]}
      >
        <Input ref={inputRef} onPressEnter={save} onBlur={save} />
      </Form.Item>
    ) : (
      <div
        className="editable-cell-value-wrap"
        style={{
          paddingRight: 24,
        }}
        onClick={toggleEdit}
      >
        {children}
      </div>
    );
  }

  return <td {...restProps}>{childNode}</td>;
};

class DataGrid extends React.Component {
  state = {
    data: [],
    columns: [],
    selectedRowKeys: [],
    selectedRows: [],
    pagination: {
      current: 1,
      pageSize: Constant.LIST_PAGE_SIZE, //TODO: Set up from the profile
    },
    loading: false,
    searchData: {},
  };
  getTableScroll = (is_gridViewer) => {
    let extraHeight = 74;
    let tHeader = null;
    let id = null;
    if (id) {
      tHeader = document.getElementById(id) ? document.getElementById(id).getElementsByClassName("ant-table-thead")[0] : null;
    } else {
      tHeader = document.getElementsByClassName("ant-table-thead")[0];
    }
    let tHeaderBottom = 0;
    let tHeaderTop = 0;

    if (tHeader) {
      tHeaderBottom = tHeader.getBoundingClientRect().bottom;
      tHeaderTop = tHeader.getBoundingClientRect().top;
    }

    var header_height = 0;
    var search_header_height = 0;
    var pagination = 64;
    var margin = 10;
    var topActionHeight = 0;
    var layout_footer_height = 0;
    var pageTitleHeight = 0;
    var extra_fields_height = 0;
    var check_box_height = 0;
    var sheduler_button = 0;

    let header = document.getElementsByClassName("ant-layout-header")[0];
    if (header) {
      header_height = header.getBoundingClientRect().height; //""
    }
    let topAction = document.getElementsByClassName("ant-space-horizontal")[0];
    if (topAction) {
      topActionHeight = topAction.getBoundingClientRect().height;
    }
    let pageTitle = document.getElementsByClassName("ant-space ant-space-vertical")[0];
    if (pageTitle) {
      pageTitleHeight = pageTitle.getBoundingClientRect().height;
    }
    let layout_footer = document.getElementsByClassName("layot-footer-pagination")[0];
    if (layout_footer) {
      layout_footer_height = topAction.getBoundingClientRect().height;
    }
    let search_header = document.getElementsByClassName("ant-tabs-nav-wrap")[0];
    if (search_header) {
      search_header_height = search_header.getBoundingClientRect().height;
    }
    let extra_fields = document.getElementsByClassName("extra-fields")[0];
    if (extra_fields){
      extra_fields_height = topAction.getBoundingClientRect().height;
    }
    let check_box = document.getElementsByClassName("checkBox")[0];
    if (check_box){
      check_box_height = topAction.getBoundingClientRect().height;
    }
    let sheduler_btn = document.getElementsByClassName("sheduler-btn")[0];
    if (sheduler_btn){
      sheduler_button = topAction.getBoundingClientRect().height;
    }
    if (is_gridViewer) {
      let height = `calc(100vh - ${extraHeight + header_height + search_header_height + pagination + margin + topActionHeight + layout_footer_height+ extra_fields_height+ check_box_height+sheduler_button}px)`;
      this.setState({ ScrollY: height });
    } else {
      let height = `calc(100vh - ${tHeaderTop + pagination + margin + topActionHeight + layout_footer_height + search_header}px)`;
      this.setState({ ScrollY: height });
    }
  };
  getDataSource = () => {
    return this.state.data;
  };
  setDataSource = (data) => {
    this.setState({ data: data });
  };
  componentDidMount() {
    const is_gridViewer = typeof this.props.appSchema.gridViewer == "undefined" ? true : false;

    this.getTableScroll(is_gridViewer);
    this.props.setRefreshTableFuncRef(this.reloadTable);
    this.setColumns();
  }

  onEditShowModal = (text, record, index, modal) => {
    let url = modal.url;
    let title = modal.title ?? "";
    if (modal.title_key) {
      modal.title_key.forEach((key) => {
        if (title != "") {
          title = title + " - " + record[key];
        } else {
          title = record[key];
        }
      });
    }
    var queryData = "";
    if (modal.params) {
      modal.params.forEach((param) => {
        url = url + "/" + record[param];
      });
    }
    if (modal.queryParams) {
      modal.queryParams.forEach((param) => {
        if (param.value) {
          queryData = queryData + param.key + "=" + param.value + "&";
        } else {
          queryData = queryData + param.key + "=" + record[param.key] + "&";
        }
      });
    }
    if (queryData != "") {
      if (url.includes("?")) {
        url = url + "&" + queryData;
      } else {
        url = url + "?" + queryData;
      }
    }
    this.props.showModal(title, url);
  };
  handleTableChange = (pagination, filters, sorter) => {
    pagination = this.state.pagination;
    this.filters = filters;
    this.sorter = sorter;
    this.fetch({
      sortField: sorter === undefined || sorter.field === undefined ? this.props.appSchema.default_sort_col : sorter.field,
      sortOrder: sorter === undefined || sorter.order === undefined ? this.props.appSchema.default_sort_order : sorter.order,
      pagination,
      filters: filters,
    });
  };
  UNSAFE_componentWillMount() {
    const is_gridViewer = typeof this.props.appSchema.gridViewer == "undefined" ? true : false;
    new Promise((resolve, reject) => {
      setTimeout(() => {
        resolve();
      }, 2000);
    }).then(() => {
      this.getTableScroll(is_gridViewer);
    });
  }
  componentDidUpdate = (preProps, preState) => {
    if (preState.ScrollY !== this.state.ScrollY) {
      const is_gridViewer = typeof this.props.appSchema.gridViewer == "undefined" ? true : false;

      this.getTableScroll(is_gridViewer);
    }
  };
  setColumns = () => {
    let { columns, bind_on_load, default_sort_col, default_sort_order } = this.props.appSchema;
    let cols = [];

    // It will render column in order based on the defined sequence in schema
    columns = columns.sort((first, second) => {
      return first.sequence - second.sequence;
    });
    columns.forEach((column) => {
      if (column.row_key) {
        rowKey = column.value;
      }
      if (column.show !== undefined && column.show === false) {
        return;
      }
      let col = {
        dataIndex: column.value,
        title: column.text,
        sorter: column.sortable ? true : false,
      };
      if (column.width) {
        col["width"] = column.width;
      }
      if (column.fixed) {
        col["fixed"] = column.fixed;
      }
      if (column.editable) {
        col["editable"] = column.editable;
      }
      if (column.required) {
        col["required"] = column.required;
      }
      if (column.fixed) {
        col["fixed"] = column.fixed;
      }

      let cellStyle = {};

      // To apply text-overflow ellipsis
      if (column.overflow === false) {
        cellStyle["whiteSpace"] = "nowrap";
        cellStyle["maxWidth"] = column.width;
      }

      if (column.align !== undefined) {
        cellStyle["textAlign"] = column.align;
      }

      if (Object.keys(cellStyle).length > 0) {
        col["onCell"] = () => {
          return {
            style: cellStyle,
          };
        };
      }
      if (column.render !== undefined && typeof column.render == "function") {
        col["render"] = column.render;
      } else {
        col["render"] = (text, record, index) => {
          if (column.overflow === false) {
            return (
              <Tooltip title={text}>
                <div style={{ textOverflow: "ellipsis", overflow: "hidden" }}>{text}</div>
              </Tooltip>
            );
          } else if (column.render) {
            return (
              <JsxParser
                bindings={{
                  text: text,
                  record: record,
                }}
                jsx={column.render}
              />
            );
          } else if (column.modal) {
            return (
              <a className={column.class ? column.class : ""} onClick={() => this.onEditShowModal(text, record, index, column.modal)}>
                {column.modal.text ? column.modal.text : text}
              </a>
            );
          } else {
            return text;
          }
        };
      }
      if (column.searchable) {
        // If column searchable then merge col and getColumnSearchProps dicts. It will show search icon over the column header.
        col = {
          ...this.getColumnSearchProps(column),
          ...col,
        };
      }
      cols.push(col);
    });
    this.setState({
      columns: cols,
    });
    if (bind_on_load === false) {
      this.setState({
        loading: false,
        data: [],
      });
    } else {
      const { pagination } = this.state;
      this.fetch({
        sortField: default_sort_col,
        sortOrder: default_sort_order,
        pagination,
      });
    }
  };
  rowSelectionChange = (key, selectedRows) => {};

  reloadTable = (searchData) => {
    if (searchData) {
      this.setState({
        searchData: searchData,
      });
    }
    const { default_sort_col, default_sort_order } = this.props.appSchema;
    const { pagination } = this.state;
    this.fetch(
      {
        sortField: default_sort_col,
        sortOrder: default_sort_order,
        pagination,
      },
      searchData
    );
  };

  fetch = (params = {}, searchData = {}) => {
    this.setState({ loading: true, selectedRowKeys: [], selectedRows: [] });
    this.onSelectChange(this.state.selectedRowKeys, this.state.selectedRows);
    //TODO: Improvement: Pass from schema. Avoid code
    sortOrder = params.sortOrder == "descend" ? "desc" : "asc";
    sortColumn = params.sortField;

    let listQueryParam = {
      sortCol: sortColumn,
      sortOrder: sortOrder,
      page: params.pagination.current,
      pageSize: params.pagination.pageSize,
      query: {},
    };

    let axiosRequest = null;
    let queryParam =
      Constant.APP_LIST_HTTP_HANDLER == "Get"
        ? `page=${listQueryParam.page}&page_size=${listQueryParam.pageSize}&ordering=${sortOrder == "desc" ? "-" + sortColumn : sortColumn}`
        : "";
    if (params.filters) {
      for (let [key, value] of Object.entries(params.filters)) {
        if (value != null) {
          let searchType = value[0];
          if (searchType === "datetime") {
            listQueryParam["query"][`filter|${key}|gte`] = value[1];
            listQueryParam["query"][`filter|${key}|lte`] = value[2];
            if (Constant.APP_LIST_HTTP_HANDLER == "Get") {
              queryParam += `&${key}_gte=${value[1]}&${key}_lte=${value[2]}`;
            }
          } else {
            listQueryParam["query"][`filter|${key}|contains`] = value[1];
            if (Constant.APP_LIST_HTTP_HANDLER == "Get") queryParam += `&${key}=${value[1]}`;
          }
        }
      }
    }
    if (this.state.searchData) {
      Object.entries(this.state.searchData).forEach(([key, value]) => {
        if (value != null) {
          let searchType = value[0];
          if (searchType === "datetime") {
            listQueryParam["query"][`filter|${key}|gte`] = value[1];
            listQueryParam["query"][`filter|${key}|lte`] = value[2];
          } else {
            listQueryParam["query"][`filter|${key}|contains`] = value[1];
            if (Constant.APP_LIST_HTTP_HANDLER == "Get") queryParam += `&${key}=${value[1]}`;
          }
        }
      });
    }
    if (searchData) {
      Object.entries(searchData).forEach(([key, value]) => {
        if (value != null) {
          let searchType = value[0];
          if (searchType === "datetime") {
            listQueryParam["query"][`filter|${key}|gte`] = value[1];
            listQueryParam["query"][`filter|${key}|lte`] = value[2];
            if (Constant.APP_LIST_HTTP_HANDLER == "Get") {
              queryParam += `&${key}_gte=${value[1]}&${key}_lte=${value[2]}`;
            }
          } else {
            listQueryParam["query"][`filter|${key}|contains`] = value[1];
            if (Constant.APP_LIST_HTTP_HANDLER == "Get") queryParam += `&${key}=${value[1]}`;
          }
        }
      });
    }
    if (Constant.APP_LIST_HTTP_HANDLER == "Get") {
      if (this.props.appSchema.url.includes("?")) {
        queryParam = "&" + queryParam;
      } else {
        queryParam = "?" + queryParam;
      }
      axiosRequest = axios.get(this.props.appSchema.url + queryParam);
    } else {
      axiosRequest = axios.post(this.props.appSchema.url, listQueryParam);
    }

    axiosRequest.then((result) => {
      this.setState({
        loading: false,
        data: result.data.data,
        pagination: {
          ...params.pagination,
          total: result.data.totalRecords,
        },
      });
    });
  };
  getSelectedRows = () => {
    return this.state.selectedRows;
  };
  onSelectChange = (selectedRowKeys, selectedRows) => {
    if (this.props.appSchema.row_selection_type == "single") {
      if (this.state.selectedRowKeys.length > 0) {
        let newRow = [];
        let RowKeys = [];
        for (var i = 0; i < selectedRowKeys.length; i++) {
          if (this.state.selectedRowKeys[0] != selectedRowKeys[i]) {
            RowKeys.push(selectedRowKeys[i]);
          }
        }
        for (var i = 0; i < selectedRows.length; i++) {
          if (this.state.selectedRows[0] != selectedRows[i]) {
            newRow.push(selectedRows[i]);
          }
        }
        this.setState({ selectedRowKeys: RowKeys, selectedRows: newRow });
      } else {
        this.setState({ selectedRowKeys, selectedRows });
      }
    } else {
      this.setState({ selectedRowKeys, selectedRows });
      //this.setState({ selectedRows });
    }
    this.props.onRowSelectionChange(this.props.name, selectedRows);
  };
  getColumnSearchProps = (column) => {
    let props = {
      filterDropdown: ({ setSelectedKeys, selectedKeys, confirm, clearFilters }) => {
        return (
          <div style={{ padding: 8 }}>
            {column.type == "datetime" ? (
              <div style={{ marginBottom: 8, display: "block" }}>
                {/* TODO: Apply datetime localization.
              https://ant.design/components/date-picker/#Localization */}
                <RangePicker
                  size={"small"}
                  ref={(node) => {
                    this.searchInput = node;
                  }}
                  ranges={{
                    Today: [moment(), moment()],
                    Yesterday: [moment().subtract(1, "days"), moment().subtract(1, "days")],
                    "Last 7 Days": [moment().subtract(6, "days"), moment()],
                    "Last 30 Days": [moment().subtract(29, "days"), moment()],
                    "This Month": [moment().startOf("month"), moment().endOf("month")],
                    "Last Month": [moment().subtract(1, "months").startOf("month"), moment().subtract(1, "months").endOf("month")],
                    "This Year": [moment().startOf("year"), moment().endOf("year")],
                    "Last Year": [moment().subtract(1, "year").add(1, "day"), moment()],
                  }}
                  onChange={(e) => {
                    if (e) {
                      let startDate = e[0].format("YYYY-MM-DD");
                      let endDate = e[1].format("YYYY-MM-DD");
                      setSelectedKeys([column.type, startDate, endDate]);
                      this.handleSearch(selectedKeys, confirm, column);
                    }
                  }}
                />
              </div>
            ) : (
              <Input
                ref={(node) => {
                  this.searchInput = node;
                }}
                placeholder={`Search ${column.text}`}
                value={selectedKeys[1]}
                onChange={(e) => setSelectedKeys(e.target.value ? [column.type, e.target.value] : [])}
                onPressEnter={() => this.handleSearch(selectedKeys, confirm, column)}
                style={{ marginBottom: 8, display: "block" }}
              />
            )}

            <Space>
              <Button
                type="primary"
                onClick={() => this.handleSearch(selectedKeys, confirm, column)}
                icon={<SearchOutlined />}
                size="small"
                style={{ width: 90 }}
              >
                Search
              </Button>
              <Button onClick={() => this.handleReset(clearFilters)} size="small" style={{ width: 90 }}>
                Reset
              </Button>
            </Space>
          </div>
        );
      },
      filterIcon: (filtered) => <SearchOutlined style={{ color: filtered ? "#1890ff" : undefined }} />,
      onFilterDropdownVisibleChange: (visible) => {
        if (visible) {
          setTimeout(() => {
            if (this.searchInput.constructor.name == "RangePicker") {
              //TODO: Open date-time picker automatically to improve user experience
            }

            // this.searchInput.select();
          }, 100);
        }
      },
    };
    return props;
  };

  handleSearch = (selectedKeys, confirm, column) => {
    confirm();
    this.setState({
      searchText: column.type == "datetime" ? selectedKeys : selectedKeys[0],
      searchedColumn: column.value,
      searchType: column.type,
    });
  };
  handleReset = (clearFilters) => {
    this.setState({ searchText: "", searchedColumn: "", searchType: "" });
    clearFilters();
  };

  getColumnByDataIndex = (value) => {
    const { columns } = this.state;
    const cols = columns.filter((column) => column.dataIndex == value);
    return cols[0];
  };
  renderPagination = () => {
    const { pageSize, total, current } = this.state.pagination;
    return (
      <Pagination
        defaultCurrent={1}
        focus={true}
        pageSize={pageSize}
        total={total}
        size="small"
        current={current}
        onChange={(page, pageSize) => {
          if (page == 0) {
            page = 1;
          }
          let pagination = {
            current: page,
            pageSize: pageSize,
          };
          this.setState({ pagination: pagination });
          setTimeout(() => {
            this.handleTableChange(pagination, this.filters, this.sorter);
          }, 10);
        }}
      />
    );
  };

  renderFooter = () => {
    const gridViewer = typeof this.props.appSchema.gridViewer == "undefined" ? true : false;
    return (
      <>
        {gridViewer ? (
          <Affix
            className="layot-footer-pagination"
            offsetBottom={0}
            style={{
              bottom: "0",
              paddingTop: "0px",
              position: "fixed",
              borderTop: "solid 1px #e6e6e6",
              right: "59px",
              left: "253px",
              minHeight: "60px",
              backgroundColor: "white",
            }}
          >
            <Space size="small" style={{ float: "right", paddingTop: "4px" }}>
              {this.renderPagination()}
            </Space>
          </Affix>
        ) : (
          <Space size="small" style={{ float: "right", paddingTop: "8px" }}>
            {this.renderPagination()}
          </Space>
        )}
      </>
    );
  };
  render() {
    const { columns, data, pagination, loading, selectedRowKeys } = this.state;
    let rowSelection = {
      selectedRowKeys,
      onChange: this.onSelectChange,
      //selections: [Table.SELECTION_ALL, Table.SELECTION_INVERT, Table.SELECTION_NONE],
    };
    if (this.props.appSchema.row_selection_type == "single") {
      rowSelection = {
        selectedRowKeys,
        onChange: this.onSelectChange,
      };
    }
    //Hide row selection checkboxes
    if (this.props.appSchema.row_selection === false) {
      rowSelection = null;
    }
    const handleSave = (row) => {
      const newData = [...data];
      const index = newData.findIndex((item) => row[rowKey] === item[rowKey]);
      const item = newData[index];
      newData.splice(index, 1, { ...item, ...row });
      this.setState({
        data: newData,
      });
    };

    const components = {
      body: {
        row: EditableRow,
        cell: EditableCell,
      },
    };
    const columnsNew = columns.map((col) => {
      if (!col.editable) {
        return col;
      }
      return {
        ...col,
        onCell: (record) => ({
          record,
          editable: col.editable,
          dataIndex: col.dataIndex,
          title: col.title,
          required: col.required,
          handleSave,
        }),
      };
    });
    return (
      <Table
        className={this.props.appSchema.row_selection_type}
        onRow={(record, rowIndex) => {
          if (this.props.appSchema.onRow) {
            return this.props.appSchema.onRow(record, rowIndex);
          }
        }}
        components={components}
        rowClassName={() => "editable-row"}
        columns={columnsNew}
        rowKey={(record) => {
          return record[rowKey];
        }}
        rowSelection={rowSelection}
        dataSource={data}
        pagination={false}
        loading={loading}
        scroll={{  y: this.state.ScrollY ?? this.props.scroll  }}
        onChange={this.handleTableChange}
        sticky
        size="small"
        footer={this.renderFooter}
      />
    );
  }
}
export default DataGrid;
