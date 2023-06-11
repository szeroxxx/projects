import { useNavigate } from "react-router-dom";
import { useContext } from "react";
import AuthContext from "../context/AuthProvider";

export default function useLogout() {
    const { setAuth } = useContext(AuthContext);
    const navigate = useNavigate();

    function setLogout()  {
        setAuth({});
        localStorage.clear();
        navigate('/login');    
    }
    return [setLogout]
}

