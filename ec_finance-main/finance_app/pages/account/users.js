import React, { Component } from "react";
import ActionPanel from "../../components/ActionPanel";
import AppModal from "../../components/AppModal";
import DataGridViewer from "../../components/DataGridViewer";
import PageTitle from "../../components/PageTitle";

class Users extends Component {
  state = { data: {} };

  appSchema = {
    pageTitle: "Users",
    buttons: [
      {
        name: "new_user",
        title: "Add new",
        primary: "primary",
        icon_code: "UserAddOutlined",
        tooltip: "",
        sequence: 1,
        click_handler: () => {
          this.addUser();
        },
      },
      {
        name: "edit",
        title: "Edit",
        primary: "primary",
        icon_code: "EditOutlined",
        tooltip: "",
        sequence: 1,
        click_handler: () => {
          var data = this.dataGridViewer.getSelectedRows();
          this.editUser(data);
        },
        multi_select: false,
      },
    ],
    listing: [
      {
        search: [
          { key: "first_name", label: "First Name" },
          { key: "last_name", label: "Last Name" },
          { key: "username", label: "User Name" },
          { key: "usergroup", label: "Role" },
        ],
        dataGridUID: "users",
        url: "/dt/accounts/users",
        paging: true,
        default_sort_col: "id",
        default_sort_order: "descend",
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
            value: "first_name",
            text: "First Name",
            sortable: true,
            width: 300,
            sequence: 2,
          },

          {
            value: "last_name",
            text: "Last Name",
            sortable: true,
            sequence: 3,
          },
          {
            value: "username",
            text: "User Name",
            sortable: true,
          },
          {
            value: "usergroup",
            sortable: true,
            text: "Role",
          },
        ],
      },
    ],
  };
  formField = (is_edit) => {
    let fields = [];
    fields.push(
      {
        name: "first_name",
        title: "First name",
        input_type: "text",
        place_holder: "First name",
        validations: { required: true },
        sequence: 1,
      },
      {
        name: "last_name",
        title: "Last name",
        input_type: "text",
        place_holder: "Last name",
        validations: { required: true },
        sequence: 2,
      },
      {
        name: "email",
        title: "Email",
        input_type: "text",
        tooltip: "Email",
        place_holder: "Email",
        validations: { required: true, type: "email" },
        sequence: 3,
      },
      {
        name: "role_ids",
        title: "Role",
        input_type: "select",
        datasource: {
          name: "user_roles",
          query: "/dt/accounts/user_roles/",
          parameters: [{ name: "name" }],
        },
        place_holder: "Search role",
        mode: "multiple",
        validations: { required: true },
        sequence: 6,
      },
      {
        name: "is_active",
        title: "Active",
        input_type: "checkbox",
        validations: { required: true },
      }
    );
    if (is_edit == false) {
      fields.push(
        {
          name: "password",
          title: "Password",
          input_type: "password",
          tooltip: "Password",
          place_holder: "Password",
          validations: { required: true },
          sequence: 4,
        },
        {
          name: "password2",
          title: "Confirm password",
          input_type: "password",
          tooltip: "Password",
          place_holder: "Confirm Password",
          validations: { required: true },
          sequence: 5,
        }
      );
    }
    return fields;
  };
  getUserSchema = (userId, submitApi, init_data, is_edit) => {
    var userSchema = {
      pageTitle: "User",
      style: { width: "85%", height: "relative" },
      formSchema: {
        init_data: init_data,
        edit_button: is_edit,
        on_submit: {
          api: submitApi,
          post_data: { user_id: userId },
          afterSubmit: () => {
            this.appModal.hideModal();
            this.dataGridViewer.refresh();
          },
        },
        readonly: false,
        columns: 1,
        fields: this.formField(is_edit),
        buttons: [],
      },
    };
    return userSchema;
  };
  componentDidMount = () => {
    // call function if needed on component load.
  };
  addUser = () => {
    this.appModal.show({ schema: this.getUserSchema(0, "/dt/accounts/user/create_user/", {}, false) });
  };
  editUser = (data) => {
    var init_data = {
      api: "/dt/accounts/user/get_user/",
      post_data: { user_id: data[0].id },
    };
    this.appModal.show({ schema: this.getUserSchema(data[0].id, "/dt/accounts/user/update_user/", init_data, true) });
  };
  rowSelectionChange = (key, selectedRows) => {
    this.setState((prevState) => ({
      data: { ...prevState.data, [key]: selectedRows },
    }));
  };

  render() {
    return (
      <div>
        <PageTitle pageTitle={this.appSchema.pageTitle}></PageTitle>
        <ActionPanel buttons={this.appSchema.buttons} selectedRows={this.state.data[this.appSchema.listing[0].dataGridUID]} />
        <DataGridViewer
          schema={this.appSchema.listing[0]}
          onRowSelectionChange={this.rowSelectionChange}
          ref={(node) => {
            this.dataGridViewer = node;
          }}
        ></DataGridViewer>
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

export default Users;
