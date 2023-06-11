import DataGrid from "../components/DataGrid";
import AdvancedSearch from "../components/AdvancedSearch";
import PreViewPane from "../components/PreViewPane";
import React, { Component } from "react";
import { Affix, Button } from 'antd';
import {DoubleLeftOutlined} from "@ant-design/icons";
import AppModal from "./AppModal";

class index extends Component {
  state = { data: {}, isModalVisible: false,showPreViewPane:false };

  componentDidMount = () => {};

  rowSelectionChange = (key, selectedRows) => {
    if (this.props.onRowSelectionChange) {
      this.props.onRowSelectionChange(key, selectedRows);
    }
    if(this.preViewPane){
      this.preViewPane.selectedData(selectedRows);
  }
  };
  setRefreshTable = (refreshChildTableFunc) => {
    this.refresh = refreshChildTableFunc;  
  };
  onShowPreViewPane=()=>{
    this.preViewPane.showDrawer();
  }
  onModalClose = (data) => {
    if (data.action == "reload_table") {
      this.refresh();
    }
  };
  onClose= (data) => {
      this.refresh();
  };
  showModal = (title, url) => {
    this.appModal.showModal(title, url);
  };
  searchData = (searchData) => {
    this.dataGrid.reloadTable(searchData);
  };
  getDataSource=()=>{
    return this.dataGrid.getDataSource();
  }
  setDataSource=(data)=>{
    return this.dataGrid.setDataSource(data);
  }
  getSelectedRows = () => {
    return this.dataGrid.getSelectedRows();
  };
  render() {
    console.log('this.props.schema.pre_view',this.props.schema.pre_view);
    return (
      <div className="tms-data-grid-viewer site-drawer-render-in-current-wrapper"  ref={(node) => {
        this.container = node;
      }}>
        {this.props.schema.pre_view &&
        <>
        <Affix className="view-pane-position prePane">
        <div onClick={this.onShowPreViewPane}><DoubleLeftOutlined /></div>
        </Affix>
        <PreViewPane PreViewList={this.props.schema.pre_view} ref={(node) => {
            this.preViewPane = node;
          }} ></PreViewPane>
          </>
        }
        {this.props.schema.search && <AdvancedSearch onSearch={this.searchData} style={this.props.searchStyle} searchSchema={this.props.schema.search}></AdvancedSearch>}
        <DataGrid
          name={this.props.schema.dataGridUID}
          appSchema={this.props.schema}
          onRowSelectionChange={this.rowSelectionChange}
          setRefreshTableFuncRef={this.setRefreshTable}
          showModal={this.showModal}
          scroll={this.props.schema.scroll}
          ref={(node) => {
            this.dataGrid = node;
          }}
        />
        <AppModal
          callBack={this.onClose}
          visible={this.state.isModalVisible}
          ref={(node) => {
            this.appModal = node;
          }}
        ></AppModal>
      </div>
    );
  }
}

export default index;
