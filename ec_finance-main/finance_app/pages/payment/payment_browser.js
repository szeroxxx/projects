import AppLayout from "../../components/AppLayout";
import PageTitle from "../../components/PageTitle";
import AppModal from "../../components/AppModal";
import DataForm from "../../components/DataForm";
import React, { Component } from "react";
import axios from "axios";

const { confirm } = Modal;
import {Modal } from "antd";
class PaymentBrowser extends Component {
  
  state = { data: {} };
  getPageListing = (status) => {
    this.setState({ status: status });
    let default_sort_col = "id";
    let default_sort_order = "descend";
    var listing = [
      {
        search: [
          { key: "invoice_no", label: "Invoice Nr." },
          { key: "customer_name", label: "Customer" },
          { key: "created_on", label: "Payment From date" },
          { key: "payment_to_date", label: "Payment To date" },
          { key: "invoice_value", label: "Invoice amount" },
          { key: "payment_mode", label: "Payment mode" },
          { key: "payment_id", label: "Payment Id" },
          { key: "country_name", label: "Country" },
          { key: "bank_name", label: "Bank name" },
          { key: "source", label: "Source" },
        ],
        dataGridUID: "tblPaymentBrowser",
        url: "/dt/payment/payment_browser/?ids="+this.state.id,  
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
            value: "ec_customer_id",
            text: "ec customer id",
            show: false,
            row_key: true,
            sequence: 2,
          },
          {
            value: "invoice_no",
            text: "Invoice Nr.",
            sortable: true,
            width: 100,
            sequence: 3,
          },
          {
            value: "customer_name",
            text: "Customer name",
            sortable: true,
            width: 135,
            sequence: 4,
          },
          {
            value: "payment_date",
            text: "Payment date",
            sortable: true,
            width: 120, 
            sequence: 5,
          },
          {
            value: "payment_mode",
            text: "Payment mode",
            sortable: true,
            width: 130,
            sequence: 6,
          },
          {
            value: "invoice_status",
            text: "Invoice status",
            sortable: true,
            width: 120,
            sequence: 7,
          },
          {
            value: "payment_id",
            text: "Payment Id",
            sortable: true,
            width: 110,
            sequence: 8,
          },
          {
            value: "close_by",
            text: "Closed by",
            sortable: true,
            width: 100,
            sequence: 9,
          },
          {
            value: "close_on",
            text: "Closed on",
            sortable: true,
            width: 100,
            sequence: 10,
          },
          {
            value: "invoice_value",
            text: "Invoice amount",
            sortable: true,
            width: 130,
            sequence: 11,
          },
          {
            value: "amount",
            text: "Payment amount",
            sortable: true,
            width: 140,
            sequence: 12,
          },
          {
            value: "currency_symbol",
            text: "Currency symbol",
            sortable: true,
            width: 140,
            sequence: 13,
          },
          {
            value: "bank_account_no",
            text: "Bank account Nr.",
            sortable: true,
            width: 140,
            sequence: 14,
          },
          {
            value: "bank_name",
            text: "Bank name",
            sortable: true,
            width: 110,
            sequence: 15,
          },
          {
            value: "country",
            text: "Country",
            sortable: true,
            width: 100,
            sequence: 16,
          },
          {
            value: "source",
            text: "Source",
            sortable: true,
            width: 100,
            sequence: 17,
          },
          {
            value: "invoice_id",
            text: "invoice id",
            sortable: true,
            show: false,
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
        dataGridUID: "tblPaymentBrowser",
        name: "history",
        title: "History",
        position : "menu",
        tooltip: "",
        sequence: 1,
        class:"mr-left",
        icon_code:"HistoryOutlined",
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows("tblPaymentBrowser");
          this.appModal.show({ 
            title: "History: "+ data[0].invoice_no,
            url: "/invoice/invoice_history/?invoice_id=" + data[0].invoice_id,
            style:{width:"90%", height:"70vh"} });
        },
      },
      {
        dataGridUID: "tblPaymentBrowser",
        name: "edit_profile",
        title: "Edit profile",
        icon_code: "UserOutlined",
        primary: "primary",
        tooltip: "",
        sequence: 2,
        class:"mr-left",
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows("tblPaymentBrowser");
          this.editProfile(data);
        }
      },
      {
        dataGridUID: "tblPaymentBrowser",
        name: "customer_login",
        title: "Customer login",
        icon_code: "UserSwitchOutlined",
        primary: "primary",
        tooltip: "",
        sequence: 3,
        class:"mr-left",
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows("tblPaymentBrowser");
          this.customerLogin(data);
        }
      },
      {
        dataGridUID: "tblPaymentBrowser",
        name: "export_xls",
        title: "Export XLS",
        icon_code: "ExportOutlined",
        position : "menu",
        tooltip: "",
        sequence: 4,
        type:"primary",
        class:"mr-left",
        click_handler: () => {
          this.exportXls();
        } 
      },
    )
    return buttons;

  };

  appSchema = {
    pageTitle: "Payment Browser",
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
      listing: this.getPageListing("tblPaymentBrowser"),
      buttons: this.getPageButtons("tblPaymentBrowser"),
    },
  };
  componentDidMount = () => {
   
  };
  exportXls = ()=>{
    var data = this.dataForm.getDataSource("tblPaymentBrowser")
    var ids = ""
    for (var row in data){
      ids = ids + data[row].id +"," 
    }
   
    window.open("/dt/base/payment_browser_export/?coda_transaction_id=" + ids )

  }
  customerLogin = (data) => {
    var ec_customer_id = null
    if (data[0]){
      ec_customer_id = data[0].ec_customer_id
    }
    axios.post("/dt/customer/customer_login/", {ec_customer_id : ec_customer_id}).then((response) => {
      if(response.data.code == 1){
      
        window.open(response.data.data.url)
      }
    });
  }
  editProfile = (data)=>{
    var ec_customer_id = null
    if (data[0]){
      ec_customer_id = data[0].ec_customer_id
    }
    var customer_name = null
    if (data[0]){
      customer_name = data[0].customer_name
    }
    var post_data = {
      ec_customer_id : ec_customer_id
    }
    axios.post("/dt/customer/edit_profile/", post_data).then((response) => {
      if (response.data.code == 1) {
         this.appModal.show(
              {
                url: response.data.data,
                title:"Edit Profile :" + " "+ customer_name, 
                style:{width:"90%", height:"85vh"} 
          });
        return;
      }
    });
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
export default PaymentBrowser;
