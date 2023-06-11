const withPlugins = require("next-compose-plugins");
const withTM = require("next-transpile-modules")([
  "@babel/preset-react",
  "@fullcalendar/common",
  "@fullcalendar/daygrid",
  "@fullcalendar/interaction",
  "@fullcalendar/react",
  "@fullcalendar/timegrid",
]);
const nextConfig = {
  reactStrictMode: true,
  trailingSlash: true,
  backendEndPoint: "http://192.168.1.205:8004",
  async rewrites() {
    debugger;
    return [
      {
        source: "/dt/:path*",
        destination: `http://192.168.1.205:8004/dt/:path*/`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/dt/:path*",
        headers: [
          {
            key: "Authorization",
            value: "Basic SW50ZWxsaWFsQGFkbWluLmNvbTppc3BsMTIzOw==",
          },
        ],
      },
    ];
  },
};

module.exports = withPlugins([[withTM]], nextConfig);
