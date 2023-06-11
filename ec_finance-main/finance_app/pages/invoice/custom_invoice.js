import AppLayout from "../../components/AppLayout";
import PageTitle from "../../components/PageTitle";
import DataForm from "../../components/DataForm";
import React, { Component } from "react";


class customInvoice extends Component {
  user_id = this.props.session.user.data.user_id;
  state = { data: {} };
  getPageListing = (status) => {
    this.setState({ status: status });
    let default_sort_col = "id";
    let default_sort_order = "descend";
      var listing = [
        {
          search: [
            { key: "", label: "Delivery Nr" },
            { key: "", label: "Customer" },
            { key: "", label: "From delivery date" },
            { key: "", label: "Till delivery date" },

          ],
          pre_view:[
          {doc:'deliverynote',label:"Delivery note",key:"delivery_no"},
        //   {doc:'',label:"Customer invoice",key:""},
        //   {doc:'',label:"User details",key:""},
        //   {doc:'',label:"Credit report  ",key:""},

          ],
          dataGridUID: "custominvoice",
          url: "",
          paging: true,
          default_sort_col: default_sort_col,
          default_sort_order: default_sort_order,
          row_selection: true,
          bind_on_load: true,
          onRow: (record, rowIndex) => {
            let bg = "";
            if (record.status == "Closed") {
              bg = "#F8FEF4";
            }
            return {
              style: {
                background: bg,
              },
            };
          },
          columns: [
            {
                value: "id",
                text: "ID",
                show: false,
                row_key: true,
                sequence: 1,
              },
              {
                value: "",
                text: "Delivery Nr.",
                sortable: true,
                sequence: 1,
                width: 150,
              },
              {
                value: "",
                text: "Customer",
                sortable: true,
                width: 150,
              },
              {
                value: "",
                text: "Delivered on.",
                sortable: true,
                width: 150,
              },
              {
                value: "",
                text: "Delivery Country",
                width: 150,
              },
              {
                value: "",
                text: "Ship tracking nr.",
                width: 100,
              },
              {
                value: "",
                text: "Order nr.",
                width: 100,
              },
              {
                value: "",
                text: "View document",
                width: 100,
              },
          ],
        },
      ]
      return listing;
  };
  getPageButtons = (status) => {
    var buttons = [];
    buttons.push(
      {
        dataGridUID:"custominvoice",
        name: "export_xls",
        title: "Export XLS",
        icon_code:"ExportOutlined",
        tooltip: "",
        sequence: 2,
      },
      {
        dataGridUID:"custominvoice",
        name : "custom_invoice",
        title :"Custom invoice",
        icon_code:"SettingOutlined",
      },
    );
    return buttons;
  };
  appSchema = {
    pageTitle: "Custom invoice",
    formSchema: {
      init_data: {},
      on_submit: {},
      edit_button: false,
      submit_button: false,
      hide_buttons: false,
      disabled: true,
      readonly: false,
      buttons_position: "top",
      buttons: this.getPageButtons("custominvoice"),
      listing: this.getPageListing("custominvoice"),
    },
  };
  refresh=()=>{
    this.dataForm.refreshTable();
  }
  componentDidMount = () => {
  };
  render() {
    return (
      <div>
        <PageTitle pageTitle={this.appSchema.pageTitle}></PageTitle>
        <DataForm
          schema={this.appSchema}
          initData={this.state}
          ref={(node) => {
            this.dataForm = node;
          }}
        ></DataForm>
      </div>
    );
  }
}
export default customInvoice;