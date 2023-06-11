import { Upload, Button, Avatar, Image } from "antd";
import React from "react";
import { UploadOutlined } from "@ant-design/icons";

//TODO: Give more generic name like FileField and add props like type="image", preview="true"
class FileUpload extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      files: this.props.fieldProps.value || [],
    };
  }

  componentDidMount() {
    if (this.props.fieldProps.showInlinePreview && this.state.files.length > 0) {
      this.setState({ inlineImagePreviewSrc: this.state.files[0].url });
    }
  }
  onRemove = (file) => {
    var filtered = this.state["files"].filter(function (el) {
      return el.uid != file.uid;
    });
    this.setState({
      files: filtered || [],
    });
  };
  dummyRequest = ({ file, onSuccess }, multiple, limit) => {
    const reader = new FileReader();

    //TODO: Reader should executed only for Image file.
    //TODO: Test Case1: Test using different types of files
    //TODO: Test Case2: Test using multiple files with combination of different file.
    reader.onloadend = async () => {
      this.props.fieldProps.handleFiles(this.props.name, file);
      if (this.props.fieldProps.showInlinePreview) this.setState({ inlineImagePreviewSrc: reader.result });

      this.setState({
        files: [
          ...this.state["files"],
          {
            uid: new Date().getMilliseconds(),
            postKey: this.props.name,
            name: file.name,
            status: "done",
            url: reader.result,
            file: file,
          },
        ].slice(0, multiple ? (limit > -1 ? limit : this.state.files.length + 1) : 1),
      });
    };

    if (file) {
      reader.readAsDataURL(file);
    }
    setTimeout(() => {
      onSuccess("ok");
    }, 0);
  };

  render() {
    const {
      accept = this.props.fieldProps.accept ?? "*",
      limit = this.props.fieldProps.limit ?? 1,
      showUploadList = this.props.fieldProps.showUploadList ?? false,
      showInlinePreview,
      listType = this.props.fieldProps.listType ?? "",
    } = this.props.fieldProps;

    let multipleSelection = limit > 1;
    if (showInlinePreview && limit > 1) {
      throw new Error("Inline file preview only possible for single file per upload control. Use showUploadList configuration.");
    }

    let { files, inlineImagePreviewSrc } = this.state;

    const uploadButton = () => {
      return showInlinePreview ? (
        inlineImagePreviewSrc ? (
          <Image alt="Image" preview={false} src={inlineImagePreviewSrc} style={{ width: "100%" }} />
        ) : (
          <Avatar size={80} src={`/man.png`} shape="square" />
        )
      ) : files.length >= limit ? null : (
        <Button icon={<UploadOutlined />}>Click to Upload</Button>
      );
    };

    return (
      <>
        <Upload
          disabled={this.props.disabled}
          maxCount={limit}
          multiple={multipleSelection}
          accept={accept}
          listType={listType}
          fileList={files}
          showUploadList={showUploadList}
          onRemove={this.onRemove}
          customRequest={(f) => this.dummyRequest(f, multipleSelection, limit)}
        >
          {uploadButton()}
        </Upload>
      </>
    );
  }
}

export default FileUpload;
