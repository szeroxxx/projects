import AppLayout from "../../components/AppLayout";
import PageTitle from "../../components/PageTitle";
import DataForm from "../../components/DataForm";
import AppModal from "../../components/AppModal";
import React, { Component } from "react";

class offTheSelf extends Component {
  user_id = this.props.session.user.data.user_id;
  state = { data: {} , status: "all" , is_model:this.props.is_model};
  getPageListing = (status) => {
    this.setState({ status: status });
    let default_sort_col = "id";
    let default_sort_order = "descend";
      var listing = [
        {
          search: [
            { key: "", label: "Delivery Note" },
            { key: "", label: "Customer" },
            { key: "", label: "Type" },
            { key: "", label: "Handling Company" },
            { key: "", label: "From delivery date" },
            { key: "", label: "Till delivery date" },
            { key: "", label: "Delivery country" },
            { key: "", label: "Invoice country" },
            { key: "", label: "From amount" },
            { key: "", label: "Till amount" },
          ],
          pre_view:[
          {doc:'deliverynote',label:"Delivery note",key:"delivery_no"},
          {doc:'invoice',label:"Invoice",key:"invoice_number"},
          ],
          dataGridUID: "eInvoice",
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
                value: "customer_name",
                text: "Customer",
                sortable: true,
                width: 150,
              },
              {
                value: "",
                text: "Delivery date",
                sortable: true,
                width: 150,
              },
              {
                value: "",
                text: "Delivery country",
                sortable: true,
                width: 150,
              },
              {
                value: "vat_no",
                text: "VAT",
                width: 100,
              },
              {
                value: "",
                text: "Delivery net total",
                width: 150,
              },
              {
                value: "",
                text: "Delivery transport rate",
                width: 170,
              },
              {
                value: "",
                text: "View Document",
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
        icon_code: "ExportOutlined" ,
        tooltip: "",
        sequence: 2,
      },
      {
        dataGridUID:"eInvoice",
        name: "edit_delivery",
        title: "Edit delivery",
        icon_code: "EditOutlined",
        tooltip: "",
        sequence: 2,
        multi_select: false,
      },
        {
        dataGridUID:"eInvoice",
        name: "e_invoice",
        title: "Generate invoice",
        multi_select: false,
        tooltip: "",
        icon_code:"FileAddOutlined",
        },
        {
        dataGridUID:"eInvoice",
        name: "view_history",
        title: "History",
        tooltip: "",
        sequence: 3,
        icon_code: "HistoryOutlined",
        multi_select: false,
        position : "menu",
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows(status);
          this.appModal.show({ title: "Invoice History: "+ data[0].invoice_number, url: "/invoice/invoice_history/?id=" + data[0].id ,style:{width:"90%", height:"70vh"} });
        },
      },
    );
    return buttons;
  };
  appSchema = {
    pageTitle: "OTS(off the self)",
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
offTheSelf.getInitialProps = async (context) => {
  return { is_model: context.query.is_model??false};
};
export default offTheSelf;