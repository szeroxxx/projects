import Appbar from "./Appbar";
import Footer from "./Footer";
import './Layout.css';

function Layout({children}) {
  return (
   <div className="">
        <Appbar></Appbar>
        <div className="app-container">
          {children}
        </div>
        <Footer></Footer>
   </div>
  );
}

export default Layout;