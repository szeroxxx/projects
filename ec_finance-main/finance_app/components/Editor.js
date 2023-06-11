
import dynamic from 'next/dynamic'
import React from "react";
const QuillNoSSRWrapper = dynamic(import('react-quill'), {	
	ssr: false,
	loading: () => <p>Loading ...</p>,
	})


  class Editor extends React.Component {
    constructor (props) {
      super(props)
      this.state = { editorHtml: '', theme: 'snow' }
      this.handleChange = this.handleChange.bind(this)
    }
    
    handleChange (html) {
        this.setState({ editorHtml: html });
        if(this.props.onChange){
        this.props.onChange(html);
        }
        if(this.props.form && this.props.fieldProps){
          const fieldsValues = {};
          fieldsValues[this.props.fieldProps.name] = html;
          this.props.form.current.setFieldsValue(fieldsValues);
      }
    }
    
    handleThemeChange (newTheme) {
      if (newTheme === "core") newTheme = null;
      this.setState({ theme: newTheme })
    }
    
    render () {
      let style={}
      if(this.props.disabled){
        style= {pointerEvents: "none",
        background: "#f5f5f5",
        cursor: "not-allowed"
      }
      }
      if(this.props.modules){
        Editor.modules = this.props.modules;
      }
      return (
       <div  style={style}>
          <QuillNoSSRWrapper 
            theme={this.state.theme}
            onChange={this.handleChange}
            value={this.state.editorHtml}
            modules={Editor.modules}
            formats={Editor.formats}
            defaultValue={this.props.value}
            placeholder={this.props.placeholder}
            enable={false}
           />
        </div>
       )
    }
  }
  
  /* 
   * Quill modules to attach to editor
   * See https://quilljs.com/docs/modules/ for complete options
   */
  Editor.modules = {
    toolbar: [
      [{ 'header': '1'}, {'header': '2'}, { 'font': [] }],
      [{size: []}],
      ['bold', 'italic', 'underline', 'strike', 'blockquote'],
      [{'list': 'ordered'}, {'list': 'bullet'}, 
       {'indent': '-1'}, {'indent': '+1'}],
      ['link', 'image', 'video'],
      ['clean']
    ],
    clipboard: {
      // toggle to add extra line breaks when pasting HTML:
      matchVisual: false,
    }
  }
  /* 
   * Quill editor formats
   * See https://quilljs.com/docs/formats/
   */
  Editor.formats = [
    'header', 'font', 'size',
    'bold', 'italic', 'underline', 'strike', 'blockquote',
    'list', 'bullet', 'indent',
    'link', 'image', 'video'
  ]
  
  /* 
   * PropType validation
   */

  export default Editor;