import React, { Component } from "react";
import AppLayout from "../../components/AppLayout";
import PageTitle from "../../components/PageTitle";
import DataForm from "../../components/DataForm";
import AppModal from "../../components/AppModal";
import axios from "axios";

class CustomerInvoice extends Component {
  state = {};
  getPageListing = (status) => {
    this.setState({ status: status });
    let default_sort_col = "id";
    let default_sort_order = "descend";
    var listing = [
      {
        search: [
          { key: "invoice_number", label: "Invoice" },
          { key: "country", label: "Country" },
          { key: "customer_name", label: "Customer" },
          { key: "hand_company", label: "Handling company" },
          { key: "invoice_created_on", label: "invoice date", searchType: "datetime", is_advanced: true },
          { key: "invoice_due_date", label: "invoice due date", searchType: "datetime", is_advanced: true },
          { key: "invoice_value", label: "Invoice value" },
          { key: "status", label: "Status" },
          { key: "root_company", label: "Root company" },
          { key: "address_line_1", label: "Address line1" },
          { key: "address_line_2", label: "Address line2" },
          { key: "postal_code", label: "Postal code" },
          { key: "city", label: "City" },
          { key: "phone", label: "Phone" },
          { key: "fax", label: "Fax" },
          { key: "vat_no", label: "VAT" },
          { key: "account_number", label: "Accounting nr." },
        ],
        pre_view: [
          { doc: this.user_id, label: "Finance report", key: "customer_id", url: "/invoice/customer_finance_report/", name: "customer_name" },
          { doc: this.user_id, label: "Perfomance report", key: "customer_id", url: "/invoice/perfomance_report/", name: "customer_name" },
        ],
        dataGridUID: "tblCustomerInvoice",
        url: "/dt/sales/search_invoice/?customer_invoice=true",
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
            value: "invoice_number",
            text: "Invoice number",
            sortable: true,
            sequence: 2,
            width: 130,
          },
          {
            value: "invoice_created_on",
            text: "Invoice date",
            sortable: true,
            sequence: 3,
            width: 120,
          },
          {
            value: "last_reminder_date",
            text: "Last rem date",
            sortable: true,
            sequence: 4,
            width: 120,
          },
          {
            value: "curr_rate",
            text: "Exchange rate",
            sortable: true,
            sequence: 5,
            width: 120,
          },
          {
            value: "currency_symbol",
            text: "Currency symbol",
            sortable: true,
            sequence: 6,
            width: 140,
          },
          {
            value: "outstanding",
            text: "Outstanding",
            sortable: true,
            sequence: 7,
            width: 120,
          },
          {
            value: "customer_outstanding",
            text: "Customer outstanding",
            sortable: true,
            sequence: 8,
            width: 180,
          },
          {
            value: "invoice_due_date",
            text: "Invoice due date",
            sortable: true,
            sequence: 9,
            width: 140,
          },
          {
            value: "financial_block",
            text: "Financial blocked",
            sortable: true,
            sequence: 10,
            width: 150,
            render: (text, record, index) => {
              if (record.financial_block == "False") {
                return "No"
              }else{
                return "Yes"
              }
            }
          },
          {
            value: "credit_limit",
            text: "Credit limit",
            sortable: true,
            sequence: 11,
            width: 110,
          },
          {
            value: "customer_credit_limit",
            text: "Customer credit limit",
            sortable: true,
            sequence: 12,
            width: 170,
          },
          {
            value: "customer_name",
            text: "Customer",
            sortable: true,
            sequence: 13,
            width: 110,
          },
          {
            value: "payment_date",
            text: "Payment date",
            sortable: true,
            sequence: 14,
            width: 120,
          },
          {
            value: "customer_type",
            text: "Customer type",
            sortable: true,
            sequence: 15,
            width: 130,
          },
          {
            value: "handling_company",
            text: "Handling company",
            sortable: true,
            sequence: 16,
            width: 100,
          },
          {
            value: "is_root",
            text: "Root company",
            sortable: true,
            sequence: 17,
            width: 130,
          },
          {
            value: "invoice_value",
            text: "Invoice value",
            sortable: true,
            sequence: 18,
            width: 120,
          },
          {
            value: "invoice_value",
            text: "Customer invoice value",
            sortable: true,
            sequence: 19,
            width: 180,
          },
          {
            value: "status",
            text: "Status",
            sortable: true,
            sequence: 20,
            width: 110,
          },
          {
            value: "",
            text: "Recent id",
            sortable: true,
            sequence: 21,
            width: 110,
          },
          {
            value: "amount_paid",
            text: "Amount paid",
            sortable: true,
            sequence: 22,
            width: 120,
          },
          {
            value: "cust_amount_paid",
            text: "Customer amount paid",
            sortable: true,
            sequence: 23,
            width: 180,
          },
          {
            value: "delivery_no",
            text: "Delivery nr",
            sortable: true,
            sequence: 24,
            width: 110,
          },
          {
            value: "vat_no",
            text: "VAT",
            sortable: true,
            sequence: 25,
            width: 110,
          },
          {
            value: "country",
            text: "Country",
            sortable: true,
            sequence: 26,
            width: 110,
          },
          {
            value: "account_number",
            text: "Accounting no",
            sortable: true,
            sequence: 27,
            width: 130,
          },
          {
            value: "address_line_1",
            text: "Address line 1",
            sortable: true,
            sequence: 28,
            width: 130,
          },

          {
            value: "address_line_2",
            text: "Address line 2",
            sortable: true,
            sequence: 29,
            width: 130,
          },
          {
            value: "postal_code",
            text: "Postal code",
            sortable: true,
            sequence: 30,
            width: 110,
          },
          {
            value: "city",
            text: "City",
            sortable: true,
            sequence: 31,
            width: 110,
          },
          {
            value: "email",
            text: "Email",
            sortable: true,
            sequence: 32,
            width: 110,
          },
          {
            value: "phone",
            text: "Phone",
            sortable: true,
            sequence: 33,
            width: 110,
          },
          {
            value: "fax",
            text: "Fax",
            sortable: true,
            sequence: 34,
            width: 110,
          },
          {
            value: "",
            text: "Match",
            sortable: true,
            sequence: 35,
            width: 110,
          },
          {
            value: "",
            text: "Payment id",
            sortable: true,
            sequence: 36,
            width: 110,
          },
          {
            value: "",
            text: "Payment status",
            sortable: true,
            sequence: 37,
            width: 130,
          },
          {
            value: "is_deliver_invoice_by_post",
            text: "Delivery by post",
            sortable: true,
            sequence: 38,
            width: 140,
          },
          {
            value: "is_invoice_deliver",
            text: "Is invoice deliver",
            sortable: true,
            sequence: 39,
            width: 140,
            render:(text, record) => {
               return <>{"No"}</> ;
            }
          },
          {
            value: "secondry_status",
            text: "Secondary status",
            sortable: true,
            sequence: 40,
            width: 140,
          },
          {
            value: "invo_delivery",
            text: "Invoice delivery",
            sortable: true,
            sequence: 41,
            width: 140,
          },
        ],
      },
    ];
    return listing;
  };
  getPageButtons = (status) => {
    var buttons = [];
    buttons.push(
      {
        dataGridUID: "tblCustomerInvoice",
        name: "export_xls",
        title: "Export XLS",
        primary: "primary",
        position: "menu",
        icon_code: "ExportOutlined",
        tooltip: "",
        click_handler: () => {
          this.exportXls("tblCustomerInvoice");
        },
      },
      {
        dataGridUID: "tblCustomerInvoice",
        name: "edit_profile",
        title: "Edit profile",
        icon_code: "UserOutlined",
        position: "menu",
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows("tblCustomerInvoice");
          this.editProfile(data);
        },
      },
      {
        dataGridUID: "tblCustomerInvoice",
        name: "download_for_print",
        title: "Download for print",
        primary: "primary",
        icon_code: "DownloadOutlined",
        tooltip: "",
        multi_select: false,
      },
      {
        dataGridUID: "tblCustomerInvoice",
        name: "veiw_detail",
        title: "Download merged invoice PDF",
        primary: "primary",
        icon_code: "FilePdfOutlined",
        tooltip: "",
        multi_select: false,
      },
      {
        dataGridUID: "tblCustomerInvoice",
        name: "",
        title: "Download merged invoice + delivery PDF",
        primary: "primary",
        icon_code: "FilePdfOutlined",
        tooltip: "",
        multi_select: false,
      }
    );
    return buttons;
  };
  appSchema = {
    pageTitle: "Customer invoice",
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
  exportXls = () => {
    var data = this.dataForm.getDataSource("tblCustomerInvoice");
    var ids = "";
    for (var row in data) {
      ids = ids + data[row].id + ",";
    }
    window.open("/dt/base/customer_invoice_export/?invoice_id=" + ids);
  };
  editProfile = (data) => {
    var ec_customer_id = null;
    if (data[0]) {
      ec_customer_id = data[0].ec_customer_id;
    }
    var customer_name = null;
    if (data[0]) {
      customer_name = data[0].customer_name;
    }
    var post_data = {
      ec_customer_id: ec_customer_id,
    };
    axios.post("/dt/customer/edit_profile/", post_data).then((response) => {
      if (response.data.code == 1) {
        this.appModal.show({
          url: response.data.data,
          title: "Edit Profile :" + " " + customer_name,
          style: { width: "90%", height: "85vh" },
        });
        return;
      }
    });
  };
  render() {
    return (
      <div>
        <PageTitle pageTitle={this.appSchema.pageTitle}></PageTitle>
        <DataForm
          style={{ width: "100%" }}
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
export default CustomerInvoice;
