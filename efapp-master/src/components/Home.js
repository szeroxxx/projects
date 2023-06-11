import { Link } from "react-router-dom";
import Layout from "./Layout/Layout"
import useLogout from "./../hooks/useLogout";

const Home = () => {
    const [setLogout] = useLogout();

    return (
        <><Layout>
            
            <h1>Home</h1>
            <br />
            <p>You are logged in!</p>
            <br />
            <Link to="/admin">Go to the Admin page</Link>
            <br />
            <br />
            <div className="flexGrow">
                <button onClick={setLogout}>Sign Out</button>
            </div>
        
        </Layout>
        </>
    )
}

export default Home
