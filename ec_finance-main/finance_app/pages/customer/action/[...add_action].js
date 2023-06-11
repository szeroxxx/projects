import { DeleteOutlined, KeyOutlined } from "@ant-design/icons";
import axios from "axios";
import React, { Component } from "react";
import DataForm from "../../../components/DataForm";

class Action extends Component {
  constructor(props) {
    super(props);
  }

  user_id = this.props.session.user.data.user_id;
  state = { data: {}, isEdit: this.props.isEdit, action_status: this.props.action_status == "Pending" ? "due" : "done" ,is_legal: this.props.is_legal};
  addAction = (form_data) => {
    var actionDate = this.formatDate(0);
    var next_action_date = this.formatDate(1);
    if (form_data.values.action_date) {
      actionDate = form_data.values.action_date;
    }
    if (form_data.values.remainder_date) {
      next_action_date = form_data.values.remainder_date;
    }
    var data = [
      {
        action_by_id: form_data.values.action_by,
        customer_id: this.props.customerId,
        invoice_id: this.props.invoiceId,
        action_type: form_data.values.action_type,
        is_legal: this.props.is_legal,
        action_date: actionDate,
        summary: form_data.values.summary,
        action_status: form_data.values.action_tab ? form_data.values.action_tab : this.state.action_status,
        reference: "",
        action_id: this.props.action_id,
        scope:form_data.values.scope
      },
    ];

    if (form_data.values.remainder_date && form_data.values.remainder_date != "" && form_data.values.action_tab != "due") {
      data.push({
        action_by_id: form_data.values.action_by,
        customer_id: this.props.customerId,
        is_legal: this.props.is_legal,
        invoice_id: this.props.invoiceId,
        action_type: "follow_up",
        action_date: next_action_date,
        summary: form_data.values.summary,
        action_status: "due",
        reference: "",
        action_id: this.props.action_id,
        scope:form_data.values.scope
      });
    }
    const fromData = new FormData();
    fromData.append("data", JSON.stringify(data));
    if (form_data.values.attachment) {
      form_data.values.attachment.forEach((val) => fromData.append("attachment", val));
    }
    // if (form_data.values.attachment_next) {
    //   console.log("enter in attachment","attachment_next",form_data.values.attachment_next);
    //   form_data.values.attachment_next.forEach((val) => fromData.append("attachment_done", val));
    // }
    if (form_data.values.scope == "customer_level"){
      axios
      .post("/dt/sales/action/customer_level/", fromData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((result) => {
        window.parent.postMessage(
          JSON.stringify({
            action: "close_form",
          })
        );
      });
    }else{
      axios
      .post("/dt/sales/action/", fromData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((result) => {
        window.parent.postMessage(
          JSON.stringify({
            action: "close_form",
          })
        );
      });}
  };
  formatDate = (days) => {
    const date = new Date();
    date.setDate(date.getDate() + days);
    return date;
  };

  formField = () => {
    let fields = [];
    fields.push( {
          name: "action_type",
          title: "Action type",
          input_type: "select",
          datasource: {
            data: [
              { value: "call", label: "Call" },
              { value: "email", label: "Email" },
              { value: "chat", label: "Chat" },
              { value: "offline_message", label: "Offline message" },
              { value: "remarks", label: "Remarks" },
              { value: "follow_up", label: "Follow up" },
              {
                value: "call_and_email",
                label: "Call and email",
              },
              { value: "call_and_message", label: "Call and message" },
            ],
          },
          sequence: 1,
        },
        {
          name: "action_tab",
          title: "Action tab",
          input_type: "select",
          datasource: {
            data: [
              { value: "due", label: "Follow ups" },
              { value: "done", label: "Processed" },
            ],
          },
          sequence: 2,
        },

        {
          name: "action_by",
          title: "Action by",
          input_type: "select",
          datasource: {
            name: "operators",
            query: "/dt/base/lookups/users/ ",
            parameters: [{ name: "name" }],
          },
          sequence: 3,
        },
        {
          name: "summary",
          title: "Remarks",
          input_type: "textarea",
          focus: true,
          validations: { required: true },
          sequence: 5,
        },
        {
          name: "attachment",
          title: "Attachment",
          input_type: "file",
          edit_button: true,
          post_only_if_touched: true,
          limit: 2,
          showInlinePreview: false,
          showUploadList: {
            showRemoveIcon: true,
            removeIcon: <DeleteOutlined style={{ color: "#EC7070" }} />,
          },
          sequence: 6,
        },
        {
          name: "remainder_date",
          title: "Remind me to follow up on",
          input_type: "date",
        },
        )

      if(this.state.isEdit == undefined && this.state.isEdit != true && this.state.is_legal !== "true"){
        fields.splice(3,0,{
          name: "scope",
          title: "Scope",
          input_type: "select",
          sequence: 4,
          datasource: {
            data: [
              { value: "invoice_level", label: "Invoice level" },
              { value: "customer_level", label: "Customer level" },
            ],
          },
      })
    };


    return fields
  };
  appSchema = {
    pageTitle: "Add Action",
    style: { width: "85%", height: "85vh" },
    formSchema: {
      init_data: {
        // api :"/dt/accounts/user/get_profile/",
        api: "/dt/sales/action/edit_action/",
        post_data: { action_id: this.props.action_id, user_id: this.user_id },
        form_data: { action_type: "call", action_by: this.user_id, next_action_by: this.user_id, next_action_type: "call" },
      },
      //  on_submit: {
      //   api: "/dt/sales/action/edit_action/",
      //   post_data: { action_id : this.props.action_id },
      //   afterSubmit: () => {
      //     this.appModal.hideModal();
      //   },
      // },
      edit_button: this.state.isEdit,
      submit_button: false,
      readonly: false,
      buttons: [
        {
          name: "save_actions",
          title: "Save",
          tooltip: "Save",
          type: "primary",
          sequence: 1,
          click_handler: (form_data) => {
            this.addAction(form_data);
          },
        },
      ],
      fields:this.formField(),
    },

  };

  render() {
    return (
      <>
        <DataForm
          disabled={true}
          schema={this.appSchema}
          initData={this.state}
          isModal={true}
          height={550}
          ref={(node) => {
            this.dataForm = node;
          }}
        ></DataForm>
      </>
    );
  }
}
Action.getInitialProps = async (context) => {
  return {
    is_legal: context.query.is_legal ?? false,
    customerId: context.query.add_action[0],
    invoiceId: context.query.add_action[1],
    action_id: context.query.action_id ?? 0,
    isEdit: context.query.is_edit,
    action_status: context.query.action_status,
    isModal: true,
  };
};
export default Action;
