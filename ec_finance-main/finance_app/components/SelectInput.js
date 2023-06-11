import { Select, Spin } from "antd";
import axios from "axios";
import React from "react";
import PostQuery from "../common/Util";

class SearchInput extends React.Component {
  timeout;
  datasource;
  // To use cache data to avoid remote call if value is cleared
  emptyValueRemoteData = [];

  state = {
    data: [],
    value: undefined,
    fetching: false,
    showArrow:false
  };

  componentDidMount() {
    const { datasource, display_value, value } = this.props.fieldProps;
    this.datasource = datasource;

    // Configure fix data for select
    if (datasource.data !== undefined) {
      this.emptyValueRemoteData = datasource.data;
      this.setState({
        data: this.emptyValueRemoteData,
      });
    } else {
      // Add select option for the edit mode of form if select datasource is remote
      this.doRemoteSearch("");
      this.setState({
        data: [{ value: value, label: display_value }],
      });
    }

    this.setState({ value: [value] });
  }

  fetch = (value, callback) => {
    if (this.timeout) {
      clearTimeout(this.timeout);
      this.timeout = null;
    }

    const datasource = this.datasource;
    function getSelectData() {
      let postQuery = new PostQuery();
      let filterParam = {};
      const { parameters } = datasource;
      if (value != "" && parameters !== undefined && parameters.length > 0) {
        filterParam[`filter|${parameters[0].name}|contains`] = value;
      }
      postQuery.addQuery(datasource.name, filterParam);
      let postParam = postQuery.getPostQueries();
      postParam["option_meta"] = datasource.option_meta;

      const queryData = async function () {
        const res = await axios.get(datasource.query);
        return res.data;
      };

      queryData().then((d) => {
        const { data } = d;
        const options = [];
        data.map((option) => {
          options.push({
            value: option.key_value,
            label: option.display_value,
          });
        });
        callback(options);
      });
    }

    this.timeout = setTimeout(getSelectData, 300);
  };

  doClientSideSearch = (value) => {
    var data = this.emptyValueRemoteData.filter(function (item) {
      return item.label.toLowerCase().startsWith(value.toLowerCase());
    });
    this.setState({ data: data });
  };

  doRemoteSearch = (value) => {
    //Use client cache data to avoid remote call if value is cleared
    if (value == "" && this.emptyValueRemoteData.length > 0) {
      this.setState({ data: this.emptyValueRemoteData });
      return;
    }

    this.setState({ fetching: true });
    this.fetch(value, (data) => {
      if (value == "") {
        this.emptyValueRemoteData = data;
      }

      this.setState({ data });
      this.setState({ fetching: false });
    });
  };

  handleSearch = (value) => {
    if (this.datasource.parameters === undefined && this.emptyValueRemoteData.length != 0) {
      this.doClientSideSearch(value);
      return;
    }

    this.doRemoteSearch(value);
  };

  handleChange = (value, obj) => {
    this.setState({ value: value });
    if (this.props.form) {
      const fieldsValues = {};
      if(Array.isArray(value)){
      fieldsValues[this.props.fieldProps.name] = value.join();
      }else{
        fieldsValues[this.props.fieldProps.name] = value;
      }
      this.props.form.current.setFieldsValue(fieldsValues);
    }
    if(this.props.handleChange){

      this.props.handleChange(value, obj);
    }
    //
  };

  handleFocus = () => {
    this.handleSearch("");
  };
  MouseOver = (event)=> {
    event.target.style.cursor = 'pointer';
    this.setState({showArrow:true})
  }
  MouseOut = (event)=> {
    event.target.style.cursor = '';
    this.setState({showArrow:false})
    }
  render() {
    const { fetching, data, value } = this.state;
    return (
      <Select
        mode={this.props.fieldProps.mode ? this.props.fieldProps.mode : "single"}
        placeholder={this.props.placeholder}
        style={this.props.style}
        defaultActiveFirstOption={false}
        showSearch={true}
        showArrow={this.state.showArrow}
        filterOption={false}
        onSearch={this.handleSearch}
        onChange={this.handleChange}
        onFocus={this.handleFocus}
        notFoundContent={fetching ? <Spin size="small" /> : null}
        options={data}
        onClear={() => this.setState({ data: [] })}
        onDeselect={() => console.log("I am deselected")}
        disabled={this.props.disabled}
        defaultValue={this.props.value}
        onMouseEnter = {this.MouseOver}
        onMouseLeave = {this.MouseOut}
      ></Select>
    );
  }
}
export default SearchInput;
