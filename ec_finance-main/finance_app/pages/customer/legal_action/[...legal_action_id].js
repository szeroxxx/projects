import { DeleteOutlined, DownloadOutlined, EditOutlined, ExclamationCircleOutlined, LinkOutlined } from "@ant-design/icons";
import { DatePicker, Modal, Tooltip } from "antd";
import axios from "axios";
import moment from "moment";
import React, { Component } from "react";
import { showMessage } from "../../../common/Util";
import AppIcons from "../../../components/AppIcons";
import AppModal from "../../../components/AppModal";
import DataForm from "../../../components/DataForm";
const { confirm } = Modal;
class LegalAction extends Component {
  constructor(props) {
    super(props);
  }
  user_id = this.props.session.user.data.user_id;
  state = { data: {}, followDate: moment().add(1, "day") };
  appSchema = {
    pageTitle: this.props.customer,
    formSchema: {
      init_data: {
        api: "/dt/sales/scheduler/customer_details/",
        post_data: { customer_id: this.props.customerId, is_legal: true },
      },
      on_submit: {},
      edit_button: false,
      submit_button: false,
      hide_buttons: false,
      readonly: false,
      columns: 2,
      buttons: [
        {
          name: "add_action",
          title: "Add Actions",
          tooltip: "Add Actions",
          sequence: 1,
          click_handler: (form_data) => {
            this.appModal.show({
              title: "Add Action",
              url: "/customer/action/" + this.props.customerId + "/" + this.props.invoiceId + "/?is_legal=true",
              style: { width: "80%", height: "85vh" },
            });
          },
        },
        ,
        {
          name: "close",
          title: "Close",
          tooltip: "",
          sequence: 1,
          click_handler: (form_data) => {
            window.parent.postMessage(
              JSON.stringify({
                action: "close_form",
              })
            );
          },
        },
      ],
      tabs: [
        {
          UID: "tab_1",
          label: "Info",
          fields: [
            {
              name: "customer_name",
              title: "Customer",
              input_type: "label",
              sequence: 1,
            },
            {
              name: "total_invoice",
              title: "Total invoices",
              input_type: "label",
              sequence: 2,
            },
            {
              name: "email",
              title: "Email",
              input_type: "label",
              sequence: 3,
            },
            {
              name: "invoice_amount",
              title: "Invoice amount",
              input_type: "label",
              sequence: 3,
            },
            {
              name: "contact_number",
              title: "Contact",
              input_type: "label",
              sequence: 4,
            },
            {
              name: "paid_amount",
              title: "Paid amount",
              input_type: "label",
              sequence: 5,
            },
            {
              name: "country",
              title: "Country",
              input_type: "label",
              sequence: 6,
            },
            {
              name: "total_reminder",
              title: "Total Reminders",
              input_type: "label",
              sequence: 7,
            },
            {
              name: "last_reminder",
              title: "Last Reminder",
              input_type: "label",
              sequence: 8,
            },
          ],
          tabs: [
            {
              UID: "tab_action",
              label: "Action",
              buttons: [
                {
                  name: "mark_completed",
                  title: "Mark completed",
                  dataGridUID: "actions",
                  tooltip: "",
                  multi_select: false,
                  sequence: 2,
                  confirm: {
                    title: "Are you sure you want to complete this action?",
                    content: <></>,
                    okText: "Yes, Complete",
                    cancelText: "No, Cancel",
                    onOk: () => {
                      this.sendToCompleted("actions");
                    },
                  },
                },
                {
                  name: "add_follow_up",
                  title: "Add follow up",
                  dataGridUID: "actions",
                  multi_select: false,
                  tooltip: "",
                  sequence: 2,
                  confirm: {
                    title: "Follow up date",
                    icon: <></>,
                    content: (
                      <>
                        <DatePicker
                          defaultValue={this.state.followDate}
                          onChange={(e) => {
                            if (e != null) {
                              this.setState({ followDate: e._d });
                            } else {
                              showMessage("Follow up date must be required", "", "error");
                              this.setState({ followDate: null });
                            }
                          }}
                        ></DatePicker>
                      </>
                    ),
                    okText: "Add follow up",
                    cancelText: "Cancel",
                    onOk: () => {
                      this.addFollowUp("actions");
                    },
                  },
                },
              ],
              listing: [
                {
                  dataGridUID: "actions",
                  url: "/dt/sales/actions/?invoice_id=" + this.props.invoiceId,
                  paging: true,
                  default_sort_col: "id",
                  default_sort_order: "descend",
                  row_selection: true,
                  bind_on_load: true,
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
                      value: "action_type",
                      sortable: true,
                      text: "Action type",
                      render: (text, record, index) => {
                        return (
                          <>
                            {text == "Call" && <AppIcons code="PhoneOutlined" />}
                            {text == "Follow up" && <AppIcons code="BellOutlined" />}
                            {text == "Email" && <AppIcons code="MailOutlined" />}
                            {text == "Chat" && <AppIcons code="SoundOutlined" />}
                            {text == "Remarks" && <AppIcons code="FileExclamationOutlined" />}
                            {text == "Offline message" && <AppIcons code="ReconciliationOutlined" />}
                            {" " + text}
                          </>
                        );
                      },
                    },
                    {
                      value:"invoice_nr",
                      text:"Invoice number",
                      // sortable: true,
                      render: (text, record, index) => {
                        if (record.is_cust_base == false) {
                          return record.invoice_nr
                        }
                      }
                    },
                    {
                      value: "summary",
                      text: "Remarks",
                      sortable: true,
                    },
                    {
                      value: "action_status",
                      sortable: true,
                      text: "Status",
                    },
                    {
                      value: "full_name",
                      sortable: true,
                      text: "Action by",
                    },
                    {
                      value: "action_date",
                      text: "Action date",
                      sortable: true,
                      width: 300,
                      sequence: 2,
                    },

                    {
                      value: "attachment",
                      sortable: false,
                      text: "Attachment",
                      width: 100,
                      render: (text, record, index) => {
                        return (
                          <>
                            {record.url != null && record.url.length > 10 && (
                              <div onClick={() => this.downloadAttachment(record, this.dataForm, this.user_id)}>
                                <DownloadOutlined />
                              </div>
                            )}
                          </>
                        );
                      },
                    },
                    {
                      value: "id",
                      sortable: false,
                      text: "",
                      width: 40,
                      render: (text, record, index) => {
                        return (
                          <div className="deleteIcon" onClick={() => this.deleteAction(record, this.dataForm, this.user_id)}>
                            <Tooltip placement="top" title="delete">
                              <DeleteOutlined />
                            </Tooltip>
                          </div>
                        );
                      },
                    },
                    {
                      value: "id",
                      text: "",
                      width: 40,
                      render: (text, record, index) => {
                        return (
                          <div>
                            <Tooltip placement="top" title="Edit">
                              <EditOutlined
                                onClick={() =>
                                  this.appModal.show({
                                    title: "Edit Action",
                                    url:
                                      "/customer/action/" +
                                      this.props.customerId +
                                      "/" +
                                      this.props.invoiceId +
                                      "/?action_id=" +
                                      record.id +
                                      "&is_edit=true" +
                                      "&action_status=" +
                                      record.action_status,
                                    style: { width: "80%", height: "80vh" },
                                  })
                                }
                              />
                            </Tooltip>
                          </div>
                        );
                      },
                    },
                  ],
                },
              ],
            },
            {
              UID: "tab_all_action",
              label: "All Invoices Action",
              buttons: [
                {
                  name: "mark_completed",
                  title: "Mark completed",
                  dataGridUID: "actions",
                  tooltip: "",
                  multi_select: false,
                  sequence: 2,
                  confirm: {
                    title: "Are you sure you want to complete this action?",
                    content: <></>,
                    okText: "Yes, Complete",
                    cancelText: "No, Cancel",
                    onOk: () => {
                      this.sendToCompleted("actions");
                    },
                  },
                },
                {
                  name: "add_follow_up",
                  title: "Add follow up",
                  dataGridUID: "actions",
                  multi_select: false,
                  tooltip: "",
                  sequence: 2,
                  confirm: {
                    title: "Follow up date",
                    icon: <></>,
                    content: (
                      <>
                        <DatePicker
                          defaultValue={this.state.followDate}
                          onChange={(e) => {
                            if (e != null) {
                              this.setState({ followDate: e._d });
                            } else {
                              showMessage("Follow up date must be required", "", "error");
                              this.setState({ followDate: null });
                            }
                          }}
                        ></DatePicker>
                      </>
                    ),
                    okText: "Add follow up",
                    cancelText: "Cancel",
                    onOk: () => {
                      this.addFollowUp("actions");
                    },
                  },
                },
              ],
              listing: [
                {
                  dataGridUID: "all_actions",
                  url: "/dt/sales/actions/?customer_id=" + this.props.customerId ,
                  paging: true,
                  default_sort_col: "id",
                  default_sort_order: "descend",
                  row_selection: true,
                  bind_on_load: true,
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
                      value: "action_type",
                      sortable: true,
                      text: "Action type",
                      render: (text, record, index) => {
                        return (
                          <>
                            {text == "Call" && <AppIcons code="PhoneOutlined" />}
                            {text == "Follow up" && <AppIcons code="BellOutlined" />}
                            {text == "Email" && <AppIcons code="MailOutlined" />}
                            {text == "Chat" && <AppIcons code="SoundOutlined" />}
                            {text == "Remarks" && <AppIcons code="FileExclamationOutlined" />}
                            {text == "Offline message" && <AppIcons code="ReconciliationOutlined" />}
                            {" " + text}
                          </>
                        );
                      },
                    },
                    {
                      value:"invoice_nr",
                      text:"Invoice number",
                      // sortable: true,
                      render: (text, record, index) => {
                        if (record.is_cust_base == false) {
                          return record.invoice_nr
                        }
                      }
                    },
                    {
                      value: "summary",
                      text: "Remarks",
                      sortable: true,
                    },
                    {
                      value: "action_status",
                      sortable: true,
                      text: "Status",
                    },
                    {
                      value: "full_name",
                      sortable: true,
                      text: "Action by",
                    },
                    {
                      value: "action_date",
                      text: "Action date",
                      sortable: true,
                      width: 300,
                      sequence: 2,
                    },

                    {
                      value: "attachment",
                      sortable: false,
                      text: "Attachment",
                      width: 100,
                      render: (text, record, index) => {
                        return (
                          <>
                            {record.url != null && record.url.length > 10 && (
                              <div onClick={() => this.downloadAttachment(record, this.dataForm, this.user_id)}>
                                <DownloadOutlined />
                              </div>
                            )}
                          </>
                        );
                      },
                    },
                    {
                      value: "id",
                      sortable: false,
                      text: "",
                      width: 40,
                      render: (text, record, index) => {
                        return (
                          <div className="deleteIcon" onClick={() => this.deleteAction(record, this.dataForm, this.user_id)}>
                            <Tooltip placement="top" title="delete">
                              <DeleteOutlined />
                            </Tooltip>
                          </div>
                        );
                      },
                    },
                    {
                      value: "id",
                      text: "",
                      width: 40,
                      render: (text, record, index) => {
                        return (
                          <div>
                            <Tooltip placement="top" title="Edit">
                              <EditOutlined
                                onClick={() =>
                                  this.appModal.show({
                                    title: "Edit Action",
                                    url:
                                      "/customer/action/" +
                                      this.props.customerId +
                                      "/" +
                                      this.props.invoiceId +
                                      "/?action_id=" +
                                      record.id +
                                      "&is_edit=true" +
                                      "&action_status=" +
                                      record.action_status,
                                    style: { width: "80%", height: "80vh" },
                                  })
                                }
                              />
                            </Tooltip>
                          </div>
                        );
                      },
                    },
                  ],
                },
              ],
            },
          ],
        },
        {
          UID: "tab_2",
          label: "Invoices",
          buttons: [
            /*{
              name: "send_to_legal_action",
              title: "Send To Legal Action",
              type: "primary",
              tooltip: "",
              multi_select: true,
              sequence: 2,
              click_handler: () => {
                this.sendToLegalAction("invoices");
              },
            },*/
          ],
          listing: [
            {
              dataGridUID: "invoices",
              url: "/dt/sales/legal_customer_invoices/?customer_id=" + this.props.customerId,
              paging: true,
              default_sort_col: "id",
              default_sort_order: "descend",
              row_selection: true,
              bind_on_load: true,
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
                  value: "invoice_number",
                  text: "Invoice number",
                  sortable: true,
                  sequence: 2,
                  render: (text, record, index) => {
                    return (
                      <div>
                        {record.invoice_number}
                        <LinkOutlined
                          className="on-hover-color"
                          style={{ marginLeft: 10 }}
                          onClick={() => window.open("https://mail.google.com/mail/u/0/?#search/" + record.invoice_number.replace("/", "%2F"), "_blank")}
                        />
                      </div>
                    );
                  },
                },

                {
                  value: "invoice_amount",
                  text: "Invoice amount",
                  sortable: true,
                  sequence: 3,
                },
                {
                  value: "amount_paid",
                  text: "Amount paid",
                  sortable: true,
                },
                {
                  value: "last_reminder_date",
                  sortable: true,
                  text: "Last reminder date",
                },
                {
                  value: "total_reminder",
                  sortable: true,
                  text: "Total reminder",
                },
                {
                  value: "invoice_created_on",
                  sortable: true,
                  text: "Invoice created",
                },

                {
                  value: "invoice_status",
                  sortable: true,
                  text: "Invoice status",
                },
                {
                  value: "secondary_status",
                  sortable: true,
                  text: "Secondary status",
                  width: 150,
                },
              ],
            },
          ],
        },
        {
          UID: "tab_3",
          label: "Reminders",
          listing: [
            {
              dataGridUID: "reminders",
              url: "/dt/sales/scheduler/?customer_id=" + this.props.customerId,
              paging: true,
              default_sort_col: "id",
              default_sort_order: "descend",
              row_selection: true,
              bind_on_load: true,
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
                  value: "scheduler_name",
                  text: "Reminder name",
                  sortable: true,
                  width: 300,
                  sequence: 2,
                },

                {
                  value: "customer_name",
                  text: "Customer name",
                  sortable: true,
                  sequence: 3,
                },
                {
                  value: "total_invoice",
                  text: "Total invoice",
                  sortable: true,
                  modal: {
                    url: "/customer/invoices/",
                    title: "Reminder",
                    title_key: ["scheduler_name"],
                    queryParams: [{ key: "customer_id", value: this.props.customerId }, { key: "id" }],
                  },
                },
                {
                  value: "created_on",
                  sortable: true,
                  text: "Created on",
                },
              ],
            },
          ],
        },
      ],
    },
  };
  addFollowUp = (gridID) => {
    var selectedRows = this.dataForm.getSelectedRows(gridID);
    var value = "";
    if (this.state.followDate === null) {
      showMessage("Follow up date must be required", "", "error");
      return;
    }
    for (var row in selectedRows) {
      value = value + selectedRows[row].id + ",";
    }
    axios
      .post("/dt/sales/action/follow_up_action/", {
        ids: value.slice(0, -1),
        user_id: this.user_id,
        action_date: this.state.followDate,
        invoice_id: this.props.invoiceId,
      })
      .then((response) => {
        if (response.data.code == 0) {
          this.dataForm.showMessage("error", { message: "Failed!", description: response.data.message });
          return;
        }
        this.dataForm.showMessage("success", { message: "Success!", description: response.data.message });
        this.dataForm.refreshTable(gridID);
      });
  };
  sendToCompleted = (gridID) => {
    var selectedRows = this.dataForm.getSelectedRows(gridID);
    var value = "";
    for (var row in selectedRows) {
      value = value + selectedRows[row].id + ",";
    }
    axios.post("/dt/sales/action/complete_action/", { ids: value.slice(0, -1), user_id: this.user_id, invoice_id: this.props.invoiceId }).then((response) => {
      if (response.data.code == 0) {
        this.dataForm.showMessage("error", { message: "Failed!", description: response.data.message });
        return;
      }
      this.dataForm.showMessage("success", { message: "Success!", description: response.data.message });
      this.dataForm.refreshTable(gridID);
    });
  };
  downloadAttachment = (record, dataForm, user_id) => {
    window.open("/dt/attachment/dwn_attachment/?uid=" + record.uid + "&app=sales&model=collectionactionattachment&user_id=" + user_id);
  };
  deleteAction = (data, dataForm, userId) => {
    confirm({
      title: "Are you sure want to delete this record?",
      icon: <ExclamationCircleOutlined />,
      content: <></>,
      cancelText: "No, Cancel",
      okText: "Yes, Delete",

      onOk() {
        axios.post("/dt/sales/action/delete_action/ ", { ids: data.id + "", user_id: userId }).then((response) => {
          if (response.data.code == 0) {
            dataForm.showMessage("error", { message: "Failed!", description: response.data.message });
            return;
          }
          dataForm.showMessage("success", { message: "Success!", description: response.data.message });
          dataForm.refreshTable("actions");
          dataForm.refreshTable("all_actions");
        });
      },
      onCancel() {
        console.log("Cancel");
      },
    });
  };
  render() {
    return (
      <>
        <DataForm
          schema={this.appSchema}
          initData={this.state}
          isModal={true}
          activeTabUID={'tab_action'}
          isFrame={true}
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
      </>
    );
  }
}
LegalAction.getInitialProps = async (context) => {
  return {
    customer: context.query.c ?? "",
    customerId: context.query.legal_action_id[0],
    invoiceId: context.query.legal_action_id[1],
    action_status: context.query.action_status,
    isModal: true,
  };
};
export default LegalAction;
