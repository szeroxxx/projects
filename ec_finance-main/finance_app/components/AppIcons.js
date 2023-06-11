import {
  AreaChartOutlined,
  BankOutlined,
  BellOutlined,
  CalendarOutlined,
  CarryOutOutlined,
  CheckCircleOutlined,
  CheckOutlined,
  ClockCircleOutlined,
  CopyOutlined,
  CopyrightOutlined,
  DeleteOutlined,
  DollarOutlined,
  DownloadOutlined,
  DribbbleSquareOutlined,
  EditOutlined,
  EuroCircleOutlined,
  EuroOutlined,
  ExceptionOutlined,
  ExclamationCircleOutlined,
  ExportOutlined,
  FieldTimeOutlined,
  FileAddOutlined,
  FileDoneOutlined,
  FileExclamationOutlined,
  FileSearchOutlined,
  FileTextOutlined,
  FileUnknownOutlined,
  GroupOutlined,
  HistoryOutlined,
  MailOutlined,
  MessageOutlined,
  MinusCircleOutlined,
  PhoneOutlined,
  ProfileOutlined,
  PrinterOutlined,
  FilePdfOutlined,
  ReadOutlined,
  ReconciliationOutlined,
  ReloadOutlined,
  RetweetOutlined,
  ScheduleOutlined,
  SettingOutlined,
  ShopOutlined,
  SolutionOutlined,
  SoundOutlined,
  SwitcherOutlined,
  UploadOutlined,
  UserAddOutlined,
  UsergroupAddOutlined,
  UserOutlined,
  UserSwitchOutlined,
  CloudServerOutlined,
  CloudSyncOutlined,
  CloudUploadOutlined,
  RedoOutlined
} from "@ant-design/icons";
import React from "react";
function getIcon(code) {
  if (code == "ExceptionOutlined") return <ExceptionOutlined />;
  else if (code == "SettingOutlined") return <SettingOutlined />;
  else if (code == "CheckOutlined") return <CheckOutlined />;
  else if (code == "EuroCircleOutlined") return <EuroCircleOutlined />;
  else if (code == "EuroOutlined") return <EuroOutlined />;
  else if (code == "UsergroupAddOutlined") return <UsergroupAddOutlined />;
  else if (code == "BankTwoTone") return <BankOutlined />;
  else if (code == "GroupOutlined") return <GroupOutlined />;
  else if (code == "PhoneOutlined") return <PhoneOutlined />;
  else if (code == "MailOutlined") return <MailOutlined />;
  else if (code == "SoundOutlined") return <SoundOutlined />;
  else if (code == "ReconciliationOutlined") return <ReconciliationOutlined />;
  else if (code == "BellOutlined") return <BellOutlined />;
  else if (code == "FileExclamationOutlined") return <FileExclamationOutlined />;
  else if (code == "FileUnknownOutlined") return <FileUnknownOutlined />;
  else if (code == "FileSearchOutlined") return <FileSearchOutlined />;
  else if (code == "SwitcherOutlined") return <SwitcherOutlined />;
  else if (code == "FileAddOutlined") return <FileAddOutlined />;
  else if (code == "FileDoneOutlined") return <FileDoneOutlined />;
  else if (code == "ExclamationCircleOutlined") return <ExclamationCircleOutlined />;
  else if (code == "ClockCircleOutlined") return <ClockCircleOutlined />;
  else if (code == "DollarOutlined") return <DollarOutlined />;
  else if (code == "CheckCircleOutlined") return <CheckCircleOutlined />;
  else if (code == "EditOutlined") return <EditOutlined />;
  else if (code == "CopyrightOutlined") return <CopyrightOutlined />;
  else if (code == "ReadOutlined") return <ReadOutlined />;
  else if (code == "HistoryOutlined") return <HistoryOutlined />;
  else if (code == "DownloadOutlined") return <DownloadOutlined />;
  else if (code == "RetweetOutlined") return <RetweetOutlined />;
  else if (code == "UserOutlined") return <UserOutlined />;
  else if (code == "UserSwitchOutlined") return <UserSwitchOutlined />;
  else if (code == "ReloadOutlined") return <ReloadOutlined />;
  else if (code == "MinusCircleOutlined") return <MinusCircleOutlined />;
  else if (code == "FieldTimeOutlined") return <FieldTimeOutlined />;
  else if (code == "FileTextOutlined") return <FileTextOutlined />;
  else if (code == "UploadOutlined") return <UploadOutlined />;
  else if (code == "ProfileOutlined") return <ProfileOutlined />;
  else if (code == "ExportOutlined") return <ExportOutlined />;
  else if (code == "DeleteOutlined") return <DeleteOutlined />;
  else if (code == "UserAddOutlined") return <UserAddOutlined />;
  else if (code == "ShopOutlined") return <ShopOutlined />;
  else if (code == "DribbbleSquareOutlined") return <DribbbleSquareOutlined />;
  else if (code == "SolutionOutlined") return <SolutionOutlined />;
  else if (code == "ScheduleOutlined") return <ScheduleOutlined />;
  else if (code == "AreaChartOutlined") return <AreaChartOutlined />;
  else if (code == "CalendarOutlined") return <CalendarOutlined />;
  else if (code == "CarryOutOutlined") return <CarryOutOutlined />;
  else if (code == "CopyOutlined") return <CopyOutlined />;
  else if (code == "MessageOutlined") return <MessageOutlined />;
  else if (code == "PrinterOutlined") return <PrinterOutlined />;
  else if (code == "FilePdfOutlined") return <FilePdfOutlined />;
  else if (code == "CloudServerOutlined") return <CloudServerOutlined />;
  else if (code == "CloudSyncOutlined") return <CloudSyncOutlined />;
  else if (code == "CloudUploadOutlined") return <CloudUploadOutlined />;
  else if (code == "RedoOutlined") return <RedoOutlined  />;
  else return <></>;
}
const AppIcons = ({ code }) => {
  return getIcon(code);
};
export default AppIcons;
