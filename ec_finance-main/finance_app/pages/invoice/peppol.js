import AppLayout from "../../components/AppLayout";
import PageTitle from "../../components/PageTitle";
import DataForm from "../../components/DataForm";
import AppModal from "../../components/AppModal";
import axios from "axios";
import {Modal} from "antd";
import React, { Component } from "react";
const { confirm } = Modal;
class Peppol extends Component {
  state = { data: {} , status: "all" };
  getPageListing = (status) => {
    this.setState({ status: status });
    let default_sort_col = "id";
    let default_sort_order = "descend";
      var listing = [
        {
          search: [
          { key: "invoice_number", label: "Invoice" },
          { key: "created_on", label: "From invoice date" },
          { key: "invoice_due_date", label: "Till invoice date" },
          { key: "vat_no", label: "VAT" },
          { key: "customer_name", label: "Customer" },
          { key: "peppol_id", label: "PEPPOL ID" },
          { key: "", label: "From send date" },
          { key: "", label: "Till send date" },
          ],
          pre_view:[
            {doc:'invoice',label:"Invoice",key:"invoice_number"},
            {doc:'deliverynote',label:"Delivery note",key:"delivery_no"},
            {doc:this.user_id,label:"Finance report",key:"customer_id", url:"/invoice/customer_finance_report/", name:"customer"},
            {doc:this.user_id,label:"Perfomance report",key:"customer_id", url:"/invoice/perfomance_report/", name:'customer'},
          ],
          dataGridUID: status,
          url: "/dt/sales/peppol_invoice/?peppol_status="+status,
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
                text: "Invoice Nr.",
                sortable: true,
                width: 150,
                sequence: 2,
              },
              {
                value: "pe_status",
                text: "Status",
                sortable: true,
                width: 150,
                sequence: 3,
              },
              {
                value: "created_on",
                sortable: true,
                text: "Invoice Date",
                width: 150,
                sequence: 4,
              },
              {
                value: "customer",
                text: "Customer",
                sortable: true,
                width: 150,
                sequence: 5,
              },
              {
                value: "status",
                text: "Invoice status",
                sortable: true,
                width: 150,
                sequence: 6,
              },
              {
                value: "hand_comp",
                text: "Handling company",
                sortable: true,
                width: 170,
                sequence: 7,
              },
              {
                value: "",
                text: "Sent time",
                sortable: true,
                width: 150,
                sequence: 8,
              },
              {
                value: "vat_no",
                text: "VAT",
                sortable: true,
                width: 150,
                sequence: 9,
              },
              {
                value: "result",
                text: "Result",
                sortable: true,
                width: 150,
                sequence: 10,
              },
              {
                value: "error",
                text: "Error / Remarks",
                sortable: true,
                sequence: 3,
                width: 150,
                sequence: 11,
              },
              {
                value: "peppol_id_verified",
                text: "Peppol id verified",
                sortable: true,
                sequence: 12,
                width: 150,
              },
              {
                value: "",
                text: "Peppole id",
                sortable: true,
                width: 150,
                sequence: 13,
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
            dataGridUID: status,
            name : "edit_profile",
            title :"Edit profile",
            icon_code: "UserOutlined",
            position : "menu",
            multi_select: false,
            click_handler: () => {
              var data = this.dataForm.getSelectedRows(status);
              console.log(data,"lllllll");
              this.editProfile(data);
            }
          },
          {
            dataGridUID: status,
            name: "export_xls",
            title: "Export XLS",
            primary: "primary",
            position : "menu",
            icon_code: "ExportOutlined" ,
            tooltip: "",
            click_handler: () => {
              var data = this.dataForm.getDataSource(status)
              this.exportXls(data);
            }
          },
          {
            dataGridUID: status,
            name: "export_xml",
            title: "Export XML",
            primary: "primary",
            position : "menu",
            icon_code: "ExportOutlined",
            tooltip: "",
            click_handler: () => {
              var data = this.dataForm.getDataSource(status)
              this.exportXML(data);
            }
          },
          {
            dataGridUID: status,
            name: "send_peppol",
            title: "Send peppol",
            primary: "primary",
            icon_code: "CloudUploadOutlined" ,
            tooltip: "",
            // click_handler: () => {
            //   this.sendPeppol(status);
            // }
          },
          {
            dataGridUID: status,
            name: "force_send_peppol",
            title: "Force send peppol",
            primary: "primary",
            icon_code: "CloudUploadOutlined" ,
            tooltip: "",
            // click_handler: () => {
            //   this.forceSendPeppol(status);
            // }
          },
          {
            dataGridUID: status,
            name: "view_history",
            title: "History",
            primary: "primary",
            position : "menu",
            multi_select: false,
            icon_code: "HistoryOutlined",
            tooltip: "",
            click_handler: () => {
              this.setState({ status: status });
              var data = this.dataForm.getSelectedRows(status);
              console.log(data[0].created_on,"llllllllll");
              this.appModal.show({ title: "Invoice History: "+ data[0].invoice_number, url: "/invoice/peppol_history/?id=" + data[0].id + "&invoice_number=" + data[0].invoice_number +"&created_on=" + data[0].created_on + "&customer=" + data[0].customer,
              style:{width:"90%", height:"70vh"} });
            },
          },

    );
    return buttons;
  };

  appSchema = {
    pageTitle: "Peppol Invoice",
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
          label: "Ok",
          listing: this.getPageListing("ok"),
          buttons: this.getPageButtons("ok"),
        },
        {
          UID: "tab_4",
          label: "Not sent",
          listing: this.getPageListing("not"),
          buttons: this.getPageButtons("not"),
        },
      ],
    },
  };
  exportXls = (data)=>{
    console.log(data);
    var ids = ""
    for (var row in data){
      ids = ids + data[row].id +","
    }
    window.open("/dt/base/peppol_invoice_export/?invoice_id=" + ids  + "&file_type=" + "xls")
  }
  exportXML = (data)=>{
    var ids = ""
    for (var row in data){
      ids = ids + data[row].id +","
    }
    window.open("/dt/base/peppol_invoice_export/?invoice_id=" + ids  + "&file_type=" + "xml")
  }
  editProfile = (data)=>{
    var ec_customer_id = null
    if (data[0]){
      ec_customer_id = data[0].ec_customer_id
    }
    var customer_name = null
    if (data[0]){
      customer_name = data[0].customer
    }
    var post_data = {
      ec_customer_id : ec_customer_id
    }
    axios.post("/dt/customer/edit_profile/", post_data).then((response) => {
      if (response.data.code == 1) {
        console.log(response.data.data);
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
export default Peppol;