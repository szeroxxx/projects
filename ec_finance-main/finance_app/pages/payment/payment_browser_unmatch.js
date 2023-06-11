import AppLayout from "../../components/AppLayout";
import PageTitle from "../../components/PageTitle";
import AppModal from "../../components/AppModal";
import DataForm from "../../components/DataForm";
import React, { Component } from "react";
import axios from "axios";
import {ExclamationCircleOutlined  } from "@ant-design/icons";
const { confirm } = Modal;
import {Modal } from "antd";
class PaymentBrowserUnmatch extends Component {
  state = { data: {}};
  getPageListing = (status) => {
    this.setState({ status: status });
    let default_sort_col = "id";
    let default_sort_order = "descend";
    var listing = [
      {
        search: [
          { key: "customer_name", label: "Name" },
          { key: "bank_account_nr", label: "Bank account Nr." },
          { key: "amount", label: "Amount" },
          { key: "message", label: "Message" },
          { key: "created_on", label: "From created date" },
          { key: "till_created_date", label: "Till created date" },
          { key: "bank_name", label: "Bank name" },
        ],
        dataGridUID: "tblPaymentBrowserUnmatch",
        url: "/dt/payment/payment_browser_unmatch/",
        paging: true,
        default_sort_col: default_sort_col,
        default_sort_order: default_sort_order,
        row_selection: true,
        bind_on_load: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "customer_name",
            text: "Customer name",
            sortable: true,
            width: 100,
            sequence: 2,
          },
          {
            value: "bank_account_nr",
            text: "Bank account number",
            sortable: true,
            width: 130,
            sequence: 3,
          },
          {
            value: "bank_name",
            text: "Bank name",
            sortable: true,
            width: 100,
            sequence: 4,
          },
          {
            value: "amount",
            text: "Amount",
            sortable: true,
            width: 100,
            sequence: 5,
          },
          {
            value: "message",
            text: "Message",
            sortable: true,
            width: 100,
            sequence: 6,
          },
          {
            value: "invoice_nos",
            text: "Invoice Nr(s)",
            sortable: true,
            width: 100,
            sequence: 7,
          },
          {
            value: "remarks",
            text: "Remark",
            sortable: true,
            width: 100,
            sequence: 8,
          },
          {
            value: "created_on",
            text: "Created date",
            sortable: true,
            width: 100,
            sequence: 9,
          },
          {
            value: "full_name",
            text: "Created by",
            sortable: true,
            width: 100,
            sequence: 10,
          },
          {
            value: "",
            text: "Communication",
            sortable: true,
            width: 100,
            sequence: 11,
          },
        ],
      },
    ]
    return listing;
  };
  getPageButtons = () => {
    var buttons = [];
    buttons.push(
      {
        dataGridUID: "tblPaymentBrowserUnmatch",
        name: "delete",
        title: "Delete",
        primary: "primary",
        icon_code: "DeleteOutlined" ,
        tooltip: "",
        sequence: 1,
        class:"mr-left",
        multi_select: true,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows("tblPaymentBrowserUnmatch");
          this.deletePayment(data,this.refresh);
        }
      },
      {
        dataGridUID: "tblPaymentBrowserUnmatch",
        name: "search_invoices",
        title: "Search invoices",
        icon_code: "FileSearchOutlined",
        primary: "primary",
        tooltip: "",
        sequence: 2,
        class:"mr-left", 
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows("tblPaymentBrowserUnmatch");
          this.invoiceSearch(data);
        }
      },
      {
        dataGridUID: "tblPaymentBrowserUnmatch",
        name: "search_proforma_invoices",
        title: "Search Proforma invoices",
        icon_code: "FileSearchOutlined" ,
        primary: "primary",
        position:"menu",
        tooltip: "",
        sequence: 3,
        class:"mr-left", 
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows("tblPaymentBrowserUnmatch");
        }
      },
      {
        dataGridUID: "tblPaymentBrowserUnmatch",
        name: "export_xls",
        title: "Export XLS",
        icon_code: "ExportOutlined",
        primary: "primary",
        position:"menu",
        tooltip: "",
        type:"primary",
        sequence: 4,
        class:"mr-left", 
        click_handler: () => {
          this.exportXls();
        }
      },
      {
        dataGridUID: "tblPaymentBrowserUnmatch",
        name: "new_communication",
        title: "New communication",
        icon_code: "MailOutlined" ,
        primary: "primary",
        position:"menu",
        tooltip: "",
        sequence: 5,
        class:"mr-left", 
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows("tblPaymentBrowserUnmatch");
        }
      },
    )
    return buttons;
  };
  appSchema = {
    pageTitle: "Payment Browser (Unmatched)",
    formSchema: {
      init_data: {},
      on_submit: {},
      edit_button: false,
      submit_button: false,
      hide_buttons: false,
      disabled: true,
      readonly: false,
      columns: 2,
      buttons_position: "top",
      listing: this.getPageListing("all"),
      buttons: this.getPageButtons("all"),
    },
  };
  componentDidMount = () => {
    
  };
  exportXls = ()=>{
    var data = this.dataForm.getDataSource("tblPaymentBrowserUnmatch")
    var ids = ""
    for (var row in data){
      ids = ids + data[row].id +"," 
    }
    window.open("/dt/base/payment_unmatch_export/?payment_unmatch_id=" + ids )
  }
  refresh=()=>{
    this.dataForm.refreshTable('tblPaymentBrowserUnmatch');
  }
  deletePayment = (data,callback) => {
    var ids = ""
    for (var row in data){
      ids= ids+ data[row].id +"," 
    }
    confirm({
      title: "Are you sure want to delete this record ?",
      icon: <ExclamationCircleOutlined />,
      content:  <></>,
      cancelText: "No, Cancel",
      okText: "Yes, Delete",
      onOk() {
        axios.post("/dt/payment/delete_payment_unmatched/", {ids:ids.slice(0, -1)}).then(() => {
          callback()
        });
      },
      onCancel() {
      },
    });
  };
  invoiceSearch = (data) => {
    var name = data[0].customer_name
    this.appModal.show(
      {
        title: "Search Invoices: " + name,
        url: "/invoice/search_invoice/?name="+name+"&is_model=true",
        style:{width:"90%", height:"85vh"} 
  })
  }
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
        <AppModal
          callBack={this.onModelClose}
          ref={(node) => {
            this.appModal = node;
          }}
        ></AppModal>
      </div>
    );
  }
}
export default PaymentBrowserUnmatch;
