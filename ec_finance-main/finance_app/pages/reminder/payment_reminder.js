import DataGridViewer from "../../components/DataGridViewer";


import AppLayout from "../../components/AppLayout";
import PageTitle from "../../components/PageTitle";
import ActionPanel from "../../components/ActionPanel";
import EmailPreview from "../../components/EmailPreview";
import AppModal from "../../components/AppModal";
import SearchInput from "../../components/SelectInput";
import AppIcons from "../../components/AppIcons";
import React, { Component } from "react";
import {Row, Col,  Form, Select, Button,Checkbox} from "antd";
import axios from "axios";
class PaymentReminder extends Component {
  state = { data: {} ,handling_company:[],render: false};
  paymentReminderAppSchema = {
    pageTitle: "Payment Reminder",
    buttons: [
      {
        name: "send_reminder",
        title: "Send reminder",
        primary: "primary",
        tooltip: "",
        sequence: 1,
        class:"mr-left",
        confirm: {
          title: "are you sure you want to continue?",
          content: <>Invoice payment reminder will be scheduled</>,
          okText: "Yes, Send ",
          cancelText: "No, Cancel",
          onOk: () => {
            var data = this.countryGridViewer.getSelectedRows()
            this.createScheduler(data)
          },
        },
        // click_handler: () => {
        //   var data = this.countryGridViewer.getSelectedRows();
        //   this.sendReminder(data);
        // }
        // multi_select: false,
      },
      {
        name: "edit_profile",
        title: "Edit profile",
        tooltip: "",
        sequence: 1,
        icon_code: "UserOutlined",
        class:"mr-left",
        click_handler: () => {
          var data = this.customerGridViewer.getSelectedRows();
          this.editProfile(data);
        }
        // multi_select: false,
      },
      {
        name: "reminder_preview",
        title: "Reminder preview",
        icon_code: "FileTextOutlined",
        tooltip: "",
        sequence: 1,
        class:"mr-left",
        // multi_select: false,
        click_handler: (data) => {
          var data = this.customerGridViewer.getSelectedRows();
          if (data[0]){
          this.emailTemplate(data[0].customer_id)
          }
        },
      },
    ],
    listing: [
      {
        dataGridUID: "countryBreakup",
        url: "/dt/sales/country_breakup/",
        paging: true,
        default_sort_col: "country_id",
        default_sort_order: "descend",
        row_selection: true,
        bind_on_load: false,
        // onRow:(record, rowIndex) => {
        //   return {
        //     onClick: event => {
        //       this.customerGridViewer.searchData({country_id:['text',record.country_id]})
        //     },
        //   };
        // },
        columns: [
          {
            value: "country_id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "country_name",
            text: "Country name",
            sortable: true,
            width: 200,
            sequence: 2,
          },
          {
            value: "zero_days_amount",
            text: "0 Days amount",
            sortable: true,
            width: 200,
            sequence: 3,
          },
          {
            value: "zero_days_invoice",
            text: "0 Days invoice",
            sortable: true,
            width: 200,
          },
          {
            value: "l_ten_days_amount",
            sortable: true,
            text: "Due <10 Days amount",
            width: 200,
          },
          {
            value: "l_ten_days_invoice",
            sortable: true,
            text: "Due <10 Days invoice",
            width: 200,
          },
          {
            value: "l_thirty_days_amount",
            sortable: true,
            text: "Due <30 Days amount",
            width: 200,
          },
          {
            value: "l_thirty_days_invoice",
            sortable: true,
            text: "Due <30 Days invoice",
            width: 200,
          },
          {
            value: "l_sixty_days_amount",
            sortable: true,
            text: "Due <60 Days amount",
            width: 200,
          },
          {
            value: "l_sixty_days_invoice",
            sortable: true,
            text: "Due <60 Days invoice",
            width: 200,
          },
          {
            value: "l_ninety_days_amount",
            sortable: true,
            text: "Due <90 Days amount",
            width: 200,
          },
          {
            value: "l_ninety_days_invoice",
            sortable: true,
            text: "Due <90 Days invoice",
            width: 200,
          },
          {
            value: "g_ninety_days_amount",
            sortable: true,
            text: "Due >90 Days amount",
            width: 200,
          },
          {
            value: "g_ninety_days_invoice",
            sortable: true,
            text: "Due >90 Days invoice",
            width: 200,
          },
        ],
      },

      {
        dataGridUID: "customerBreakup",
        url: "/dt/sales/customer_breakup/",
        paging: true,
        default_sort_col: "customer_id",
        default_sort_order: "descend",
        row_selection: true,
        bind_on_load: false,
        onRow:(record, rowIndex) => {
          return {
            onClick: event => {
              this.invoiceGridViewer.searchData({customer_id:['text',record.customer_id]})
            },
          };
        },
        columns: [
          {
            value: "customer_id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "company_name",
            text: "Company name",
            sortable: true,
            width: 200,
            sequence: 2,
          },
          {
            value: "email",
            text: "Email",
            sortable: true,
            width: 200,
            sequence: 2,
          },

          {
            value: "last_rem_date",
            text: "Reminder date",
            sortable: true,
            sequence: 3,
            width: 200,
          },
          {
            value: "language_code",
            text: "Language code",
            sortable: true,
            width: 200,
          },
          {
            value: "username",
            text: "Contact person",
            sortable: true,
            width: 200,
          },
          {
            value: "zero_days_amount",
            sortable: true,
            text: "0 Days amount",
            width: 200,
          },
          {
            value: "zero_days_invoice",
            sortable: true,
            text: "0 Days invoice",
            width: 200,
          },
          {
            value: "l_ten_days_amount",
            sortable: true,
            text: "Due <10 Days amount",
            width: 200,
          },
          {
            value: "l_ten_days_invoice",
            sortable: true,
            text: "Due <10 Days invoice",
            width: 200,
          },
          {
            value: "l_thirty_days_amount",
            sortable: true,
            text: "Due <30 Days amount",
            width: 200,
          },
          {
            value: "l_thirty_days_invoice",
            sortable: true,
            text: "Due <30 Days invoice",
            width: 200,
          },
          {
            value: "l_sixty_days_amount",
            sortable: true,
            text: "Due <60 Days amount",
            width: 200,
          },
          {
            value: "l_sixty_days_invoice",
            sortable: true,
            text: "Due <60 Days amount",
            width: 200,
          },
          {
            value: "l_ninety_days_amount",
            sortable: true,
            text: "Due <90 Days amount",
            width: 200,
          },
          {
            value: "l_ninety_days_invoice",
            sortable: true,
            text: "Due <90 Days invoice",
            width: 200,
          },
          {
            value: "g_ninety_days_amount",
            sortable: true,
            text: "Due >90 Days amount",
            width: 200,
          },
          {
            value: "g_ninety_days_invoice",
            sortable: true,
            text: "Due >90 Days invoice",
            width: 200,
          },
        ],
      },
      {
        dataGridUID: "invoiceBreakup",
        url: "/dt/sales/invoice_breakup/",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: true,
        bind_on_load: false,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "type",
            text: "Type",
            sortable: true,
            width: 200,
            sequence: 2,
          },
          {
            value: "type",
            text: "Reminder",
            sortable: true,
            width: 200,
            sequence: 2,
          },
          {
            value: "type",
            text: "Reminder status",
            sortable: true,
            width: 200,
            sequence: 2,
          },
          {
            value: "last_rem_date",
            text: "Reminder date",
            sortable: true,
            width: 200,
            sequence: 2,
          },

          {
            value: "invoice_number",
            text: "Invoice Nr.",
            sortable: true,
            width: 200,
            sequence: 2,
          },
          {
            value: "invoice_created_on",
            text: "Invoice date",
            sortable: true,
            width: 200,
            sequence: 2,
          },
          {
            value: "outstanding_amount",
            text: "Outstanding amount",
            sortable: true,
            sequence: 3,
            width: 200,
          },
          {
            value: "currency_outstanding_amount",
            text: "Currency Outstanding amount",
            sortable: true,
            width: 200,
          },
          {
            value: "outstanding_days",
            sortable: true,
            text: "Outstanding Days",
            width: 200,
          },
          {
            value: "invoice_due_date",
            sortable: true,
            text: "Invoice due date",
            width: 200,
          },
          {
            value: "invoice_value",
            sortable: true,
            text: "Invoice amount",
            width: 200,
          },
          {
            value: "currency_outstanding_amount",
            sortable: true,
            text: "Currency invoice amount",
            width: 200,
          },
          {
            value: "amount_paid",
            sortable: true,
            text: "Amount paid",
            width: 200,
          },
          {
            value: "amount_paid",
            sortable: true,
            text: "Currency amount paid",
            width: 200,
          },
          {
            value: "",
            sortable: true,
            text: "Paid on",
            width: 200,
          },
          {
            value: "order_nrs",
            sortable: true,
            text: "Order-Nr(s)",
            width: 200,
          },
          {
            value: "currency_symbol",
            sortable: true,
            text: "Currency symbol",
            width: 200,
          },
        ],
      },
    ],

  };
  handleChange = (hand_company_id)=>{
    this.setState({hand_company_id})
}
editProfile = (data)=>{
  var ec_customer_id = null
  if (data[0]){
    ec_customer_id = data[0].ec_customer_id
  }
  var post_data = {
    ec_customer_id : ec_customer_id
  }
  console.log(post_data)
  axios.post("/dt/customer/edit_profile/", post_data).then((response) => {
    if (response.data.code == 1) {
       this.appModal.show(
            {
              url: response.data.data,
              title:"Edit Profile",
              style:{width:"90%", height:"85vh"}
        });
      return;
    }
  });

}

sendReminder = (data)=>{
  var customerData = this.customerGridViewer.getSelectedRows();
  console.log(customerData);
  var invoiceData = this.invoiceGridViewer.getSelectedRows();

  var country_id = null
  if (data[0]){
    country_id = data[0].country_id
  }
  var ec_customer_id = null
  var email = null
  if (customerData[0]){
    ec_customer_id = customerData[0].ec_customer_id,
    email = customerData[0].email
  }
  var invoice_number = null
  var invoice_id = null
  var status = null
  if (invoiceData[0]){
    invoice_id = invoiceData[0].invoice_id,
    invoice_number = invoiceData[0].invoice_number
    status = invoiceData[0].status
  }
  var post_data=  {
      company_id: this.state.hand_company_id,
      country_id: country_id,
      ec_customer_id: ec_customer_id,
      invoice_id: invoice_id ,
      email: email,
      invoice_number:invoice_number,
      status : status
  }
  console.log(post_data);

  axios.post("/dt/sales/send_reminder/", post_data).then((response) => {
    if (response.data.code == 0) {
      // this.dataForm.showMessage("error", { message: "Failed!", description: response.data.message });
      return;
    }
    // this.dataForm.showMessage("success", { message: "Success!", description: response.data.message });
    // this.dataForm.refreshTable(gridID);
  });
}
loadCustomerBreakup = ()=>{
  const hand_company_id = this.state.hand_company_id
  this.countryGridViewer.searchData({company_id:['text',hand_company_id]})
}
  emailTemplate = (customer_id) => {
    this.setState({render : !this.state.render,customer_id:customer_id,hand_company_id:this.state.hand_company_id})
  }
  componentDidMount = () => {
  };
  onChangeIncludeInvoicePDF =(e) => {
    console.log('onChangeIncludeInvoicePDF',e.target.checked);
  }
  countrySelectionChange = (key, selectedRows) => {
    let row = selectedRows[0]
    if (row){
      this.customerGridViewer.searchData({country_id:['text' , row.country_id]})
    }
  };
  render() {
    return (
      <div>
        <PageTitle pageTitle={this.paymentReminderAppSchema.pageTitle}></PageTitle>
        <Row>
        <Col span={24}>
        <Form.Item label="Handling Company" className="collection-input">
        <SearchInput  handleChange={this.handleChange}  fieldProps={{mode:"single",datasource:{query:"/dt/base/lookups/hand_company/"}}} style={{width:300}}></SearchInput>
        <Button style={{marginLeft:8}}
        onClick={this.loadCustomerBreakup}
        type="primary" icon={<AppIcons code={"ReloadOutlined"}/>}
         >Load</Button>
      </Form.Item>
      </Col>
      </Row>

        <b><h3 style={{marginTop:10}}>Country breakup</h3></b>
        <DataGridViewer
          schema={this.paymentReminderAppSchema.listing[0]}
          onRowSelectionChange={this.countrySelectionChange}
          ref={(node) => {
            this.countryGridViewer = node;
          }}
        >
        </DataGridViewer>
        <b><h3>Customer breakup</h3></b>
       <DataGridViewer
          schema={this.paymentReminderAppSchema.listing[1]}
          ref={(node) => {
            this.customerGridViewer = node;
          }}
        >
        </DataGridViewer>
        <b><h3>Customer invoice breakup</h3></b>
        <DataGridViewer
          schema={this.paymentReminderAppSchema.listing[2]}
          // onRowSelectionChange={this.rowSelectionChange}
          ref={(node) => {
            this.invoiceGridViewer = node;
          }}
        >
        </DataGridViewer>
        <Row style={{marginBottom:10,marginTop:10}}>
        <Col md={12}>
        <Checkbox onChange={this.onChangeIncludeInvoicePDF}>Include Invoice PDF</Checkbox>
        </Col>
        <Col md={12} >
        <ActionPanel buttons={this.paymentReminderAppSchema.buttons} selectedRows={this.state.data[this.paymentReminderAppSchema.listing[0].dataGridUID]}/>

        </Col>
        </Row>
        { this.state.render &&
        <EmailPreview
          customer={this.state.customer_id}
          hand_company={this.state.hand_company_id}

        >

        </EmailPreview>
        }
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

export default PaymentReminder;
