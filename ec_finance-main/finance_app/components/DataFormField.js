import { Modal, DatePicker, Form, Input, InputNumber, Checkbox } from "antd";
import React, { lazy, Suspense, useEffect, useState } from "react";
import moment from "moment";
import shortid from "shortid";
import FileUpload from "./FileUpload";
//import Editor from "./Editor";
import SearchInput from "./SelectInput";
const { confirm } = Modal;
const { TextArea } = Input;
const DataFormField = ({ fieldProps, disabled, form, customValue }) => {
  const [formField, setFormField] = useState({});
  const [validationsRules, setValidationsRules] = useState([{}]);
  const [formCustomFieldValue, SetFormCustomFieldValue] = useState(customValue);
  useEffect(() => {
    const FieldFactory = {
      text: {
        getField: () => <Input placeholder={fieldProps.place_holder} disabled={disabled} />,
      },
      password: {
        getField: () => <Input.Password placeholder={fieldProps.place_holder} disabled={disabled} />,
      },
      custom: {
        getField: async () => {
          const CustomComponent = await lazy(() => import(`${fieldProps.component_path}`));
          return (
            <CustomComponent
              data={fieldProps.value}
              form={form}
              fieldProps={fieldProps}
              disabled={disabled}
              key={shortid.generate()}
              customValue={formCustomFieldValue}
            ></CustomComponent>
          );
        },
      },
      date: {
        getField: () => {
          let defaultValue = null;
          if (fieldProps.default_value) {
            defaultValue = moment(fieldProps.default_value, "YYYY-MM-DD");
          }
          return <DatePicker placeholder={fieldProps.place_holder} defaultValue={defaultValue} disabled={disabled} />;
        },
      },
      editor: {
        //getField: () => <Editor placeholder={fieldProps.place_holder} disabled={disabled} form={form} fieldProps={fieldProps} />,
      },
      select: {
        getField: () => <SearchInput form={form} disabled={disabled} placeholder={fieldProps.place_holder} fieldProps={fieldProps} />,
      },
      number: {
        getField: () => <InputNumber placeholder={fieldProps.placeholder} disabled={disabled} style={{ width: "100%" }} />,
      },
      checkbox: {
        getField: () => <Checkbox placeholder={fieldProps.placeholder} disabled={disabled} style={{ width: "100%" }} />,
      },
      email: {
        getField: () => <Input placeholder={fieldProps.placeholder} disabled={disabled} />,
      },
      label: {
        getField: () => <span>{fieldProps.value}</span>,
      },
      textarea: {
        getField: () => <TextArea rows={4} placeholder={fieldProps.placeholder} disabled={disabled} style={{ width: "100%" }} autoFocus={fieldProps.focus} />,
      },
      link: {
        getField: () => (
          <a href={fieldProps.href} target={fieldProps.target} disabled={disabled} onClick={!disabled ? fieldProps.click_handler : () => {}}>
            {fieldProps.title}
          </a>
        ),
      },
      file: {
        getField: () => (
          <FileUpload
            name={fieldProps.name}
            data={fieldProps.value}
            form={form}
            disabled={disabled}
            fieldProps={fieldProps}
            key={shortid.generate()}
          ></FileUpload>
        ),
      },
    };

    let validationsRules = [];
    if (fieldProps.validations) {
      validationsRules.push(fieldProps.validations);
    }
    setValidationsRules(validationsRules);
    let formField = {};
    if (fieldProps.input_type == "custom") {
      FieldFactory[fieldProps.input_type].getField().then((comp) => {
        formField = { field: comp };
        setFormField(formField);
      });
    } else {
      formField = { field: FieldFactory[fieldProps.input_type].getField() };
      setFormField(formField);
    }
  }, []);

  return (
    <Form.Item
      name={fieldProps.name}
      label={fieldProps.title}
      valuePropName={fieldProps.input_type == "checkbox" ? "checked" : "value"}
      tooltip={fieldProps.tooltip}
      rules={validationsRules}
    >
      {fieldProps.input_type !== "custom" ? formField.field : <Suspense fallback="Loading...">{formField.field}</Suspense>}
    </Form.Item>
  );
};

export default DataFormField;
