import "@fullcalendar/common/main.css";
import "@fullcalendar/daygrid/main.css";
import "@fullcalendar/timegrid/main.css";
import { getSession, SessionProvider } from "next-auth/react";
import App from "next/app";
import { useState } from "react";
import Constant from "../common/Constant";
import AppLayout from "../components/AppLayout";
import "../styles/app.css";
import Splash from "./splash";
let appCompLoaded = false;
function loadDependencies(theme) {
  // setAppCSS reloads the app component and to avoid infinite call of loadDependencies, function is terminated if app Component is initialized already.
  if (appCompLoaded) {
    return null;
  }

  return new Promise(function (resolve, reject) {
    let importPromise = null;
    if (theme == "black") {
      importPromise = import("../styles/theme/theme_black.css");
    } else if (theme == "dark_orange") {
      importPromise = import("../styles/theme/theme_dark_orange.css");
    } else if (theme == "persian_green") {
      importPromise = import("../styles/theme/theme_persian_green.css");
    } else if (theme == "pink") {
      importPromise = import("../styles/theme/theme_pink.css");
    } else if (theme == "radical_red") {
      importPromise = import("../styles/theme/theme_radical_red.css");
    } else if (theme == "royal_blue") {
      importPromise = import("../styles/theme/theme_royal_blue.css");
    } else if (theme == "violet") {
      importPromise = import("../styles/theme/theme_violet.css");
    } else {
      importPromise = import("antd/dist/antd.css");
    }

    importPromise.then((r) => resolve());
  });
}

function FinanceApp({ Component, pageProps: { ...pageProps }, session, router }) {
  const [appCSS, setAppCSS] = useState({ loaded: false });

  let appTheme = session ? session.user.data.theme : null;
  const appInitPromise = loadDependencies(appTheme);
  if (!appCompLoaded) {
    appInitPromise.then(function () {
      setAppCSS((previousState) => {
        appCompLoaded = true;
        return { ...previousState, loaded: true };
      });
    });
  }

  if (!appCSS.loaded) {
    return <Splash>Loading</Splash>;
  }

  if (session) {
    Constant.LIST_PAGE_SIZE = session.user.data.display_row;
  }

  return (
    <SessionProvider session={session}>
      {pageProps.is_open && <Component {...pageProps} session={session}></Component>}
      {!pageProps.isModal && !pageProps.is_open && (
        <AppLayout>
          <Component {...pageProps} session={session}></Component>
        </AppLayout>
      )}
      {pageProps.isModal && !pageProps.is_open && <Component {...pageProps} session={session}></Component>}
    </SessionProvider>
  );
}

FinanceApp.getInitialProps = async (context) => {
  const appProps = await App.getInitialProps(context);

  // Pass the session object before App component rendered.
  // As the CSS needs to be loaded theme wise dynamically based on user preference before the App components loaded.
  const session = await getSession(context);
  return {
    ...appProps,
    session,
  };
};

export default FinanceApp;
