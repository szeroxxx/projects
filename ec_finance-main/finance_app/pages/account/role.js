import { Button, Card, Checkbox, Col, Divider, Form, Input, Menu, Row } from "antd";
import axios from "axios";
import React from "react";
import { showMessage } from "../../common/Util";
const CheckboxGroup = Checkbox.Group;
const { SubMenu } = Menu;
class Role extends React.Component {
  user_id = this.props.session.user.data.user_id;
  state = {
    menus: [],
    checked: false,
    module: [localStorage.getItem("openKeys")],
    name_status: "",
    disabled: this.props.role_id ? true : false,
    subModuleAllChecked: false,
    uniChecked: false,
    permissions: [],
    indeterminate: true,
    filtered_perms: [],
    all_perms: [],
    currentSubMenuIds: localStorage.getItem("content_ids"),
    uniIndeterminate: true,
    role_name: this.props.role_name,
    role_id: this.props.role_id,
    openKeys: [localStorage.getItem("openKeys")],
    content_id: localStorage.getItem("content_id"),
    currentMenuKey: localStorage.getItem("currentMenuKey"),
    currentSubMenuKey: localStorage.getItem("currentSubMenuKey"),
  };
  componentDidMount = () => {
    this.getMenus();
  };
  getMenus = () => {
    axios.get("/dt/accounts/role/get_role/?role_id=" + this.state.role_id).then((response) => {
      let data = response.data;
      let permissions = data.data.permissions;
      let applied_perms = data.data.applied_perms;
      let content_perms = permissions.filter((el) => parseInt(el.content_id) === parseInt(this.state.content_id));
      if (data.code == 1) {
        this.setState({
          menus: data.data.lists,
          permissions: permissions,
          applied_perms: applied_perms,
          checkedList: applied_perms,
          all_perms: applied_perms,
          filtered_perms: content_perms.map((el) => {
            return { label: el.act_name, value: el.id };
          }),
        });
      }
    });
  };
  handleClick = (e) => {
    let content_id = String(e.keyPath[0]).split(",")[1];
    let content_perms = this.state.permissions.filter((el) => parseInt(el.content_id) === parseInt(content_id));
    this.setState({
      currentMenuKey: e.keyPath[1],
      currentSubMenuKey: String(e.keyPath[0]).split(",")[0],
      filtered_perms: content_perms.map((el) => {
        return { label: el.act_name, value: el.id };
      }),
      content_id: content_id,
      all_perms: [...new Set(this.state.all_perms.concat(this.state.checkedList))],
      // checkedList: [...new Set(this.state.all_perms.concat(this.state.checkedList))],
    });

    localStorage.setItem("currentMenuKey", e.keyPath[1]);
    localStorage.setItem("currentSubMenuKey", String(e.keyPath[0]).split(",")[0]);
    localStorage.setItem("openKeys", e.keyPath[1]);
    localStorage.setItem("content_id", content_id);
  };

  onOpenChange = (items) => {
    const latestOpenKey = items.find((key) => this.state.openKeys.indexOf(key) === -1);
    let items_len = items.length == 2 ? items[1] : items[0];
    let opened_menus = this.state.menus.filter((x) => x.content_group === items_len);
    if (items !== undefined && opened_menus[0] !== undefined) {
      let ids = "";
      for (var row in opened_menus[0].content_name) {
        ids += String(opened_menus[0].content_name[row].id).trimEnd().trimStart() + ",";
      }
      localStorage.setItem("content_ids", ids);
      let content_id = opened_menus[0].content_name[0].id;
      let content_perms = this.state.permissions.filter((el) => parseInt(el.content_id) === parseInt(content_id));
      this.setState({
        currentSubMenuKey: opened_menus[0].content_name[0].content_name,
        currentSubMenuIds: ids,
        filtered_perms: content_perms.map((el) => {
          return { label: el.act_name, value: el.id };
        }),
      });
    }

    this.setState({ openKeys: latestOpenKey ? [latestOpenKey] : [], module: latestOpenKey !== undefined ? latestOpenKey : [localStorage.getItem("openKeys")] });
    if (items.length == 2) {
      this.setState({
        openedContent: items[1],
        all_perms: this.state.all_perms,
      });
    }
  };
  testFunc = () => {};
  onChange = (e) => {
    if (e.target.checked) {
      this.setState((state) => ({
        all_perms: [...new Set(state.all_perms.concat([e.target.value]))],
        checkedList: [...new Set(this.state.checkedList.concat([e.target.value]))],
      }));
    } else {
      this.setState((state) => ({
        all_perms: [...new Set(state.all_perms.filter((x) => e.target.value !== x))],
        checkedList: [...new Set([...this.state.checkedList].filter((x) => e.target.value !== x))],
      }));
    }
    // let removed_list2 = [...new Set([...this.state.checkedList].filter((x) => !this.state.all_perms.includes(x)))];
    // let all = [...new Set(this.state.all_perms.concat(list))];
    // this.setState((state) => ({
    //   all_perms: [...new Set(state.all_perms.concat(list))],
    //   checkedList: list,
    //   indeterminate: !!list.length && list.length < this.state.filtered_perms.length,
    //   subModuleAllChecked: list.length === this.state.filtered_perms.length,
    //   uniChecked: list.length === this.state.filtered_perms.length,
    // }));
    // let removed_list = [...new Set([...this.state.checkedList].filter((x) => !list.includes(x)))];
    // let final_list = [...new Set(this.state.all_perms.filter((x) => !removed_list.includes(x)))];
    // this.setState((state) => ({
    //   all_perms: final_list,
    // }));
  };

  // componentDidUpdate = (prevProps, prevState) => {
  //   if (prevState.checkedList !== this.state.checkedList) {
  //     this.setState((state) => ({
  //       all_perms: state.all_perms.concat(this.state.checkedList),
  //     }));
  //   }
  //   if (prevState.checkedList !== this.state.checkedList) {
  //     this.setState((state) => ({
  //       all_perms: state.all_perms.concat(this.state.checkedList),
  //     }));
  //   }
  // };

  removeFromArray = (arr, remove) => {
    return arr.filter((value) => !remove.includes(value));
  };

  subModuleAllCheck = (e) => {
    let checkedList = this.state.filtered_perms.map((el) => {
      return el.value;
    });
    let removeArr = this.removeFromArray(this.state.checkedList, [...new Set(checkedList)]);
    let contentPer = e.target.checked
      ? this.state.filtered_perms.map((el) => {
          return el.value;
        })
      : [];
    this.setState({
      checkedList: e.target.checked ? [...new Set(this.state.checkedList.concat(contentPer))] : removeArr,
      indeterminate: false,
      subModuleAllChecked: e.target.checked,
    });
  };
  uniCheck = (e) => {
    let ids = [];
    let curr_sub_ids = this.state.currentSubMenuIds.split(",");
    for (var prow in this.state.permissions) {
      for (var crow in curr_sub_ids) {
        if (parseInt(this.state.permissions[prow].content_id) === parseInt(curr_sub_ids[crow])) {
          ids.push(this.state.permissions[prow].id);
        }
      }
    }
    var allPerms = this.state.filtered_perms.map((el) => {
      return el.value;
    });
    var finalArr;
    if (e.target.checked == false) {
      finalArr = this.removeFromArray(this.state.all_perms, [...new Set(ids)]);
    } else {
      finalArr = [...new Set(this.state.all_perms.concat(ids))];
    }
    this.setState({
      checkedList: finalArr,
      uniIndeterminate: false,
      uniChecked: e.target.checked,
      subModuleAllChecked: e.target.checked,
      all_perms: finalArr,
    });
  };

  saveRole = (e) => {
    var postData = {
      user_id: this.user_id,
      role_id: this.props.role_id,
      name: this.state.role_name,
      role_perm: String([...new Set(this.state.all_perms)])
        .replace("]")
        .replace("["),
    };
    axios.post("/dt/accounts/role/create_and_update_role/", postData).then((response) => {
      var data = response.data;
      if (data.code == 1) {
        this.getMenus();
        window.parent.postMessage(
          JSON.stringify({
            action: "save",
          })
        );
        this.setState({
          disabled: !this.state.disabled,
        });
      } else {
        showMessage(data.message, "", "error");
      }
    });
  };
  render() {
    return (
      <>
        <div style={{ marginLeft: 20, marginTop: 10, minHeight: 500 }}>
          <Form>
            <Row>
              <Form.Item requiredMark={false} title="Role name" label="Role Name" required={true}>
                <Input
                  status={this.state.name_status}
                  value={this.state.role_name}
                  disabled={this.state.disabled}
                  // bordered={false}
                  // style={{ width: 500, borderTop: 0, borderLeft: 0, borderRight: 0 }}
                  style={{ width: 500 }}
                  onChange={(e) => {
                    this.setState({ role_name: e.target.value });
                  }}
                ></Input>
              </Form.Item>
            </Row>
            <Row>
              <Card
                size="large"
                style={{
                  minWidth: 300,
                  minHeight: 500,
                  borderRight: "none",
                }}
              >
                <p>Set rights for role:</p>
                <Col span={8}>
                  <Menu
                    mode="inline"
                    style={{
                      width: 256,
                    }}
                    onClick={this.handleClick}
                    defaultSelectedKeys={[this.state.currentSubMenuKey, this.state.currentMenuKey]}
                    defaultOpenKeys={[this.state.currentSubMenuKey, this.state.currentMenuKey]}
                    openKeys={this.state.openKeys}
                    onOpenChange={this.onOpenChange}
                    title={"test"}
                  >
                    {this.state.menus.map((menuItem) => {
                      return (
                        <SubMenu key={menuItem.content_group} title={menuItem.content_group}>
                          {menuItem.content_name.map((subMenuItem) =>
                            subMenuItem.content_name.length > 0 ? (
                              <Menu.Item key={subMenuItem.content_name + "," + subMenuItem.id}>{subMenuItem.content_name}</Menu.Item>
                            ) : (
                              <Menu.Item key={subMenuItem.content_name + "," + subMenuItem.id}></Menu.Item>
                            )
                          )}
                        </SubMenu>
                      );
                    })}
                  </Menu>
                </Col>
              </Card>
              <Card
                size="large"
                title={"Select all permissions for module " + this.state.module}
                extra={
                  <Checkbox
                    indeterminate={this.state.uniIndeterminate}
                    disabled={this.state.disabled}
                    key={this.state.content_id}
                    checked={this.state.uniChecked}
                    onChange={this.uniCheck}
                  />
                }
                style={{
                  minWidth: 600,
                  minHeight: 500,
                  borderLeft: "none",
                }}
              >
                <Form.Item style={{ fontWeight: "bold" }}>
                  <Checkbox
                    indeterminate={this.state.indeterminate}
                    disabled={this.state.disabled}
                    key={this.state.content_id}
                    // value={this.state.content_id}
                    checked={this.state.subModuleAllChecked}
                    onChange={this.subModuleAllCheck}
                  >
                    {this.state.currentSubMenuKey}
                  </Checkbox>
                </Form.Item>

                <Divider />
                {this.state.filtered_perms.map((perm) => (
                  <div style={{ marginTop: 10 }} key={perm.value}>
                    <Checkbox
                      key={perm.value}
                      value={perm.value}
                      disabled={this.state.disabled}
                      checked={this.state.checkedList.includes(perm.value)}
                      onChange={this.onChange}
                    >
                      {perm.label}
                    </Checkbox>
                  </div>
                ))}
                {/* <Checkbox.Group options={this.state.filtered_perms} disabled={this.state.disabled} value={this.state.checkedList} onChange={this.onChange} /> */}
              </Card>
              <Col span={4}></Col>
            </Row>
            <Form.Item style={{ float: "right", marginBottom: 0 }}></Form.Item>
          </Form>
        </div>
        <div style={{ float: "right", marginRight: 50, marginTop: 20 }}>
          <Button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              window.parent.postMessage(
                JSON.stringify({
                  action: "close",
                })
              );
            }}
          >
            Close
          </Button>
          {this.state.disabled == false ? (
            <Button type="primary" style={{ marginLeft: 10 }} onClick={this.saveRole}>
              Save
            </Button>
          ) : (
            <Button
              type="primary"
              style={{ marginLeft: 10 }}
              onClick={(e) => {
                this.setState({
                  disabled: !this.state.disabled,
                });
              }}
            >
              Edit
            </Button>
          )}
        </div>
      </>
    );
  }
}

Role.getInitialProps = async (context) => {
  return {
    isModal: true,
    role_name: context.query.role_name,
    role_id: context.query.role_id,
    isEdit: context.query.role_id ? true : false,
  };
};
export default Role;
