import { Outlet } from "react-router-dom";
import { useState, useEffect } from "react";
import useRefreshToken from '../hooks/useRefreshToken';
import useAuth from '../hooks/useAuth';
import { Spinner } from 'react-bootstrap';

const PersistLogin = () => {
    const [isLoading, setIsLoading] = useState(true);
    const refresh = useRefreshToken();
    const { auth, persist } = useAuth();

    useEffect(() => {
        let isMounted = true;

        const verifyRefreshToken = async () => {
            try {
                await refresh();
            }
            catch (err) {
                console.error(err);
            }
            finally {
                isMounted && setIsLoading(false);
            }
        }

        const rt = JSON.parse(localStorage.getItem("refresh_token"));
        if(rt){
            !auth?.access_token && persist ? verifyRefreshToken() : setIsLoading(false);
        }
        else{
            setIsLoading(false);
        }

        return () => isMounted = false;
    }, [])


    return (
        <>
            {!persist
                ? <Outlet />
                : isLoading
                    ? <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><Spinner animation="border" /></div>
                    : <Outlet />
            }
        </>
    )
}

export default PersistLogin