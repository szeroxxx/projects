import { Button, Col, Form, Input, InputNumber, Modal, Radio, Row } from "antd";
import axios from "axios";
import React, { Component } from "react";
import { FinMessage, showMessage } from "../../common/Util";
import AppModal from "../../components/AppModal";
import DataForm from "../../components/DataForm";
import PageTitle from "../../components/PageTitle";
import SearchInput from "../../components/SelectInput";

const { confirm } = Modal;
const plainOptions = [
  { label: "From invoice date", value: 1 },
  { label: "First day of the month following invoice due date", value: 2 },
];
class SearchInvoice extends Component {
  user_id = this.props.session.user.data.user_id;
  state = { data: {}, status: "pending", is_model: this.props.is_model };
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
          { key: "packing", label: "Payment tracking id" },
          { key: "account_number", label: "Accounting nr." },
        ],
        pre_view: [
          { doc: "invoice", label: "Invoice", key: "invoice_number" },
          { doc: "deliverynote", label: "Delivery note", key: "delivery_no" },
          {
            doc: this.user_id,
            label: "Finance report",
            key: "customer_id",
            url: "/invoice/customer_finance_report/",
            name: "customer_name",
            ec: "ec_customer_id",
          },
          { doc: this.user_id, label: "Perfomance report", key: "ec_customer_id", url: "/invoice/perfomance_report/", name: "customer_name" },
          {
            doc: this.user_id,
            ec: "ec_customer_id",
            key: "customer_id",
            label: "Credit status",
            url: "/invoice/credit_status/",
            name: "customer_name",

          },
        ],
        dataGridUID: status,
        url: "/dt/sales/search_invoice/?status=" + status + "&is_model=true" + "&name=" + this.props.name,
        paging: true,
        default_sort_col: default_sort_col,
        default_sort_order: default_sort_order,
        row_selection: true,
        bind_on_load: true,
        gridViewer: this.props.isModal ? true : undefined,
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
            searchable: true,
            type: "datetime",
          },
          {
            value: "customer_name",
            text: "Customer",
            sortable: true,
            width: 150,
          },
          {
            value: "invoice_value",
            text: "Invoice value",
            sortable: true,
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
            sequence: 3,
            width: 150,
            render: (text,record,index) => {
              if (record.financial_block == 'False') {
                return "No"
              }else{
                return "Yes"
              }
            }
          },
          {
            value: "payment_date",
            text: "Payment date",
            sortable: true,
            sequence: 3,
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
            sequence: 3,
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
            text: "Delivery nr.",
            sortable: true,
            sequence: 3,
            width: 150,
          },
          {
            value: "vat_no",
            text: "VAT",
            sortable: true,
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
            sortable: true,
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
            value: "packing",
            text: "Payment Id",
            sortable: true,
            sequence: 3,
            width: 150,
          },
          {
            value: "is_finished",
            text: "Payment status",
            sortable: true,
            sequence: 3,
            width: 150,
            render:(text,record,index) => {
            if (record.is_finished == "False"){
              return "Unpaid"
            }else{
              return "Paid"
              }
            }
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
            render: (text,record,index) => {
              if (record.is_invoice_deliver == 'False') {
                return "No"
              }else{
                return "Yes"
              }
            }
          },
          {
            value: "invo_delivery",
            text: "Invoice delivery",
            sortable: true,
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
          {
            value: "account_number",
            text: "Accounting nr.",
            sortable: true,
            sequence: 3,
            width: 150,
          },
        ],
      },
    ];
    return listing;
  };
  onModelClose = () => {
    this.dataForm.refreshTable(this.state.status);
  };
  getPageButtons = (status) => {
    var buttons = [];
    buttons.push(
      {
        name: "grant-days",
        title: "Grant days",
        sequence: 1,
        icon_code: "ScheduleOutlined",
        position: "menu",
        multi_select: false,
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows(status);
          this.setState({ isGrantModalVisible: true });
          this.setState({ invoice_due_date: data[0].invoice_due_date });
          this.setState({ invoice_number: data[0].invoice_number });
          this.setState({ invoice_id: data[0].id });
        },
      },
      {
        name: "close_invoice",
        title: "Close Invoice",
        tooltip: "",
        sequence: 2,
        multi_select: true,
        icon_code: "FileDoneOutlined",
        click_handler: () => {
          var data = this.dataForm.getSelectedRows(status);
          var customers = [];
          for (let i in data) {
            customers.push(data[i].customer_id);
          }
          const is_same_customer = (arr) => arr.every((val, i, arr) => val === arr[0]);
          if (is_same_customer(customers) == false) {
            showMessage("Not allowed.", "Select invoices for one customer at a time", "error");
            return;
          }
          if (data[0].status == "Closed") {
            confirm({
              title: "This invoice" + " " + data[0].invoice_number + " " + "is already closed ",
              icon: <></>,
              content: <>Are you sure you want to close it again ?</>,
              cancelText: "No, Cancel",
              okText: "Yes, Close",
              onOk: () => {
                this.setState({ status: status });
                this.closeInvoice(data);
              },
              onCancel() {},
            });
          } else {
            this.setState({ status: status });
            var data = this.dataForm.getSelectedRows(status);
            this.closeInvoice(data);
          }
        },
      },
      {
        name: "edit_invoice",
        title: "Edit Invoice",
        tooltip: "",
        sequence: 2,
        multi_select: false,
        icon_code: "EditOutlined",
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows(status);
          this.editInvoice(data);
        },
      },
      {
        name: "view_history",
        title: "History",
        tooltip: "",
        sequence: 3,
        icon_code: "HistoryOutlined",
        multi_select: false,
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows(status);
          this.appModal.show({
            title: "Invoice History: " + data[0].invoice_number,
            url: "/invoice/invoice_history/?id=" + data[0].id,
            style: { width: "90%", height: "70vh" },
          });
        },
      },
      {
        name: "customer_login",
        title: "Customer Login",
        multi_select: false,
        tooltip: "",
        position: "menu",
        icon_code: "UserSwitchOutlined",
        sequence: 3,
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows(status);
          this.customerLogin(data);
        },
      },
      {
        name: "secondary_status",
        title: "Change secondary status",
        icon_code: "RetweetOutlined",
        position: "menu",
        multi_select: true,
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows(status);
          if (data.length == 0) {
            showMessage("Select one.", "Please select Record", "error");
          } else {
            this.setState({ invoice_number: data[0].invoice_number });
            this.setState({ invoice_id: data[0].id });
            this.setState({ isModalVisible: true });
          }
        },
      },
      {
        name: "change_status",
        title: "Change status",
        icon_code: "RetweetOutlined",
        multi_select: true,
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows(status);
          if (data.length == 0) {
            showMessage("Select one.", "Please select Record", "error");
          } else {
            this.setState({ invoice_number: data[0].invoice_number });
            this.setState({ invoice_id: data[0].id });
            this.setState({ isChangeModalVisible: true });
          }
        },
      },
      {
        name: "edit_profile",
        title: "Edit profile",
        icon_code: "UserOutlined",
        multi_select: false,
        click_handler: () => {
          var data = this.dataForm.getSelectedRows(status);
          this.editProfile(data);
        },
      },
      {
        name: "credit_limit",
        title: "Credit limit",
        position: "menu",
        icon_code: "EuroCircleOutlined",
        multi_select: false,
        click_handler: () => {
          this.setState({ status: status });
          this.setState({ isCreditLimitModalVisible: true });
          var data = this.dataForm.getSelectedRows(status);

          // this.setState({credit_limit:data[0].credit_limit})
          // this.setState({customer_credit_limit:data[0].customer_credit_limit})
          this.creditLimit(data);
        },
      },
      {
        name: "credit_status",
        title: "Credit status",
        icon_code: "EuroCircleOutlined",
        multi_select: false,
        position: "menu",
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows(status);
          if (data.length == 0) {
            showMessage("Select one.", "Please select Record", "error");
          } else {
            this.setState({ customer_id: data[0].customer_id });
            this.appModal.show({
              title: "Credit Status ",
              url:
                "/invoice/credit_status/?customer_id=" +
                data[0].customer_id +
                "&creditlimit=" +
                data[0].credit_limit +
                "&customercreditlimit=" +
                data[0].customer_credit_limit +
                "&cust_outstanding=" +
                data[0].customer_outstanding +
                "&ec_customer_id=" +
                data[0].ec_customer_id +
                "&invoice_id=" +
                data[0].id,
              style: { width: "90%", height: "70vh" },
            });
          }
        },
      },
      {
        name: "credit_on_invoice",
        title: "Credit on invoice",
        icon_code: "FileDoneOutlined",
        multi_select: false,
        position: "menu",
        click_handler: () => {
          this.setState({ status: status });
          var data = this.dataForm.getSelectedRows(status);
          this.creditOnInvoice(data);
        },
      },
      {
        name: "export_csv",
        title: "Export CSV",
        icon_code: "ExportOutlined",
        position: "menu",
        click_handler: () => {
          var data = this.dataForm.getDataSource(status);
          this.exportCSV(data);
        },
      },
      {
        name: "export_xls",
        title: "Export XLS",
        icon_code: "ExportOutlined",
        position: "menu",
        click_handler: () => {
          var data = this.dataForm.getDataSource(status);
          this.exportXls(data);
        },
      },
      {
        name: "export_xml",
        title: "Export XML",
        icon_code: "ExportOutlined",
        position: "menu",
        click_handler: () => {
          var data = this.dataForm.getDataSource(status);
          this.exportXML(data);
        },
      }
    );
    return buttons;
  };

  appSchema = {
    pageTitle: "Search invoice",
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
          label: "Pending",
          listing: this.getPageListing("pending"),
          buttons: this.getPageButtons("pending"),
          fields: [
            {
              input_type: "custom",
              name: "text",
              value: "pending",
              component_path: "./invoice/SearchPanel",
            },
          ],
        },
        {
          UID: "tab_2",
          label: "Overdue",
          listing: this.getPageListing("overdue"),
          buttons: this.getPageButtons("overdue"),
          fields: [
            {
              input_type: "custom",
              name: "text",
              value: "overdue",
              component_path: "./invoice/SearchPanel",
            },
          ],
        },
        {
          UID: "tab_3",
          label: "Paid/Closed",
          listing: this.getPageListing("closed"),
          buttons: this.getPageButtons("closed"),

          fields: [
            {
              input_type: "custom",
              name: "text",
              value: "closed",
              component_path: "./invoice/SearchPanel",
            },
          ],
        },
        {
          UID: "tab_4",
          label: "All",
          listing: this.getPageListing("all"),
          buttons: this.getPageButtons("all"),
          fields: [
            {
              input_type: "custom",
              name: "text",
              value: "all",
              component_path: "./invoice/SearchPanel",
            },
          ],
        },
      ],
    },
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
  customerLogin = (data) => {
    var ec_customer_id = null;
    if (data[0]) {
      ec_customer_id = data[0].ec_customer_id;
    }
    axios.post("/dt/customer/customer_login/", { ec_customer_id: ec_customer_id }).then((response) => {
      if (response.data.code == 1) {
        window.open(response.data.data.url);
      }
    });
  };
  editInvoice = (data) => {
    var invoice_id = data[0].id;
    var invoice_number = data[0].invoice_number;
    this.appModal.show({
      title: "Edit Invoice:" + " " + invoice_number,
      url: "/invoice/edit_invoice/?ids=" + invoice_id + "&user_id=" + this.user_id,
      style: { width: "90%", height: "90vh" },
    });
  };
  creditOnInvoice = (data) => {
    var invoice_id = data[0].id;
    this.appModal.show({
      title: "Parameter entry",
      url: "/invoice/credit_on_invoice/?ids=" + invoice_id,
      style: { width: "90%", height: "90vh" },
    });
  };
  closeInvoice = (data) => {
    var invoice_ids = "";
    for (var row in data) {
      invoice_ids = invoice_ids + data[row].id + ",";
    }
    this.appModal.show({
      title: "Register payment",
      url: "/invoice/close_invoice/?ids=" + invoice_ids.slice(0, -1) + "&user_id=" + this.user_id,
      style: { width: "90%", height: "75vh" },
    });
  };
  status_handleChange = (row) => {
    this.setState({ status_id: row });
  };
  changeStatus_handleChange = (row) => {
    this.setState({ status_id: row });
  };
  changeGrant_handleChange = (row) => {
    this.setState({ days: row });
  };
  handleCancel = () => {
    this.setState({ isModalVisible: false });
    this.setState({ isChangeModalVisible: false });
    this.setState({ isGrantModalVisible: false });
    this.setState({ isCreditLimitModalVisible: false });
    this.setState({ isCreditStatusModalVisible: false });
  };
  updateSecondaryStatus = () => {
    var post_data = {
      user_id: this.user_id,
      status_id: this.state.status_id,
      invoice_number: this.state.invoice_number,
      invoice_id: this.state.invoice_id,
    };
    axios.post("/dt/sales/change_secondary_status/", post_data).then((response) => {
      if (response.data.data == 0) {
        showMessage("Status updated.", "Status successfully updated", "success");
        this.setState({ isModalVisible: false });
        this.dataForm.refreshTable(this.state.status);
      } else {
        showMessage("No update.", "Something went wrong", "error");
      }
    });
  };
  updateDays = () => {
    var grant_days = {
      user_id: this.user_id,
      days: this.state.days,
      invoice_number: this.state.invoice_number,
      invoice_due_date: this.state.invoice_due_date,
      invoice_id: this.state.invoice_id,
      status_id: this.state.status_id,
    };
    axios.post("/dt/sales/grant_days/", grant_days).then((response) => {
      if (response.data.data == 0) {
        showMessage("Status updated.", "Status successfully updated", "success");
        this.setState({ isGrantModalVisible: false });
        this.dataForm.refreshTable(this.state.status);
      } else {
        showMessage("No update.", "Something went wrong", "error");
      }
    });
  };
  updateStatus = () => {
    var post_data = {
      user_id: this.user_id,
      status_id: this.state.status_id,
      invoice_number: this.state.invoice_number,
      invoice_id: this.state.invoice_id,
    };
    axios.post("/dt/sales/change_invoice_status/", post_data).then((response) => {
      if (response.data.data == 0) {
        showMessage("Status updated.", "Status successfully updated", "success");
        this.setState({ isChangeModalVisible: false });
        this.dataForm.refreshTable(this.state.status);
      } else {
        showMessage("No update.", "Something went wrong", "error");
      }
    });
  };
  creditLimit(data) {
    axios.post("/dt/sales/credit_limit/", { customer_id: data[0].ec_customer_id }).then((response) => {
      var val = response.data.data.data[0];
      this.setState({
        ec_company_id: data[0].ec_customer_id,
        credit_limit: val.climit,
        base_credit_limit: val.iclimit,
        date_type: val.ddtype,
        starting_days: val.cdays,
      });
    });
  }
  change_creditlimit = () => {
    var data = {
      credit_limit: this.state.credit_limit,
      base_credit_limit: this.state.base_credit_limit,
      starting_days: this.state.starting_days,
      invoice_date: this.state.date_type,
      ec_company_id: this.state.ec_company_id,
    };
    axios.post("/dt/sales/change_credit_limit/", data).then((response) => {
      if (response.data.code == 1) {
        showMessage("", "Credit limit updated.", "success");
        this.setState({ isCreditLimitModalVisible: false });
        this.dataForm.refreshTable(this.state.status);
      } else {
        showMessage("No update.", "Something went wrong", "error");
      }
    });
  };
  refresh = () => {
    this.dataForm.refreshTable();
  };
  componentDidMount = () => {};
  exportXls = (data) => {
    var ids = "";
    for (var row in data) {
      ids = ids + data[row].id + ",";
    }
    window.open("/dt/base/search_invoice_export/?invoice_id=" + ids + "&file_type=" + "xls");
  };
  exportCSV = (data) => {
    var ids = "";
    for (var row in data) {
      ids = ids + data[row].id + ",";
    }
    window.open("/dt/base/search_invoice_export/?invoice_id=" + ids + "&file_type=" + "csv");
  };
  exportXML = (data) => {
    var ids = "";
    for (var row in data) {
      ids = ids + data[row].id + ",";
    }
    window.open("/dt/base/search_invoice_export/?invoice_id=" + ids + "&file_type=" + "xml");
  };
  closeModal = (e) => {
    if (e.action == "close_modal") {
      FinMessage("Edit Invoice successfully saved.", "success");
    }
    if (e.action == "generate_modal") {
      FinMessage("Credit on Invoice successfully generated .", "success");
    }
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
          callBack={this.closeModal}
          ref={(node) => {
            this.appModal = node;
          }}
        ></AppModal>
        <Modal title="Secondary status" visible={this.state.isModalVisible} onOk={this.handleOk} onCancel={this.handleCancel} footer={null}>
          <Form labelCol={{ xs: { span: 6 } }} wrapperCol={{ xs: { span: 12 } }} form={this.form} onFinish={this.handleOk} scrollToFirstError>
            <Form.Item style={{ marginLeft: 20 }}>
              <Form.Item className="collection-input">
                <SearchInput
                  placeholder="Status"
                  handleChange={this.status_handleChange}
                  fieldProps={{ mode: "single", datasource: { query: "/dt/base/lookups/status/" } }}
                  style={{ width: 300 }}
                ></SearchInput>
              </Form.Item>
              <Row>
                <Col span={9} style={{ marginLeft: 0 }}>
                  <Button type="primary" htmlType="submit" onClick={this.updateSecondaryStatus}>
                    Save
                  </Button>
                </Col>
                <Col span={9} style={{ marginLeft: 20 }}>
                  <Button onClick={this.handleCancel}>Cancel</Button>
                </Col>
              </Row>
            </Form.Item>
          </Form>
        </Modal>
        <Modal title="Change status" visible={this.state.isChangeModalVisible} onOk={this.handleOk} onCancel={this.handleCancel} footer={null}>
          <Form labelCol={{ xs: { span: 6 } }} wrapperCol={{ xs: { span: 12 } }} form={this.form} onFinish={this.handleOk} scrollToFirstError>
            <Form.Item style={{ marginLeft: 20 }}>
              <Form.Item className="collection-input">
                <SearchInput
                  placeholder="Status"
                  handleChange={this.changeStatus_handleChange}
                  fieldProps={{ mode: "single", datasource: { query: "/dt/base/lookups/change_status/" } }}
                  style={{ width: 300 }}
                ></SearchInput>
              </Form.Item>
              <Row>
                <Col span={9} style={{ marginLeft: 0 }}>
                  <Button type="primary" htmlType="submit" onClick={this.updateStatus}>
                    Save
                  </Button>
                </Col>
                <Col span={9} style={{ marginLeft: 20 }}>
                  <Button onClick={this.handleCancel}>Cancel</Button>
                </Col>
              </Row>
            </Form.Item>
          </Form>
        </Modal>
        <Modal title="Grant days" visible={this.state.isGrantModalVisible} onOk={this.handleOk} onCancel={this.handleCancel} footer={null}>
          <Form labelCol={{ xs: { span: 6 } }} wrapperCol={{ xs: { span: 12 } }} form={this.form} onFinish={this.handleOk} scrollToFirstError>
            <Form.Item className="collection-input">
              <InputNumber style={{ width: 400 }} placeholder="Grant days" onChange={this.changeGrant_handleChange} />
            </Form.Item>
            <Row>
              <Col>
                <Button type="primary" htmlType="submit" onClick={this.updateDays}>
                  Ok
                </Button>
              </Col>
              <Col style={{ marginLeft: 20 }}>
                <Button onClick={this.handleCancel}>Cancel</Button>
              </Col>
            </Row>
          </Form>
        </Modal>
        <Modal title="Credit limit" visible={this.state.isCreditLimitModalVisible} onOk={this.handleOk} onCancel={this.handleCancel} footer={null}>
          <Form form={this.form} onFinish={this.handleOk}>
            <Form.Item style={{ marginLeft: 20 }}>
              <h3 style={{ marginLeft: 0 }}>Credit limit level-Customer Level</h3>
              <br />
              <Row>
                <Col span={10}>
                  <p>Base system</p>
                </Col>
                <Col span={6}>
                  <Input
                    value={this.state.credit_limit}
                    placeholder="500.00"
                    style={{ width: 100 }}
                    onChange={(e) => {
                      this.setState({ credit_limit: e.target.value });
                    }}
                  />
                </Col>
                <Col span={3} style>
                  <p>EUR</p>
                </Col>
              </Row>
              <Row>
                <Col span={10} style>
                  <p>Base Graydon Credit limit</p>
                </Col>
                <Col span={6}>
                  <Input
                    value={this.state.base_credit_limit}
                    placeholder="500.00"
                    style={{ width: 100 }}
                    onChange={(e) => {
                      this.setState({ base_credit_limit: e.target.value });
                    }}
                  />
                </Col>
                <Col span={3} style>
                  <p>EUR</p>
                </Col>
              </Row>
              <br />
              <h3>Invoice due date</h3>
              <br />
              <Row>
                <Col span={10}>
                  <p>Days starting</p>
                </Col>
                <Col span={12}>
                  <Input
                    value={this.state.starting_days}
                    placeholder="30"
                    style={{ width: 50 }}
                    onChange={(e) => {
                      this.setState({ starting_days: e.target.value });
                    }}
                  />
                </Col>
              </Row>
              <Row>
                <Radio.Group
                  // options={plainOptions}
                  onChange={(e) => {
                    this.setState({ date_type: e.target.value });
                  }}
                  value={this.state.date_type}
                  style={{ marginLeft: 10 }}
                >
                  <Radio value={1}>From invoice date</Radio>
                  <Radio value={2}>First day of the month following invoice due date</Radio>
                </Radio.Group>
              </Row>
              <br />
              <Row>
                <Col span={4} style={{ marginLeft: 0 }}>
                  <Button type="primary" htmlType="submit" onClick={this.change_creditlimit}>
                    Save
                  </Button>
                </Col>
                <Col span={4} style={{ marginLeft: 0 }}>
                  <Button onClick={this.handleCancel}>Cancel</Button>
                </Col>
              </Row>
            </Form.Item>
          </Form>
        </Modal>
      </div>
    );
  }
}
SearchInvoice.getInitialProps = async (context) => {
  return {
    isModal: context.query.is_model ?? false,
    creditlimit: context.query.creditlimit,
    customercreditlimit: context.query.customercreditlimit,
    cust_outstanding: context.query.cust_outstanding,
    name: context.query.name,
  };
};
export default SearchInvoice;
