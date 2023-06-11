import DataGridViewer from "../../components/DataGridViewer";

import { DeleteOutlined, ExclamationCircleOutlined } from "@ant-design/icons";
import { Col, Form, Input, Modal, Row, Select, Tooltip } from "antd";
import axios from "axios";
import React, { Component } from "react";
import { showMessage } from "../../common/Util";
import ActionPanel from "../../components/ActionPanel";
import AppModal from "../../components/AppModal";
import EmailPreview from "../../components/EmailPreview";
import PageTitle from "../../components/PageTitle";
const { Option } = Select;
const { confirm } = Modal;

class PaymentReminder extends Component {
  constructor(props) {
    super(props);
  }

  user_id = this.props.session.user.data.user_id;
  state = { data: {}, handling_company: [], render: false };

  paymentAppSchema = {
    pageTitle: "Payment reminder exception",
    gridViewer: true,
    buttons: [
      {
        name: "schedule",
        title: "Schedule",
        class: "mr-left",
        primary: "primary",
        icon_code: "FieldTimeOutlined",
        multi_select: true,
        tooltip: "",
        sequence: 1,
        class: "mr-left",
        click_handler: (data) => {
          this.Schedule();
        },
      },
      {
        name: "reminder_preview",
        title: "Reminder preview",
        icon_code: "FileTextOutlined",
        class: "mr-left",
        primary: "primary",
        multi_select: false,
        tooltip: "",
        sequence: 2,
        class: "mr-left",
        click_handler: () => {
          var data = this.customerGridViewer.getSelectedRows();
          if (data.length == 0) {
            showMessage("Select one.", "Please select at least one Record", "error");
          } else {
            this.emailTemplate();
          }
          // this.setState({render : false})
        },
      },
      {
        name: "edit_profile",
        title: "Edit profile",
        class: "mr-left",
        primary: "primary",
        icon_code: "UserOutlined",
        tooltip: "",
        sequence: 3,
        class: "mr-left",
        multi_select: false,
        click_handler: () => {
          var data = this.customerGridViewer.getSelectedRows();
          if (data.length == 0) {
            showMessage("Select one", "Please select at least one Record", "error");
          } else {
            this.editProfile(data);
          }
        },
      },
    ],
    listing: [
      {
        dataGridUID: "scheduleReminder",
        url: "/dt/sales/invoice_schedule/",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: true,
        row_selection_type: "single",
        bind_on_load: true,
        scroll: 250,
        multi_select: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: false,
            sequence: 1,
          },
          {
            value: "name",
            text: "Scheduler name",
            sortable: true,
            width: 60,
            sequence: 2,
          },
          {
            value: "automatic_invoice",
            text: "Automatic invoices",
            sortable: true,
            width: 40,
            sequence: 3,
          },
          {
            value: "manual_invoice",
            text: "Manual invoices",
            width: 40,
            sortable: true,
          },
          {
            value: "total_invoices",
            text: "Total invoices",
            width: 40,
            sortable: true,
          },
          {
            value: "status",
            text: "Sent status",
            width: 30,
            sortable: true,
          },
          {
            value: "full_name",
            text: "Created by",
            width: 50,
          },
          {
            value: "created_on",
            text: "Created on",
            width: 70,
          },
          {
            value: "country_id",
            show: false,
            text: "country_id",
            width: 100,
          },
          {
            value: "id",
            text: "Delete ",
            width: 30,
            render: (text, record, index) => {
              return (
                <div
                  className="deleteIcon"
                  style={{
                    width: 50,
                    float: "left",
                  }}
                  onClick={() => this.deleteScheduler(record, this.refresh)}
                >
                  <Tooltip placement="top" title="delete">
                    <DeleteOutlined />
                  </Tooltip>
                </div>
              );
            },
          },
        ],
      },
      {
        dataGridUID: "countryBreakup",
        url: "/dt/sales/country_breakup/",
        paging: true,
        default_sort_col: "country_id",
        default_sort_order: "descend",
        row_selection: true,
        row_selection_type: "single",
        bind_on_load: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "country_name",
            text: "Country name",
            width: 200,
            sequence: 2,
          },
          {
            value: "zero_days_amount",
            text: "0 Days amount",
            width: 120,
          },
          {
            value: "zero_days_invoice",
            text: "0 Days invoice",
            width: 120,
          },
          {
            value: "l_ten_days_amount",
            text: "Due <10 Days amount",
            width: 180,
          },
          {
            value: "l_ten_days_invoice",
            text: "Due <10 Days invoice",
            width: 180,
          },
          {
            value: "l_thirty_days_amount",
            text: "Due <30 Days amount",
            width: 180,
          },
          {
            value: "l_thirty_days_invoice",
            text: "Due <30 Days invoice",
            width: 180,
          },
          {
            value: "l_sixty_days_amount",
            text: "Due <60 Days amount",
            width: 180,
          },
          {
            value: "l_sixty_days_invoice",
            text: "Due <60 Days invoice",
            width: 180,
          },
          {
            value: "l_ninety_days_amount",
            text: "Due <90 Days amount",
            width: 180,
          },
          {
            value: "l_ninety_days_invoice",
            text: "Due <90 Days invoice",
            width: 180,
          },
          {
            value: "g_ninety_days_amount",
            text: "Due >90 Days amount",
            width: 180,
          },
          {
            value: "g_ninety_days_invoice",
            text: "Due >90 Days invoice",
            width: 180,
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
        row_selection_type: "single",
        bind_on_load: false,
        gridViewer: true,
        columns: [
          {
            value: "id",
            text: "ID",
            show: false,
            row_key: true,
            sequence: 1,
          },
          {
            value: "company_name",
            text: "Company Name",
            width: 200,
            sequence: 2,
          },
          {
            value: "email",
            text: "Email",
            width: 200,
            sequence: 2,
          },
          {
            value: "re_created_on",
            text: "Reminder date",
            width: 150,
            sequence: 2,
          },

          {
            value: "language_code",
            text: "Language Code Nr.",
            width: 150,
            sequence: 2,
          },
          {
            value: "username",
            text: "Contact Person",
            width: 150,
            sequence: 2,
          },
          {
            value: "zero_days_amount",
            text: "0 Days amount",
            width: 120,
          },
          {
            value: "zero_days_invoice",
            text: "0 Days invoice",
            width: 120,
          },
          {
            value: "l_ten_days_amount",
            text: "Due <10 Days amount",
            width: 180,
          },
          {
            value: "l_ten_days_invoice",
            text: "Due <10 Days invoice",
            width: 170,
          },
          {
            value: "l_thirty_days_amount",
            text: "Due <30 Days amount",
            width: 170,
          },
          {
            value: "l_thirty_days_invoice",
            text: "Due <30 Days invoice",
            width: 170,
          },
          {
            value: "l_sixty_days_amount",
            text: "Due <60 Days amount",
            width: 180,
          },
          {
            value: "l_sixty_days_invoice",
            text: "Due <60 Days amount",
            width: 180,
          },
          {
            value: "l_ninety_days_amount",
            text: "Due <90 Days amount",
            width: 180,
          },
          {
            value: "l_ninety_days_invoice",
            text: "Due <90 Days invoice",
            width: 170,
          },
          {
            value: "g_ninety_days_amount",
            text: "Due >90 Days amount",
            width: 170,
          },
          {
            value: "g_ninety_days_invoice",
            text: "Due >90 Days invoice",
            width: 170,
          },
        ],
      },
      {
        dataGridUID: "customerinvoiceBreakup",
        url: "/dt/sales/invoice_breakup/",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
        row_selection: true,
        row_selection_type: "single",
        bind_on_load: false,
        gridViewer: true,
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
            width: 100,
            sequence: 2,
          },
          {
            value: "reminder_status",
            text: "Reminder",
            width: 100,
            sequence: 2,
          },
          {
            value: "status",
            text: "Reminder status",
            width: 150,
            sequence: 2,
          },
          {
            value: "reminder_date",
            text: "Reminder date",
            width: 150,
            sequence: 2,
          },
          {
            value: "invoice_number",
            text: "Invoice number",
            width: 150,
            sequence: 2,
          },
          {
            value: "invoice_created_on",
            text: "Invoice Date",
            width: 150,
            sequence: 2,
          },

          {
            value: "outstanding",
            text: "OutStanding Amount",
            width: 180,
            sequence: 2,
          },
          {
            value: "customer_outstanding",
            text: "Currency OutStanding Amount",
            width: 220,
            sequence: 2,
          },
          {
            value: "outstanding_days",
            text: "OutStanding Days",
            width: 170,
          },
          {
            value: "invoice_due_date",
            text: "Invoice Due Date",
            width: 150,
          },
          {
            value: "invoice_value",
            text: "Invoice Amount",
            width: 150,
          },
          {
            value: "currency_invoice_value",
            text: "Currency Invoice Amount",
            width: 200,
          },
          {
            value: "amount_paid",
            text: "Amount Paid",
            width: 120,
          },
          {
            value: "cust_amount_paid",
            text: "Currency Amount Paid",
            width: 180,
          },
          {
            value: "",
            text: "Paid On",
            width: 100,
          },
          {
            value: "order_nrs",
            text: "OrderNo",
            width: 100,
          },
          {
            value: "currency_symbol",
            text: "Currency Symbol",
            width: 150,
          },
          {
            value: "remarks",
            text: "Remarks",
            width: 100,
          },
        ],
      },
    ],
  };
  rowSelectionChange = (key, selectedRows) => {
    this.setState((prevState) => ({
      data: { ...prevState.data, [key]: selectedRows },
    }));
  };
  refresh = () => {
    this.scheduleGridViewer.refresh();
  };
  deleteScheduler = (data, callback) => {
    confirm({
      title: "Are you sure want to delete this record ?",
      icon: <ExclamationCircleOutlined />,
      content: <></>,
      cancelText: "No, Cancel",
      okText: "Yes, Delete",
      onOk() {
        axios.post("/dt/sales/invoice_schedule/delete_scheduler/", { ids: data.id }).then((response) => {
          if (response.data.code == 1) {
            callback();
            showMessage("Scheduler deleted.", "Scheduler successfully deleted", "success");
          } else {
            showMessage("No delete.", "Something went wrong", "error");
          }
        });
      },
      onCancel() {},
    });
  };
  onModelClose = () => {
    this.scheduleGridViewer.refreshTable("scheduleReminder");
  };
  handleChange = (value) => {
    this.setState({ value });
  };
  editProfile = (data) => {
    var ec_customer_id = null;
    if (data[0]) {
      ec_customer_id = data[0].ec_customer_id;
    }
    axios.post("/dt/customer/edit_profile/", { ec_customer_id: ec_customer_id }).then((response) => {
      if (response.data.code == 1) {
        this.appModal.show({
          url: response.data.data,
          title: "Edit Profile",
          style: { width: "90%", height: "85vh" },
        });
        return;
      }
    });
  };
  Schedule = () => {
    var total_items = this.customerGridViewer.getSelectedRows().length;
    if (total_items.length == 0) {
      this.showMessage("error", { message: "Please select at least one Record" });
      return;
    }
    var is_pdf_include = this.state.isPDF;
    var post_data = {
      customer_id: this.state.customer_id,
      country_id: this.state.country_id,
      schedule_id: this.state.schedule_id,
      total_items: total_items,
      is_pdf_include: is_pdf_include,
      user_id: this.user_id,
    };
    confirm({
      title: "Reminder schedule",
      icon: <ExclamationCircleOutlined />,
      content: <>Invoice payment reminder schedule will be generated, are you sure you want to continue?</>,
      cancelText: "No, Cancel",
      okText: "Yes, Schedule",
      onOk() {
        axios.post("/dt/sales/schedule/", post_data).then((response) => {
          if (response.data.code == 1) {
            showMessage("Sent schedule.", "Invoices are scheduled", "success");
          } else {
            showMessage("No sent schedule.", "Please select specific row", "error");
          }
        });
      },
      onCancel() {},
    });
  };
  onChangeIncludeInvoicePDF = (isPDF) => {
    var isPDF = isPDF.target.checked;
    this.setState({ isPDF });
  };
  scheduleSelectionChange = (key, selectedRows) => {
    let row = selectedRows[0];
    if (row) {
      this.setState({ schedule_id: row.id });
      this.countryGridViewer.searchData({ schedule_id: ["text", row.id] });
    } else {
      if (this.countryGridViewer) {
        this.setState({ schedule_id: "0", country_id: "0", customer_id: "0" });
        this.countryGridViewer.searchData({ schedule_id: ["text", "0"] });
        this.customerGridViewer.searchData({ country_id: ["text", "0"], schedule_id: ["text", "0"] });
        this.invoiceGridViewer.searchData({ customer_id: ["text", "0"], country_id: ["text", "0"], schedule_id: ["text", "0"] });
      }
    }
  };
  countrySelectionChange = (key, selectedRows) => {
    let row = selectedRows[0];
    if (row) {
      this.setState({ country_id: row.id });
      this.customerGridViewer.searchData({ country_id: ["text", row.id], schedule_id: ["text", this.state.schedule_id] });
    } else {
      if (this.customerGridViewer) {
        this.setState({ country_id: "0", customer_id: "0" });
        this.customerGridViewer.searchData({ country_id: ["text", "0"], schedule_id: ["text", "0"] });
        this.invoiceGridViewer.searchData({ customer_id: ["text", "0"], country_id: ["text", "0"], schedule_id: ["text", "0"] });
      }
    }
  };
  customerSelectionChange = (key, selectedRows) => {
    let row = selectedRows[0];
    if (row) {
      this.setState({ customer_id: row.id });
      this.invoiceGridViewer.searchData({
        customer_id: ["text", row.id],
        country_id: ["text", this.state.country_id],
        schedule_id: ["text", this.state.schedule_id],
      });
    } else {
      if (this.invoiceGridViewer) {
        this.invoiceGridViewer.searchData({ customer_id: ["text", "0"], country_id: ["text", "0"], schedule_id: ["text", "0"] });
      }
    }
    this.setState((prevState) => ({
      data: { ...prevState.data, [key]: selectedRows },
    }));
  };
  emailTemplate = () => {
    this.setState({
      render: !this.state.render,
      customer_id: this.state.customer_id,
      hand_company_id: this.state.hand_company_id,
      country_id: this.state.country_id,
    });
  };
  componentDidMount = () => {};
  onFalse = () => {
    this.setState({ render: false });
  };
  render() {
    return (
      <div style={{ maxHeight: "90vh", overflow: "auto" }}>
        <Row>
          <PageTitle pageTitle={this.paymentAppSchema.pageTitle}></PageTitle>
        </Row>
        <DataGridViewer
          schema={this.paymentAppSchema.listing[0]}
          onRowSelectionChange={this.scheduleSelectionChange}
          ref={(node) => {
            this.scheduleGridViewer = node;
          }}
        ></DataGridViewer>
        <b>
          <h3>Country breakup</h3>
        </b>
        <DataGridViewer
          schema={this.paymentAppSchema.listing[1]}
          onRowSelectionChange={this.countrySelectionChange}
          ref={(node) => {
            this.countryGridViewer = node;
          }}
        ></DataGridViewer>
        <b>
          <h3>Customer breakup</h3>
        </b>
        <DataGridViewer
          schema={this.paymentAppSchema.listing[2]}
          onRowSelectionChange={this.customerSelectionChange}
          ref={(node) => {
            this.customerGridViewer = node;
          }}
        ></DataGridViewer>
        <b>
          <h3>Customer invoice breakup</h3>
        </b>
        <DataGridViewer
          schema={this.paymentAppSchema.listing[3]}
          onRowSelectionChange={this.rowSelectionChange}
          ref={(node) => {
            this.invoiceGridViewer = node;
          }}
        ></DataGridViewer>
        <Row style={{ marginBottom: 10, marginTop: 10 }}>
          <Col span={12}>
            <Form.Item label="Include invoice PDF" className="collection-input">
              <Input type={"checkbox"} onChange={this.onChangeIncludeInvoicePDF}></Input>
            </Form.Item>
          </Col>
          <Col span={12}>
            <ActionPanel buttons={this.paymentAppSchema.buttons} selectedRows={this.state.data[this.paymentAppSchema.listing[2].dataGridUID]} />
          </Col>
        </Row>
        {this.state.render && <EmailPreview customer={this.state.customer_id} hand_company={this.state.hand_company_id} onFalse={this.onFalse} />}
        <AppModal
          ref={(node) => {
            this.appModal = node;
          }}
        ></AppModal>
      </div>
    );
  }
}
export default PaymentReminder;
