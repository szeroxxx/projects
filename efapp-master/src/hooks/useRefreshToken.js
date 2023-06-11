import axios from '../api/axios';
import useAuth from './useAuth';

const useRefreshToken = () => {
    const { setAuth } = useAuth();
    const rt = JSON.parse(localStorage.getItem("refresh_token"));
    const refresh = async () => {
        var config = {
            method: 'post',
            url: '/auth/refresh',
            headers: { 
              'Authorization': `Bearer ${rt}`
            }
          };
        const response = await axios(config);
        setAuth(prev => {
            return { ...prev, access_token: response.data.access_token }
        });
        return response.data.access_token;
    }
    return refresh;
};

export default useRefreshToken;
