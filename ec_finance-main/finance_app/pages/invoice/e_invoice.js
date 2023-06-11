import AppLayout from "../../components/AppLayout";
import PageTitle from "../../components/PageTitle";
import DataForm from "../../components/DataForm";
import AppModal from "../../components/AppModal";
import axios from "axios";
import React, { Component } from "react";

class eInvoice extends Component {
  user_id = this.props.session.user.data.user_id;
  state = { data: {} , status: "all" , is_model:this.props.is_model};
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
            { key: "invoice_created_on", label: "From invoice date" },
            { key: "invoice_due_date", label: "Till invoice date" },
            { key: "invoice_value", label: "Invoice value" },
            { key: "root_company", label: "Root company" },
            { key: "secondry_status", label: "Secondary status" },
            { key: "address_line_1", label: "Address line1" },
            { key: "address_line_2", label: "Address line2" },
            { key: "postal_code", label: "Postal code" },
            { key: "city", label: "City" },
            { key: "phone", label: "Phone" },
            { key: "fax", label: "Fax" },
            { key: "vat_no", label: "VAT" },
            { key: "order_nrs", label: "Order nr." },
            // { key: "", label: "Packing tracking id" },
            { key: "account_number", label: "Accounting nr." },

          ],
          pre_view:[
          {doc:'deliverynote',label:"Delivery note",key:"delivery_no"},
          {doc:'invoice',label:"Invoice",key:"invoice_number"},
          ],
          dataGridUID: "eInvoice",
          url: "/dt/sales/search_invoice/?e_invoice=" +"True",
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
                value: "invoice_number",
                text: "Invoice Nr.",
                sortable: true,
                sequence: 1,
                width: 150,
              },
              {
                value: "status",
                sortable: true,
                text: "Status",
                width: 150,
              },
              {
                value: "invoice_created_on",
                sortable: true,
                text: "Invoice Date",
                width: 150,
              },
              {
                value: "last_reminder_date",
                text: "Last reminder date",
                sortable: true,
                width: 150,
              },
              {
                value: "curr_rate",
                text: "Exchange rate",
                sortable: true,
                width: 150,
              },
              {
                value: "currency_symbol",
                text: "Currency symbol",
                sortable: true,
                width: 150,
              },
              {
                value: "outstanding",
                text: "Outstanding",
                sortable: true,
                width: 150,
              },
              {
                value: "customer_outstanding",
                text: "Cust Outstanding",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "invoice_due_date",
                text: "Invoice due date",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "financial_block",
                text: "Financial blocked",
                sortable: true,
                sequence: 10,
                width: 150,
              },
              {
                value: "credit_limit",
                text: "Credit limit",
                sortable: true,
                sequence: 3,
                width: 150,
              },
               {
                value: "customer_credit_limit",
                text: "Customer Credit limit",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "customer_name",
                text: "Customer",
                sortable: true,
                width: 150,
              },
              {
                value: "payment_date",
                text: "Payment date",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "customer_type",
                text: "Customer type",
                sortable: true,
                sequence: 3,
                width: 150,
              },
               {
                value: "handling_company",
                text: "Handling company",
                sortable: true,
                sequence: 3,
                width: 150,
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
                width: 150,
              },
              {
                value: "invoice_value",
                text: "Cust invoice value",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "amount_paid",
                text: "Amount paid",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "cust_amount_paid",
                text: "Cust amount paid",
                sortable: true,
                sequence: 3,
                width: 150,
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
                sortable: false,
                sequence: 3,
                width: 150,
              },
              {
                value: "country",
                text: "Country",
                sortable: true,
                sequence: 3,
                width: 150,
              },
               {
                value: "account_number",
                text: "Accounting nr.",
                sortable: false,
                sequence: 3,
                width: 150,
              },
              {
                value: "address_line_1",
                text: "Address line 1",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "address_line_2",
                text: "Address line 2",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "postal_code",
                text: "Postal code",
                sortable: false,
                sequence: 3,
                width: 150,
              },
              {
                value: "city",
                text: "City",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "email",
                text: "Email",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "phone",
                text: "Phone",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "fax",
                text: "Fax",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "",
                text: "Match",
                sortable: true,
                sequence: 35,
                width: 110,
              },
              {
                value: "is_deliver_invoice_by_post",
                text: "Deliver invoice by post",
                sortable: true,
                sequence: 3,
                width: 150,
              },
              {
                value: "is_invoice_deliver",
                text: "Is invoice deliver",
                sortable: true,
                sequence: 3,
                width: 150,
                render:(text, record) => {
                  if (record.is_invoice_deliver == "True"){
                   return <>{"Yes"}</> ;}else{
                     return <>{"No"}</> ;
                   }
            }
              },
              {
                value: "invo_delivery",
                text: "Invoice delivery",
                sortable: false,
                sequence: 3,
                width: 150,
              },
              {
                value: "secondry_status",
                text: "Secondary status",
                sortable: true,
                sequence: 3,
                width: 150,
              },

          ],
        },
      ]
      return listing;
  };
  onModelClose = () => {
    this.dataForm.refreshTable(this.state.status);
  };
  getPageButtons = (status) => {
    var buttons = [];
    buttons.push(
      {
        dataGridUID:"eInvoice",
        name: "export_xls",
        title: "Export XLS",
        tooltip: "",
        icon_code:"ExportOutlined",
        sequence: 2,
        click_handler: () => {
            this.exportXls();
        }
      },
      {
        dataGridUID:"eInvoice",
        name : "edit_profile",
        title :"Edit profile",
        icon_code: "UserOutlined",
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows(status);
          this.editProfile(data);
        }
      },
      {
        dataGridUID:"eInvoice",
        name: "generate_invoice",
        title: "Generate e-Invoice",
        tooltip: "",
        sequence: 2,
        icon_code: "CloudServerOutlined",
        multi_select: false,
        click_handler: () => {
        var data = this.dataForm.getSelectedRows(status);
        this.generateEinvoice(data);
      }
      },
        {
        dataGridUID:"eInvoice",
        name: "e_invoice",
        title: "Generate e-Invoice (Schedule)",
        multi_select: false,
        icon_code : "CloudSyncOutlined",
        tooltip: "",
        },
    );
    return buttons;
  };
  appSchema = {
    pageTitle: "E-invoice",
    formSchema: {
      init_data: {},
      on_submit: {},
      edit_button: false,
      submit_button: false,
      hide_buttons: false,
      disabled: true,
      readonly: false,
      buttons_position: "top",
      buttons: this.getPageButtons("eInvoice"),
      listing: this.getPageListing("eInvoice"),
    },
  };
  exportXls = ()=>{
    var data = this.dataForm.getDataSource("eInvoice")
    var ids = ""
    for (var row in data){
      ids = ids + data[row].id +","
    }

    window.open("/dt/base/e_invoice_export/?invoice_id=" + ids )

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
  generateEinvoice = () =>{
    axios.post("/dt/sales/generate_e_invoice/").then((response) => {
      this.dataForm.showMessage("success", { description: "Generating digital signature 1 of 1" });
    })
  }
  refresh=()=>{
    this.dataForm.refreshTable();
  }
  componentDidMount = () => {
  };
  render() {
    return (
      <div >
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
eInvoice.getInitialProps = async (context) => {
  return { is_model: context.query.is_model??false};
};
export default eInvoice;