import { ExclamationCircleOutlined } from "@ant-design/icons";
import { Affix, Button, Col, Form, Modal, notification, Row, Space, Tabs } from "antd";
import axios from "axios";
import React from "react";
import shortid from "shortid";
import Constant from "../common/Constant";
import ActionPanel from "./ActionPanel";
import DataFormField from "./DataFormField";
import DataGridViewer from "./DataGridViewer";

const { confirm } = Modal;
const { TabPane } = Tabs;
class DataForm extends React.Component {
  //TODO: On cancel form clear selected files to avoid posting next time unwontedly

  formRef = React.createRef();
  formSchema = this.props.schema.formSchema;
  validateMessages = {
    required: "${label} is required!",
    types: {
      email: "${label} is not a valid email!",
      number: "${label} is not a valid number!",
    },
    number: {
      range: "${label} must be between ${min} and ${max}",
    },
  };
  constructor(props) {
    super(props);
    this.state = { formData: {} };

    if (this.formSchema.disabled) {
      this.state["disabled"] = this.formSchema.disabled;
    }
    if (this.formSchema.tabs) {
      this.state["activeTabId"] = this.formSchema.tabs[this.props.activeTab ?? 0].UID;
    }
    if (this.props.activeTabUID) {
      this.state["activeTabId"] = this.props.activeTabUID;
    }
    if (!this.formSchema.hasOwnProperty("edit_button")) {
      this.formSchema["edit_button"] = true;
    }
    if (this.formSchema.edit_button) {
      this.state["disabled"] = true;
    }
    if (!this.formSchema.hasOwnProperty("submit_button")) {
      this.formSchema["submit_button"] = true;
    }

    this.dataGridViewer = {};
    this.selectedFileFields = [];
  }

  handleFiles = (name, file) => {
    this.selectedFileFields.push(name);
    let fileFieldsValue = this.formRef.current.getFieldValue(name);

    if (typeof fileFieldsValue || typeof fileFieldsValue === "string") {
      fileFieldsValue = [file];
    } else {
      fileFieldsValue.push(file);

      // If multiple time file selected on and off from file dialog then maintain proper files list for the post data
      const fieldMeta = this.getFieldSchema(name);
      const fileFileUploadLimit = fieldMeta.limit || 1;
      if (fileFieldsValue.length > fileFileUploadLimit) {
        if (fileFileUploadLimit == 1) {
          // If single file allowed, always keep last selected file.
          fileFieldsValue = fileFieldsValue.slice(fileFileUploadLimit, fileFileUploadLimit + 1);
        } else {
          // If multiple files allowed and selected more then allowed files then set top files based on selected
          fileFieldsValue = fileFieldsValue.slice(0, fileFileUploadLimit);
        }
      }
    }

    this.formRef.current.setFieldsValue({ [name]: fileFieldsValue });
  };
  searchData = (GridUID, searchData) => {
    if (this.dataGridViewer[GridUID]) {
      this.dataGridViewer[GridUID].searchData(searchData);
    }
    return [];
  };

  clearFormFieldsSelectedFiles() {
    this.selectedFileFields.forEach((field) => this.formRef.current.setFieldsValue({ [field]: [] }));
  }
  showMessage = (type, message) => {
    //type 'success','info' ,'warning','error'
    //{ message: "Failed to set form data!", description: "description" }
    notification[type](message);
  };
  getFormData = () => {
    return this.formRef.current.getFieldsValue(true);
  };
  getSelectedRows = (GridUID) => {
    if (this.state.gridViewSelectedData && this.state.gridViewSelectedData[GridUID]) {
      return this.state.gridViewSelectedData[GridUID];
    }
    return [];
  };
  refreshTable = (GridUID) => {
    if (this.dataGridViewer[GridUID]) {
      this.dataGridViewer[GridUID].refresh();
    }
  };
  getDataSource = (GridUID) => {
    if (this.dataGridViewer[GridUID]) {
      return this.dataGridViewer[GridUID].getDataSource();
    }
    return [];
  };
  componentDidMount() {
    this.setFormData();
  }
  async setFormData() {
    if (this.formSchema.init_data === undefined) return;

    const { api, post_data, form_data } = this.formSchema.init_data;
    // Fetch data from specified API and set value in the fields
    if (api !== undefined) {
      form_data = await this.fetchFormData(api, post_data);
    }

    // Set value in the fields from the fixed data specified in field_data object
    if (form_data !== undefined) {
      // Few input components state value dependant on the assigned value in pops by setFieldValueToSchema.
      // So it is required to call setFieldValueToSchema before the setState of form in order to render child inputs with correct value.
      this.setFieldValueToSchema(form_data);
      this.formRef.current.setFieldsValue(form_data);
      this.setState({ formData: form_data }, () => {});
    }
  }
  async fetchFormData(api, post_data) {
    let bodyFormData = new FormData();
    for (let [key, value] of Object.entries(post_data)) {
      bodyFormData.append(key, value);
    }

    const response = await axios.post(api, bodyFormData);
    if (response.code == 0) {
      notification["error"]({ message: "Failed to set form data!", description: result.data.message });
      return;
    }
    return response.data.data;
  }
  getDataGridViewer = (listing, isFromTab) => {
    let itemList = [];
    let style = { minWidth: "30%" };
    if (isFromTab) {
      style = { minWidth: "30%", marginTop: "-60px" };
    }
    if (listing) {
      listing.forEach((item, index) => {
        itemList.push(
          <DataGridViewer
            key={index}
            schema={listing[index]}
            searchStyle={style}
            onRowSelectionChange={this.rowSelectionChange}
            ref={(dataGridViewer) => {
              this.dataGridViewer[listing[index].dataGridUID] = dataGridViewer;
            }}
          ></DataGridViewer>
        );
      });
    }
    return itemList;
  };
  getDataFormField = (fields) => {
    let dataFields = [];
    {
      fields &&
        fields.map((field) => {
          field = {
            ...field,
            handleFiles: this.handleFiles,
          };
          dataFields.push(
            <Col span={24 / (this.formSchema.columns ?? 1)} key={field.name}>
              <DataFormField
                customValue={this.state.gridViewSelectedData}
                form={this.formRef}
                value={field.value}
                key={shortid.generate()}
                fieldProps={field}
                disabled={this.state.disabled}
              ></DataFormField>
            </Col>
          );
        });
    }
    return <Row gutter={24}>{dataFields}</Row>;
  };
  onTabChange = (key) => {
    this.setState({ activeTabId: key });
  };
  editForm = (editable) => {
    this.setState({ disabled: editable });
  };
  geTabs = (tabs) => {
    let tabList = [];
    let hasTabs = false;
    if (tabs) {
      tabs.forEach((item, index) => {
        tabList.push(
          <TabPane tab={tabs[index].label} key={tabs[index].UID}>
            {this.getDataFormField(tabs[index].fields)}
            {this.getDataGridViewer(tabs[index].listing, true)}
            {this.geTabs(tabs[index].tabs)}
          </TabPane>
        );
      });
      hasTabs = true;
    }
    if (hasTabs) {
      return (
        <Tabs defaultActiveKey={tabs[this.props.activeTab ?? 0].UID} onChange={this.onTabChange}>
          {tabList}{" "}
        </Tabs>
      );
    }

    return <></>;
  };
  getFormButton = () => {
    let buttons = [];
    let hasButton = false;
    let Gui = "";
    if (this.props.schema.formSchema.buttons) {
      this.props.schema.formSchema.buttons.forEach((item, index) => {
        if (this.props.schema.formSchema.buttons[index].dataGridUID) {
          Gui = this.props.schema.formSchema.buttons[index].dataGridUID;
          buttons.push(this.props.schema.formSchema.buttons[index]);
          hasButton = true;
        }
      });
    }
    if (hasButton) {
      return <ActionPanel key={shortid.generate()} buttons={buttons} selectedRows={this.getSelectedRows(Gui)} />;
    }
    return "";
  };
  getTabActionPanel = (tabUID) => {
    let actionPanel = [];
    let hasTabs = false;
    if (this.formSchema.tabs) {
      actionPanel=this.getTabActionButton(this.formSchema.tabs,tabUID);
    }
    if (actionPanel.length>0) {
      return <>{actionPanel} </>;
    }

    return <></>;
  };
  getTabActionButton=(tabs,tabUID)=>{
    let actionPanel = [];
    tabs.forEach((item, index) => {
      if (tabs[index].tabs) {
        var action= this.getTabActionButton(tabs[index].tabs,tabUID);
        if(action.length>0){
          actionPanel.push(action);
        }
      }
      if (tabs[index].UID == tabUID && tabs[index].buttons) {
        if (tabs[index].listing) {
          actionPanel.push(
            <ActionPanel
              key={shortid.generate()}
              buttons={tabs[index].buttons}
              selectedRows={this.getSelectedRows(tabs[index].listing[0].dataGridUID)}
            />
          );
        } else if (tabs[index].buttons[0].dataGridUID) {
          actionPanel.push(
            <ActionPanel
              key={shortid.generate()}
              buttons={tabs[index].buttons}
              selectedRows={this.getSelectedRows(tabs[index].buttons[0].dataGridUID)}
            />
          );
        } else {
          actionPanel.push(<ActionPanel key={shortid.generate()} buttons={tabs[index].buttons} />);
        }
      }
    });
    return actionPanel;
  };
  setFieldValueToSchema = (formData) => {
    if (this.formSchema.fields) {
      this.formSchema.fields.map((field) => {
        field["value"] = formData[field.name];
        if (field.input_type == "select") {
          //Assuming if input type is select value then its display value passed in form data having same name as id field with "display" prefix
          field["display_value"] = formData["display_" + field.name];
        }

        if (field.input_type == "file" && formData[field.name]) {
          field["value"] = [
            {
              uid: "-1",
              name: field.name,
              status: "done",
              url: formData[field.name],
            },
          ];
        }
      });
    }
    if (this.formSchema.tabs) {
      this.formSchema.tabs.forEach((item, index) => {
        if (this.formSchema.tabs[index].fields) {
          this.formSchema.tabs[index].fields.map((field) => {
            field["value"] = formData[field.name];
            if (field.input_type == "select") {
              //Assuming if input type is select value then its display value passed in form data having same name as id field with "display" prefix
              field["display_value"] = formData["display_" + field.name];
            }
            if (field.input_type == "file" && formData[field.name]) {
              field["value"] = [
                {
                  uid: "-1",
                  name: field.name,
                  status: "done",
                  url: formData[field.name],
                },
              ];
            }
          });
        }
      });
    }
  };
  rowSelectionChange = (key, selectedRows) => {
    this.setState((prevState) => ({
      gridViewSelectedData: { ...prevState.data, [key]: selectedRows },
    }));
  };
  clickHandler = (button) => {
    this.formRef.current
      .validateFields()
      .then((values) => {
        if (button.click_handler) {
          button.click_handler({ form: this.formRef.current, values: values });
        } else if (button.confirm) {
          confirm({
            title: button.confirm.title,
            icon: <ExclamationCircleOutlined />,
            content: button.confirm.content,
            okText: button.confirm.okText ?? "Ok",
            cancelText: button.confirm.cancelText ?? " cancel",
            onOk() {
              button.confirm.onOk({ form: this.formRef.current, values: values });
            },
            onCancel() {},
          });
        }
      })
      .catch((errorInfo) => {});
  };
  getFieldSchema = (fieldName) => {
    const fieldMeta = this.formSchema.fields.filter(function (field) {
      return field.name == fieldName;
    });
    return fieldMeta.length > 0 ? fieldMeta[0] : null;
  };
  isFieldTouchedCheckConfigured = (fieldName) => {
    const fieldMeta = this.getFieldSchema(fieldName);

    if (fieldMeta && fieldMeta.post_only_if_touched) {
      return true;
    }
    return false;
  };
  onSubmit = () => {
    this.formRef.current.validateFields().then((values) => {
      const { api, post_data, afterSubmit } = this.formSchema.on_submit;

      const formValues = { ...values, ...post_data };
      const fromData = new FormData();
      for (let [key, value] of Object.entries(formValues)) {
        // Post field value if touched configured then skip to add in FormData
        if (this.isFieldTouchedCheckConfigured(key) && this.formRef.current.isFieldTouched(key) == false) {
          console.log("File touch works");
          console.log("otherwise", value);
          continue;
        }

        if (Constant.POST_FK_FIELD_RULE === ".") {
          if (key.includes("__")) {
            key = key.replace(/__/g, ".");
          }

          // As of now, only File type field value can be as multiple if multiple file section allowed.
          // In that scenario, FormData is extended with different file object but with same form data key.
          if (!Array.isArray(value)) {
            fromData.append(key, value);
          } else {
            value.forEach((val) => fromData.append(key, val));
          }
        }
      }
      axios.post(api, fromData).then((result) => {
        if (result.data.code == 0) {
          notification["error"]({ message: "Not Saved!", description: result.data.message });
          return;
        }

        if (afterSubmit) {
          afterSubmit(result.data.data);
        }
      });
    });
  };
  onCancel = () => {
    this.editForm(true);
    this.clearFormFieldsSelectedFiles();
  };

  render() {
    const { schema } = this.props;
    let position = "fixed";
    let left = "253px";
    let minHeight = "500px";
    if (this.props.isModal) {
      if (!this.props.isFrame) {
        position = "absolute";
      }
      if (this.props.height) {
        minHeight = this.props.height - 5 + "px";
      }
      left = "10px";
    }
    return (
      <>
        {!schema.formSchema.hide_buttons && schema.formSchema.buttons_position == "top" && <>{this.getTabActionPanel(this.state.activeTabId)}</>}
        {!schema.formSchema.hide_buttons && schema.formSchema.buttons_position == "top" && <>{this.getFormButton()}</>}
        <fieldset style={{width:"100%"}}>
          <Form

            name="basic"
            style={{ position: "relative", minHeight: minHeight }}
            validateMessages={this.validateMessages}
            labelAlign="left"
            layout="horizontal"
            labelCol={{ lg: { span: 5 }, xl: { span: 4 }, md: { span: 6 } }}
            wrapperCol={{ span: 12 }}
            ref={this.formRef}
          >
            <fieldset>
              {this.getDataFormField(schema.formSchema.fields)}
              {this.getDataGridViewer(schema.formSchema.listing)}
              {this.geTabs(schema.formSchema.tabs)}
            </fieldset>
            {schema.formSchema.buttons_position != "top" && (
              <Affix
                offsetBottom={0}
                style={{
                  bottom: "0",
                  paddingTop: "10px",
                  position: position,
                  borderTop: "solid 1px #e6e6e6",
                  right: "30px",
                  left: left,
                  minHeight: "50px",
                  backgroundColor: "white",
                }}
              >
                {!schema.formSchema.hide_buttons && (
                  <div>
                    {schema.formSchema.buttons_position != "top" && (
                      <div
                        style={{
                          float: "left",
                        }}
                      >
                        <Form.Item>
                          <Space>{this.getTabActionPanel(this.state.activeTabId)}</Space>
                        </Form.Item>
                      </div>
                    )}
                    <div
                      style={{
                        float: "right",
                      }}
                    >
                      <div>
                        <Form.Item>
                          <Space>
                            {schema.formSchema.buttons &&
                              schema.formSchema.buttons.map((button) =>
                                !button.dataGridUID ? (
                                  <Button
                                    key={shortid.generate()}
                                    disabled={this.state.disabled}
                                    danger={button.style == "danger" ? true : false}
                                    type={button.type}
                                    onClick={() => this.clickHandler(button)}
                                  >
                                    {button.title}
                                  </Button>
                                ) : null
                              )}
                            {schema.formSchema.submit_button && !this.state.disabled && (
                              <Button key="784528_submit" disabled={this.state.disabled} danger={false} type="primary" onClick={() => this.onSubmit()}>
                                Submit
                              </Button>
                            )}
                            {schema.formSchema.edit_button && !schema.formSchema.readonly && (
                              <>
                                {this.state.disabled && (
                                  <Button key="784528_Edit" danger={false} htmlType="button" onClick={() => this.editForm(false)}>
                                    Edit
                                  </Button>
                                )}

                                {!this.state.disabled && (
                                  <Space>
                                    <Button key="784528_Cancrl" htmlType="button" danger={false} onClick={this.onCancel}>
                                      Cancel
                                    </Button>
                                  </Space>
                                )}
                              </>
                            )}
                          </Space>
                        </Form.Item>
                      </div>
                    </div>
                  </div>
                )}
              </Affix>
            )}
          </Form>
        </fieldset>
      </>
    );
  }
}

export default DataForm;
