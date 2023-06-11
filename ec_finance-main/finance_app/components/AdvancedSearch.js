import { DeleteOutlined, FilterFilled, SearchOutlined } from "@ant-design/icons";
import { Input, Select, Tag, Modal, DatePicker, Row, Col, Divider } from "antd";
import React from "react";
import moment from "moment";
const { RangePicker } = DatePicker;
class AdvancedSearch extends React.Component {
  draggleRef = React.createRef();
  state = {
    selectedItems: [],
    inputtext: "",
    fetching: false,
    options: [],
    searchData: {},
    overDisabled: false,
    searchFilterData: [],
    advancedSearchVisible: false,
    bounds: {
      left: 0,
      top: 0,
      bottom: 0,
      right: 0,
    },
  };
  onPreventMouseDown = (event) => {
    event.preventDefault();
    event.stopPropagation();
    return false;
  };
  onInputKeyPress = (event) => {
    //console.log(event);
  };
  onSearch = () => {
    var searchData = {};
    Object.entries(this.state.searchData).forEach(([key, value]) => {
      if (value.inputtext != "") {
        var data = [];
        data[0] = "text";
        data[1] = value.inputtext;
        searchData[key] = data;
      }
    });
    this.props.onSearch(searchData);
    var afterOnSearch = {};
    Object.entries(this.state.searchData).forEach(([key, val]) => {
      val["edit"] = "false";
      afterOnSearch[key] = val;
    });
    this.setState({ searchData: afterOnSearch });
  };
  onAdvancedSearchCancel = () => {
    var searchData = {};
    this.props.onSearch(searchData);
    this.setState({
      advancedSearchVisible: false,
    });
  };
  onAdvancedSearchOK = () => {
    var searchData = {};
    Object.entries(this.state.searchFilterData).forEach(([key, val]) => {
      Object.entries(val).forEach(([key, val]) => {
        var data = [];
        data[0] = "datetime";
        data[1] = val[0];
        data[2] = val[1];
        searchData[key] = data;
      });
    });
    this.props.onSearch(searchData);
    this.setState({
      advancedSearchVisible: false,
    });
  };
  onStart = (_event, uiData) => {
    const { clientWidth, clientHeight } = window.document.documentElement;
    const targetRect = this.draggleRef.current?.getBoundingClientRect();

    if (!targetRect) {
      return;
    }

    this.setState({
      bounds: {
        left: -targetRect.left + uiData.x,
        right: clientWidth - (targetRect.right - uiData.x),
        top: -targetRect.top + uiData.y,
        bottom: clientHeight - (targetRect.bottom - uiData.y),
      },
    });
  };
  getFilterField = (fields) => {
    let dataFields = [];
    {
      fields &&
        fields.map((field) => {
          field = {
            ...field,
            handleFiles: this.handleFiles,
          };
          if (field.is_advanced) {
            let field_name = field.key;
            dataFields.push(
              <Row>
                <span style={{ display: "flex" }}>
                  <Col span={11}>
                    <h3 style={{ marginTop: 5 }}>{field.label} </h3>
                  </Col>
                  <Col span={1}>:</Col>
                  <Col span={18}>
                    {field.searchType == "datetime" ? (
                      <span>
                        <RangePicker
                          placement={"bottomLeft"}
                          format="YYYY-MM-DD HH:mm:ss"
                          key={field.value}
                          bordered={false}
                          size={"large"}
                          ranges={{
                            Today: [moment("00:00:00","HH:mm:ss "), moment("23:59:59","HH:mm:ss ")],
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
                              let startDate = e[0].format("YYYY-MM-DD HH:mm:ss");
                              let endDate = e[1].format("YYYY-MM-DD HH:mm:ss");
                              this.setState({ searchFilterData: this.state.searchFilterData.concat([{ [field_name]: [startDate, endDate] }]) });
                            }
                          }}
                        ></RangePicker>
                      </span>
                    ) : (
                      <Input defaultValue={this.state.input} placeholder="placeholder" />
                    )}
                  </Col>
                </span>
                {/* <Divider></Divider> */}
              </Row>
            );
          }
        });
    }
    return dataFields;
  };
  tagRender = (props) => {
    const { label, value, closable, onClose } = props;
    const optionsData = this.props.searchSchema.filter(function (option) {
      return option.key == value;
    });

    const onInputClick = (event) => {
      event.target.focus();
      event.preventDefault();
      event.stopPropagation();
    };
    const onKeyDown = (event) => {
      event.stopPropagation();
    };
    const onSearchlableClick = (event) => {
      var searchData = this.state.searchData;
      searchData[event.currentTarget.id].edit = "true";
      this.setState({ searchData: searchData });
      event.preventDefault();
      event.stopPropagation();
    };
    const handleChange = (event) => {
      var searchData = this.state.searchData;
      searchData[event.currentTarget.id].inputtext = event.target.value;
      this.setState({ searchData: searchData });
      event.preventDefault();
      event.stopPropagation();
    };

    return (
      <Tag closable={closable} onClose={onClose} style={{ marginRight: 3 }} closeIcon={<DeleteOutlined />} id={optionsData[0].key} onClick={onSearchlableClick}>
        <span className="advanced-search"> {optionsData[0].label}</span>:
        {this.state.searchData[optionsData[0].key].edit == "true" && (
          <Input
            onFocus={this.onInputfocus}
            onBlur={this.onInputBlur}
            id={optionsData[0].key}
            className="advancedSearch-input"
            key={optionsData[0].key}
            value={this.state.searchData[optionsData[0].key].inputtext}
            onChange={handleChange}
            onClick={onInputClick}
            onKeyDown={onKeyDown}
            onPressEnter={() =>
              setTimeout(() => {
                this.onSearch();
              }, 100)
            }
          />
        )}
        {this.state.searchData[optionsData[0].key].edit == "false" && (
          <span className="advancedSearch-values">{this.state.searchData[optionsData[0].key].inputtext} </span>
        )}
      </Tag>
    );
  };
  handleChange = (selectedItems, Option) => {
    this.setState({ selectedItems });
    var newData = [];
    this.props.searchSchema.forEach((element) => {
      if (selectedItems.includes(element.key)) {
        var data = { value: element.key, label: element.label };
        newData.push(data);
      }
    });
    var searchData = {};
    Option.forEach((o) => {
      searchData[o.value] = o;
    });
    this.setState({ options: newData, searchData: searchData });

    setTimeout(() => {
      this.onSearch();
    }, 100);
  };
  searchDataInselect = (value) => {
    this.setState({ inputtext: value });
    var newData = [];
    this.props.searchSchema.forEach((element) => {
      if (!this.state.selectedItems.includes(element.key) && !("searchType" in element)) {
        var data = { value: element.key, label: element.label };
        newData.push(data);
      }
    });
    this.setState({ options: newData });
  };
  render() {
    let placeholder = "Search any";
    this.props.searchSchema.forEach((element) => {
      placeholder = placeholder + " " + element.label + ",";
    });
    let style = { minWidth: "100%" };
    if (this.props.style) {
      style = this.props.style;
    }
    const { selectedItems } = this.state;
    const filteredOptions = this.state.options.filter(function (option) {
      // return !selectedItems.includes(option.value);
      return option.value;
    });
    const is_AdvancedSearch = this.props.searchSchema.filter((option) => option.is_advanced === true);
    return (
      <div className="advancedSearch-box">
        <Select
          className="advancedSearch-option"
          mode="multiple"
          placeholder={placeholder}
          filterOption={false}
          multiple={false}
          showArrow
          tagRender={this.tagRender}
          style={style}
          onChange={this.handleChange}
          onSearch={this.searchDataInselect}
          notFoundContent={null}
          suffixIcon={
            is_AdvancedSearch.length > 0 ? (
              <FilterFilled
                onClick={(e) => {
                  this.setState({ advancedSearchVisible: true });
                }}
                style={{ zIndex: 1000, marginRight: 30, background: "#fffff" }}
              />
            ) : (
              <SearchOutlined />
            )
          }
        >
          {filteredOptions.map((item) => (
            <Select.Option key={item.value} value={item.value} label={item.value} inputtext={this.state.inputtext} edit="false">
              <span>Search in </span> <b>{item.label} </b>: {this.state.inputtext}
            </Select.Option>
          ))}
        </Select>
        <Modal
          okText="Search"
          cancelText="Reset"
          // maskClosable={false}
          mask={false}
          visible={this.state.advancedSearchVisible}
          onOk={this.onAdvancedSearchOK}
          onCancel={this.onAdvancedSearchCancel}
          width={750}
          style={{ float: "right", marginTop: 100, marginRight: 60, position: "relative" }}
        >
          <fieldset>{this.getFilterField(this.props.searchSchema)}</fieldset>
        </Modal>
      </div>
    );
  }
}
export default AdvancedSearch;
