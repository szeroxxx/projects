import { Button, Form, Input, Modal } from "antd";
import axios from "axios";
import { getSession, signOut } from "next-auth/react";
import Router from "next/router";
import React from "react";
import { showMessage } from "../../common/Util";
import DataForm from "../../components/DataForm";
import PageTitle from "../../components/PageTitle";
class MyProfile extends React.Component {
  //TODO: Reload page only when them is modified on submit
  user_id = this.props.session.user.data.user_id;
  state = { data: {}, isModalVisible: false, height: 250 };
  formRef = React.createRef();
  appSchema = {
    pageTitle: "My Profile",
    formSchema: {
      init_data: {
        api: "/dt/accounts/user/get_profile/",
        post_data: { user_id: this.user_id },
      },
      on_submit: {
        api: "/dt/accounts/user/save_profile/",
        post_data: { user_id: this.user_id },
        afterSubmit: (data) => {
          data["user__first_name"] = data.user.first_name;
          data["user__last_name"] = data.user.last_name;
          axios.get(`/api/auth/session?update=${JSON.stringify(data)}`).then(() => {
            // Reloading page in getSession resolve ensures that session update promise is resolved
            // Therefore on page load, correct data will be applied which is dependant on session like a theme.
            getSession().then(Router.reload());
          });
        },
      },
      hide_buttons: false,
      readonly: false,
      columns: 1,
      fields: [
        {
          name: "profile_image",
          title: "Profile Image",
          input_type: "file",
          edit_button: true,
          post_only_if_touched: true,
          limit: 1,
          listType: "picture-card",
          showInlinePreview: true,
          accept: "image/*",
        },
        {
          name: "user__first_name",
          title: "First Name",
          input_type: "text",
          place_holder: "Enter your first name",
          validations: { required: true },
        },
        {
          name: "user__last_name",
          title: "Last Name",
          input_type: "text",
          place_holder: "Enter your last name",
          validations: { required: true },
        },
        {
          name: "user__email",
          title: "Email",
          input_type: "label",
        },
        {
          name: "",
          title: "Change password",
          input_type: "link",
          href: "#",
          click_handler: () => {
            this.setState({ isModalVisible: true });
          },
        },
        {
          name: "display_row",
          title: "Default list rows",
          input_type: "select",
          datasource: {
            data: [
              { value: 5, label: "5" },
              { value: 10, label: "10" },
              { value: 25, label: "25" },
              { value: 50, label: "50" },
              { value: 100, label: "100" },
            ],
          },
        },
        {
          input_type: "custom",
          name: "theme",
          title: "Select your theme",
          component_path: "./account/ThemeSelection",
        },
      ],
    },
  };
  onFinish = (values) => {
    console.log(values, "values");
    values["user_id"] = this.user_id;
    axios.post("/dt/accounts/user/change_password/", values).then((response) => {
      if (response.data.code == 1) {
        showMessage(response.data.message, "", "success");
        this.setState({ isModalVisible: false });
        signOut({
          callbackUrl: `${window.location.origin}`,
        });
      } else {
        showMessage(response.data.message, "", "error");
      }
    });
  };
  onCancel = () => {
    this.setState({ isModalVisible: false });
  };
  changeHeight = (e) => {
    if (e.target.value.length >= 1) {
      this.setState({ height: 420 });
    }
  };
  onFinishFailed = (e) => {
    this.setState({ height: 420 });
  };
  render() {
    return (
      <div>
        <PageTitle pageTitle={this.appSchema.pageTitle}></PageTitle>
        <div className="profile_layout">
          <DataForm schema={this.appSchema} initData={this.state}></DataForm>
        </div>
        <Modal
          title="Change password"
          visible={this.state.isModalVisible}
          width={700}
          bodyStyle={{ height: this.state.height }}
          footer={false}
          onCancel={this.onCancel}
        >
          <Form
            onFinishFailed={this.onFinishFailed}
            labelCol={{ span: 5 }}
            wrapperCol={{ span: 16 }}
            onFinish={this.onFinish}
            ref={(element) => (this.divRef = element)}
          >
            <Form.Item
              label="Current password"
              name="old_password"
              validateTrigger={["onKeyDown"]}
              rules={[
                { required: true, message: "Please input your current password!" },
                {
                  async validator(rule, value) {
                    if (value != undefined) {
                      if (value.trim().length == 0) {
                        return Promise.reject("Do not allow white space");
                      }
                    }
                  },
                  validateTrigger: "onChange",
                },
              ]}
            >
              <Input.Password pattern="[^\s]+" />
            </Form.Item>

            <Form.Item
              label="New password"
              name="new_password"
              validateTrigger={["onChange"]}
              rules={[
                {
                  required: true,
                  message: "Your password must meet the following requirements:",
                  validateTrigger: "onChange",
                },
                {
                  async validator(rule, value) {
                    if ((value || "").length >= 8 && value != undefined) {
                      return Promise.resolve();
                    } else {
                      return Promise.reject(" At least 8 characters");
                    }
                  },
                  validateTrigger: "onChange",
                },
                {
                  async validator(rule, value) {
                    let regex = new RegExp("[^&\\;<>]*[^a-zA-Z0-9&\\;<>][^&\\;<>]*");
                    if (regex.test(value) && value != undefined) {
                      return Promise.resolve();
                    }
                    return Promise.reject(" At least one special character");
                  },
                  validateTrigger: "onChange",
                },
                {
                  async validator(rule, value) {
                    let regex = new RegExp("[A-Z]+");
                    if (regex.test(value) && value != undefined) {
                      return Promise.resolve();
                    }
                    return Promise.reject(" At least one capital letter");
                  },
                  validateTrigger: "onChange",
                },
                {
                  async validator(rule, value) {
                    let regex = new RegExp("[0-9]+");
                    if (regex.test(value) && value != undefined) {
                      return Promise.resolve();
                    }
                    return Promise.reject(" At least one digit");
                  },
                  validateTrigger: "onChange",
                },
                {
                  async validator(rule, value) {
                    let regex = new RegExp("[a-z]+");
                    console.log(value, "regex.test(value)");
                    if (regex.test(value) && value != undefined) {
                      console.log("At least one small letter");
                      return Promise.resolve();
                    }
                    return Promise.reject(" At least one small letter");
                  },
                  validateTrigger: "onChange",
                },
              ]}
            >
              <Input.Password onChange={this.changeHeight} />
            </Form.Item>
            <Form.Item
              label="Confirm password"
              name="c_password"
              dependencies={["new_password"]}
              rules={[
                { required: true, message: "Please input your confirm password!" },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue("new_password") === value) {
                      return Promise.resolve();
                    } else {
                      return Promise.reject(new Error("The two passwords that you entered do not match!"));
                    }
                  },
                }),
              ]}
            >
              <Input.Password />
            </Form.Item>
            <Form.Item style={{ float: "right", marginRight: 80, paddingBottom: 40 }}>
              <Button type="primary" htmlType="submit">
                Change Password
              </Button>
            </Form.Item>
          </Form>
        </Modal>
      </div>
    );
  }
}

export default MyProfile;
