import { Space, Typography } from "antd";
const { Title } = Typography;
const PageTitle = ({ pageTitle }) => {
  return (
    <Space direction="vertical" size="large">
      <Title level={5}>{pageTitle}</Title>
    </Space>
  );
};

export default PageTitle;
