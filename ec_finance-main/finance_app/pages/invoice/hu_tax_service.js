import AppLayout from "../../components/AppLayout";
import PageTitle from "../../components/PageTitle";
import DataForm from "../../components/DataForm";
import AppModal from "../../components/AppModal";
import React, { Component } from "react";


class huTaxService extends Component {
  user_id = this.props.session.user.data.user_id;
  state = { data: {} };
  getPageListing = (status) => {
    this.setState({ status: status });
    let default_sort_col = "id";
    let default_sort_order = "descend";
      var listing = [
        {
          search:[
            { key: "customer", label: "Customer" },
            { key: "invoice_date", label: "From invoice date" },
            { key: "status_time", label: "Till invoice date" },
            { key: "", label: "From sent date" },
            { key: "", label: "Till sent date" },
            { key: "", label: "From status date" },
            { key: "", label: "Till status date" },
            { key: "hu_status", label: "Status" },
            { key: "result", label: "Result" },
            { key: "", label: "Include Skipped Invoice" },
          ],
          pre_view:[
              {doc:'invoice',label:"Invoice",key:"invoice_number"},
              ],
          dataGridUID: "huTaxService",
          url: "/dt/sales/hu_tax_service/?status=" + status ,
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
                sequence: 1,
                width: 150,

              },
              {
                value: "customer",
                text: "Customer",
                sortable: true,
                width: 150,
              },
              {
                value: "invoice_date",
                sortable: true,
                text: "Invoice Date",
                width: 150,
              },
              {
                value: "result",
                sortable: true,
                text: "Result",
                width: 150,
              },
              {
                value: "status_time",
                text: "Till invoice date",
                width: 150,
              },
              {
                value: "created_on",
                text: "Sent date",
                width: 150,
              },
              {
                value: "hu_status",
                text: "Status",
                width: 150,
              },
              {
                value: "transaction_id",
                text: "",
                width: 150,
                show: false,
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
        dataGridUID: "huTaxService",
        name: "history",
        title: "History",
        position : "menu",
        icon_code: "HistoryOutlined",
        multi_select: false,
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows("huTaxService");
          this.appModal.show({ title: "Invoice History: "+ data[0].invoice_number, url: "/invoice/hu_tax_history/?id=" + data[0].id +"&customer="+data[0].customer + "&invoice_number=" + data[0].invoice_number +"&invoice_date=" + data[0].invoice_date + "&transaction_id=" + data[0].transaction_id,
          style:{width:"90%", height:"70vh"} });
        },
      },
      {
        dataGridUID: "huTaxService",
        name: "resubmit",
        title: "Resubmit",
        icon_code:"RedoOutlined",
      },
      {
        dataGridUID: "huTaxService",
        name: "query_invoice_data_xml",
        title: "Query invoice data XML",
        tooltip: "",
        icon_code: "ProfileOutlined"
      },

    );
    return buttons;
  };

  appSchema = {
    pageTitle: "HU- Tax service",
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
      tabs: [
        {
          UID: "tab_1",
          label: "All",
          listing: this.getPageListing("all"),
          buttons: this.getPageButtons("all"),
        },
        {
          UID: "tab_2",
          label: "Error",
          listing: this.getPageListing("error"),
          buttons: this.getPageButtons("error"),
        },
        {
          UID: "tab_3",
          label: "Warm",
          listing: this.getPageListing("warm"),
          buttons: this.getPageButtons("warm"),
        },
        {
          UID: "tab_4",
          label: "Ok",
          listing: this.getPageListing("ok"),
          buttons: this.getPageButtons("ok"),

        },
        {
          UID: "tab_5",
          label: "Not Sent",
          listing: this.getPageListing("not_sent"),
          buttons: this.getPageButtons("not_sent"),

        },
      ],
    },
  };
  refresh=()=>{
    this.dataForm.refreshTable();
  }
  onModelClose = () => {
    this.dataForm.refreshTable(this.state.status);
  };
  componentDidMount = () => {
  };
  render() {
    return (
      <div IsModel={this.props.is_model}>
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
huTaxService.getInitialProps = async (context) => {
  return { id: context.query.id??"0",customer: context.query.customer,invoice_number: context.query.invoice_number,invoice_date: context.query.invoice_date,transaction_id:context.query.transaction_id};
};
export default huTaxService;